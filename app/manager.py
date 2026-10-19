"""Local-only control panel. No browser/AI status is fabricated."""
import argparse
import collections
import hashlib
import hmac
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml
from codex_bridge import read_account
from content import InvalidPost
from repository import Repository
from store import Store

BASE = Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
TASK_NAME = 'N100BlogPublisherManager'


def atomic_json(path, value):
    temp = Path(str(path)+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
    temp.replace(path)


def clean_error(error):
    text = str(error)
    text = re.sub(r'(?i)(bearer\s+|token[=: ]+)[\w.\-/+]{12,}',r'\1[숨김]',text)
    text = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]+)\b','[숨김]',text)
    return text[:1000]


class Manager:
    def __init__(self, state_dir, config_path=None):
        self.state_dir = Path(state_dir).resolve()
        self.state_dir.mkdir(parents=True,exist_ok=True)
        self.config_path = Path(config_path or self.state_dir/'config.json')
        if not self.config_path.exists():
            shutil.copyfile(BASE/'config.json',self.config_path)
        self.config = json.loads(self.config_path.read_text('utf-8-sig'))
        self.config.setdefault('codex',{'normal_model':'gpt-6-luna','normal_effort':'low','complex_model':'gpt-6.1-sol','complex_effort':'medium','auto_escalate':False,'enabled':True,'daily_limit':10,'low_quota_threshold':10})
        self.config.setdefault('remote_mcp_url','')
        self.config.setdefault('codex_path',shutil.which('codex') or '')
        self.config.setdefault('browser_path','')
        for writer in self.config.get('writers',{}).values():
            writer.setdefault('enabled',True)
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.wake_scan = threading.Event()
        self.wake_usage = threading.Event()
        self.control = {'mode':'paused','started_at':time.time(),'busy':False,'scan_busy':False,'last_scan':None,'last_error':None}
        self.models = []
        self.usage = {'buckets':[],'checked_at':None,'error':'초기 조회 중'}
        self.connections = {
            'github':{'state':'checking','message':'저장소 확인 중'},
            'naver':{'state':'setup','message':'전용 네이버 로그인 및 발행 검증 필요'},
            'mcp':{'state':'setup','message':'원격 HTTPS MCP 서버 연결 필요'},
            'codex':{'state':'checking','message':'실제 계정 조회 중'}}
        self.db_path = self.state_dir/'publisher.sqlite'
        with self.store() as store:
            store.db.executescript('''
            CREATE TABLE IF NOT EXISTS documents(path TEXT PRIMARY KEY,data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS diagnostics(id INTEGER PRIMARY KEY AUTOINCREMENT,at REAL,model TEXT,effort TEXT,status TEXT,summary TEXT,tokens TEXT);
            ''')
            store.db.commit()
            store.recover()
            stored = store.get('usage_cache')
            if stored:
                self.usage = stored
                self.usage['error']='캐시된 값 · 새 조회 중'
            self.models = store.get('models_cache',[])
            self.control['mode']=self.config.get('desired_mode','running')
            store.set('manager_started_at',time.time())
        self.token = secrets.token_urlsafe(32)
        atomic_json(self.state_dir/'control.json',{'port':self.config.get('dashboard_port',8765),'token':self.token,'pid':os.getpid()})
        handler = RotatingFileHandler(self.state_dir/'manager.log',maxBytes=2_000_000,backupCount=3,encoding='utf8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.log = logging.getLogger('publisher.manager')
        self.log.setLevel(logging.INFO)
        self.log.addHandler(handler)

    class _StoreContext:
        def __init__(self,path): self.path=path
        def __enter__(self): self.store=Store(self.path);return self.store
        def __exit__(self,*args): self.store.db.close()

    def store(self): return self._StoreContext(self.db_path)

    def record(self,event,detail='',post_id='system'):
        with self.lock,self.store() as store:
            store.event(post_id,event,clean_error(detail))
            store.db.commit()
        self.log.info('%s %s',event,clean_error(detail))

    def save_config(self):
        atomic_json(self.config_path,self.config)

    def start(self):
        for target in (self.scan_loop,self.usage_loop,self.worker_loop):
            threading.Thread(target=target,daemon=True).start()
        self.record('manager_started','관리 화면과 감지 프로세스 시작. 발행 활성화는 별도 검증 필요')

    def usage_loop(self):
        while not self.stop_event.is_set():
            try:
                usage,models = read_account(self.config.get('codex_path') or None)
                with self.lock,self.store() as store:
                    self.usage,self.models = usage,models
                    self.connections['codex']={'state':'ok','message':'계정 사용량·모델 조회 정상'}
                    store.set('usage_cache',usage)
                    store.set('models_cache',models)
                self.record('usage_refreshed','Codex 사용량과 모델 목록 갱신')
            except Exception as exc:
                error=clean_error(exc)
                with self.lock:
                    self.usage['error']=error
                    self.connections['codex']={'state':'error','message':error}
                self.record('usage_error',error)
            self.wake_usage.wait(300)
            self.wake_usage.clear()

    def scan_loop(self):
        while not self.stop_event.is_set():
            if self.control['mode']=='running' or self.wake_scan.is_set():
                try: self.scan()
                except Exception as exc:
                    error=clean_error(exc)
                    with self.lock:
                        self.connections['github']={'state':'error','message':error}
                        self.control['last_error']=error
                    self.record('scan_error',error)
            self.wake_scan.clear()
            self.wake_scan.wait(max(120,self.config.get('poll_seconds',120)))

    def scan(self):
        with self.lock:
            if self.control['scan_busy']:return
            self.control['scan_busy']=True
            config=json.loads(json.dumps(self.config))
        try:
            repo=Repository(config,self.state_dir)
            commit=repo.head()
            cache=repo.cache/f'{commit}.json'
            with self.store() as store:
                unchanged=store.get('last_commit')==commit and store.get('last_config_fingerprint')==hashlib.sha256(json.dumps(config.get('writers'),sort_keys=True).encode()).hexdigest()
            if unchanged and cache.exists():
                with self.lock:
                    self.connections['github']={'state':'ok','message':'변경 없음 · '+commit[:7]}
                    self.control['last_scan']=time.time()
                return
            posts,errors=repo.scan(commit)
            records=json.loads(cache.read_text('utf8'))
            valid={p.path:p for p in posts}
            error_map={e['path']:e['error'] for e in errors}
            docs=[]
            for item in records:
                path,source=item['path'],item['source']
                m={}
                try:
                    if source.startswith('---'):
                        m=yaml.safe_load(source.split('---',2)[1]) or {}
                except Exception: pass
                if not isinstance(m,dict):m={}
                writer=m.get('muse_account','')
                wc=config.get('writers',{}).get(writer)
                problems=[]
                if path in error_map:problems.append(error_map[path])
                if not wc:problems.append('담당 뮤즈가 등록되지 않았습니다.')
                else:
                    if not path.startswith(wc['content_prefix']):problems.append('뮤즈별 허용 폴더와 다릅니다.')
                    if m.get('category')!=wc['category_name']:problems.append('뮤즈 담당 카테고리와 다릅니다.')
                    if not wc.get('enabled',True):problems.append('담당 뮤즈가 비활성화 상태입니다.')
                known_url=''
                if writer=='muse-01' and m.get('post_id')=='2026-10-18-001':
                    known_url='https://blog.naver.com/3700708/224445449844'
                    problems.insert(0,'이미 발행된 글입니다. 신규 발행 제외 · 기존 글 이력 연결 필요')
                key=f'{writer}:{m.get("post_id",path)}'
                with self.store() as store: existing=store.row(key)
                status='duplicate' if known_url else existing['status'] if existing else 'blocked' if problems else 'pending' if m.get('status')=='ready' else 'draft'
                directory=str(PurePosixPath(path).parent)
                doc={'path':path,'id':key,'post_id':m.get('post_id',''),'writer':writer,'title':m.get('title') or PurePosixPath(path).parent.name,
                    'category':m.get('category',''),'revision':m.get('revision'),'source_status':m.get('status',''),'status':status,
                    'message':' / '.join(problems),'url':known_url or (existing or {}).get('url',''),'source_commit':commit,
                    'github_url':f'https://github.com/{config["repository"]}/blob/{commit}/{urllib.parse.quote(path,safe="/")}',
                    'image_count':len(re.findall(r'!\[[^\]]*\]\(',source)),'checked_at':time.time()}
                docs.append(doc)
                if path in valid and not problems:
                    post=valid[path]
                    # Stable compound identity across writers. Retain original ID separately.
                    post.meta={**post.meta,'source_post_id':post.meta['post_id'],'post_id':key}
                    with self.store() as store:
                        store.ingest(post,commit)
            with self.lock,self.store() as store:
                # Replace inventory as one transaction. History and results stay untouched.
                store.db.execute('DELETE FROM documents')
                store.db.executemany('INSERT INTO documents VALUES(?,?)',[(d['path'],json.dumps(d,ensure_ascii=False)) for d in docs])
                store.db.commit()
                store.set('last_commit',commit)
                store.set('last_config_fingerprint',hashlib.sha256(json.dumps(config.get('writers'),sort_keys=True).encode()).hexdigest())
                self.connections['github']={'state':'ok','message':f'원고 {len(docs)}건 확인 · {commit[:7]}'}
                self.control['last_scan']=time.time()
                self.control['last_error']=None
            self.record('repository_synced',f'원고 {len(docs)}건 · 점검 필요 {sum(bool(d["message"]) for d in docs)}건 · {commit[:7]}')
        finally:
            with self.lock:self.control['scan_busy']=False

    def worker_loop(self):
        while not self.stop_event.wait(3):
            # A configured adapter is never equated to a verified publisher.
            if self.control['mode']!='running' or not self.config.get('enabled'):
                continue
            if not self.config.get('publisher_verified'):
                continue
            self.record('publish_gate','발행 어댑터 통합 검증이 필요합니다.')
            with self.lock:
                self.config['enabled']=False
                self.save_config()

    def snapshot(self):
        with self.lock,self.store() as store:
            state=store.snapshot()
            docs=[json.loads(r[0]) for r in store.db.execute('SELECT data FROM documents ORDER BY path DESC')]
            jobs={p['id']:p for p in state['posts']}
            for d in docs:
                if d['id'] in jobs and d['status']!='duplicate':
                    job=jobs[d['id']]
                    d.update(status=job['status'],url=job['url'],message=job['message'] or d['message'])
            diagnostics=[dict(r) for r in store.db.execute('SELECT * FROM diagnostics ORDER BY id DESC LIMIT 30')]
            counts=collections.Counter(d['status'] for d in docs)
            config=json.loads(json.dumps(self.config))
            config.pop('github_token',None)
            config.pop('mcp_token',None)
            return {'control':dict(self.control),'config':config,'connections':json.loads(json.dumps(self.connections)),
                'usage':self.usage,'models':self.models,'documents':docs,'counts':dict(counts),'events':state['events'],
                'diagnostics':diagnostics,'local_time':time.time(),'state_dir':str(self.state_dir),
                'autostart':store.get('autostart',{'mode':'none','message':'자동 시작 확인 중'}),
                'capabilities':{'monitor':True,'usage':True,'models':True,'publish':bool(config.get('publisher_verified')),'mcp_connected':self.connections['mcp']['state']=='ok'}}

    def command(self,action,body):
        if action=='start':
            with self.lock:
                self.control['mode']='running'
                self.config['desired_mode']='running'
                self.save_config()
            self.wake_scan.set()
            self.record('monitor_started','GitHub 감지 시작')
            return {'message':'GitHub 감지를 시작했습니다. 검증되지 않은 발행 작업은 보류됩니다.'}
        if action in ('pause','stop'):
            with self.lock:
                self.control['mode']='paused' if action=='pause' else 'stopped'
                self.config['desired_mode']=self.control['mode']
                self.save_config()
            self.record('monitor_'+action,'진행 중인 제출이 있다면 결과 확인 후 중단')
            return {'message':'일시정지했습니다.' if action=='pause' else '감지와 신규 작업 실행을 정지했습니다. 관리 화면은 유지됩니다.'}
        if action=='scan':
            self.wake_scan.set()
            return {'message':'GitHub 원고 확인을 요청했습니다.'}
        if action=='usage':
            self.wake_usage.set()
            return {'message':'사용량과 모델 목록 갱신을 요청했습니다.'}
        if action=='retry':
            key=body.get('id','')
            with self.lock,self.store() as store:
                row=store.row(key)
                if not row or row['status'] not in ('retry','blocked'):
                    raise ValueError('안전하게 재시도할 수 있는 작업만 선택하세요. 결과 불확정·중복 작업은 재발행하지 않습니다.')
                store.transition(key,'pending','사용자가 안전한 재검사를 요청함')
            self.wake_scan.set()
            return {'message':'재검사 대기열에 넣었습니다.'}
        if action=='settings':return self.update_settings(body)
        if action=='writer':return self.update_writer(body)
        if action=='login':return self.open_naver_login()
        if action=='naver_check':
            threading.Thread(target=self.check_naver,daemon=True).start()
            return {'message':'저장된 전용 세션으로 네이버 접근을 확인합니다.'}
        if action=='mcp_check':
            threading.Thread(target=self.check_mcp,daemon=True).start()
            return {'message':'원격 MCP 연결을 확인합니다.'}
        if action=='autostart_check':
            threading.Thread(target=self.check_autostart,daemon=True).start()
            return {'message':'Windows 자동 시작 설정을 조회합니다.'}
        if action=='install_boot':
            script=BASE/'setup-autostart.ps1'
            flags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess,'CREATE_NO_WINDOW') else 0
            command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-StateDir',str(self.state_dir),'-Python',sys.executable,'-Manager',str(BASE/'manager.py')]
            if getattr(sys,'frozen',False):command.append('-Frozen')
            subprocess.Popen(command,creationflags=flags)
            self.record('boot_setup_requested','Windows 관리자 승인과 현재 사용자 암호 입력이 필요한 설치 화면 요청')
            return {'message':'Windows 설정 창을 열었습니다. 부팅 실행에는 관리자 승인과 Windows 계정 암호 입력이 필요합니다. PIN은 사용할 수 없습니다.'}
        if action=='diagnose':
            with self.lock:
                if self.control.get('ai_busy'):raise ValueError('이미 AI 진단 중입니다.')
                self.control['ai_busy']=True
                try:threading.Thread(target=self.diagnose,args=(body.get('id'),body.get('level','normal')),daemon=True).start()
                except Exception:
                    self.control['ai_busy']=False
                    raise
            return {'message':'선택한 모델로 진단을 시작합니다. 원고나 코드는 자동 변경하지 않습니다.'}
        raise ValueError('지원하지 않는 명령')

    def update_settings(self,body):
        with self.lock:
            if 'codex' in body:
                ai=body['codex']
                catalog={m['id']:m for m in self.models}
                for prefix in ('normal','complex'):
                    model,effort=ai.get(prefix+'_model'),ai.get(prefix+'_effort')
                    if model not in catalog:raise ValueError('조회된 모델 중에서 선택하세요.')
                    if effort not in catalog[model]['efforts']:raise ValueError('해당 모델에서 지원하지 않는 추론 강도입니다.')
                ai['daily_limit']=max(1,min(100,int(ai.get('daily_limit',10))))
                ai['low_quota_threshold']=max(0,min(50,int(ai.get('low_quota_threshold',10))))
                for field in ('enabled','auto_escalate'):ai[field]=bool(ai.get(field,False))
                self.config['codex']=ai
            if 'connections' in body:
                incoming=body['connections']
                repository=incoming.get('repository',self.config['repository']).strip()
                if not re.fullmatch(r'[\w.-]+/[\w.-]+',repository):raise ValueError('저장소는 owner/name 형식으로 입력하세요.')
                self.config['repository']=repository
                branch=incoming.get('branch',self.config['branch']).strip()
                if not branch or len(branch)>200:raise ValueError('브랜치를 확인하세요.')
                self.config['branch']=branch
                url=incoming.get('remote_mcp_url','').strip()
                if url:
                    u=urllib.parse.urlparse(url)
                    if u.scheme!='https' or not u.hostname or u.username or u.password:raise ValueError('원격 MCP는 인증값을 포함하지 않은 HTTPS 주소로 입력하세요.')
                self.config['remote_mcp_url']=url
                executable=incoming.get('codex_path',self.config.get('codex_path','')).strip()
                if executable and not Path(executable).is_file():raise ValueError('Codex 실행 파일이 없습니다.')
                self.config['codex_path']=executable
            self.save_config()
        self.record('settings_saved','운영/AI 설정 저장')
        self.wake_usage.set()
        self.wake_scan.set()
        return {'message':'설정을 저장했습니다. 다음 진단부터 선택 모델을 적용합니다.'}

    def update_writer(self,body):
        key=body.get('id','').strip()
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,50}',key):raise ValueError('뮤즈 별명은 영문·숫자·하이픈·밑줄로 지정하세요.')
        name=body.get('name','').strip()
        category=body.get('category_name','').strip()
        number=int(body.get('category_id',0))
        if not name or not category or number<=0:raise ValueError('뮤즈 이름과 카테고리 이름·번호를 입력하세요.')
        with self.lock:
            existing=self.config['writers'].get(key)
            if existing and (existing['category_id']!=number or existing['category_name']!=category):
                if not body.get('confirm_category_change'):raise ValueError('기존 카테고리 변경은 확인 항목을 선택해야 합니다. 이미 발행된 글은 자동 이동하지 않습니다.')
            self.config['writers'][key]={'name':name,'content_prefix':f'posts/{key}/','blog_id':self.config['blog_id'],
                'category_id':number,'category_name':category,'enabled':bool(body.get('enabled',True))}
            self.save_config()
        self.record('writer_saved',key+' 담당 설정 저장')
        self.wake_scan.set()
        return {'message':'뮤즈 담당 설정을 저장했습니다.'}

    def open_naver_login(self):
        current=getattr(self,'login_process',None)
        if current and current.poll() is None:
            return {'message':'전용 로그인 창 실행 중입니다. 열린 네이버 창을 확인하세요.'}
        flags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess,'CREATE_NO_WINDOW') else 0
        env=os.environ.copy()
        if self.config.get('browser_path'):env['PLAYWRIGHT_BROWSERS_PATH']=self.config['browser_path']
        command=[sys.executable,'--login','--state-dir',str(self.state_dir),'--blog-id',self.config['blog_id']] if getattr(sys,'frozen',False) else [sys.executable,str(BASE/'auth.py'),'--state-dir',str(self.state_dir),'--blog-id',self.config['blog_id']]
        atomic_json(self.state_dir/'login-status.json',{'state':'starting','message':'전용 로그인 브라우저 시작 중','at':time.time()})
        self.login_process=subprocess.Popen(command,env=env,creationflags=flags)
        def watch():
            self.login_process.wait()
            try:
                result=json.loads((self.state_dir/'login-status.json').read_text('utf8'))
                if result.get('state')=='saved':self.check_naver()
                else:
                    message=result.get('message','로그인 프로세스가 종료되었습니다.')
                    self.connections['naver']={'state':'error','message':message}
                    self.record('naver_error',message)
            except Exception as exc:self.record('naver_error',clean_error(exc))
        threading.Thread(target=watch,daemon=True).start()
        self.record('login_opened','전용 브라우저 수동 로그인 시작 · 일반 Chrome 세션을 읽지 않음')
        return {'message':'전용 로그인 브라우저 실행을 요청했습니다. 로그인 후 글쓰기 화면이 표시되면 연결을 확인합니다.'}

    def check_naver(self):
        state=self.state_dir/'naver-session.dpapi'
        if not state.exists():
            self.connections['naver']={'state':'setup','message':'전용 네이버 로그인이 필요합니다.'};return
        self.connections['naver']={'state':'checking','message':'전용 로그인 세션 확인 중'}
        try:
            from auth import load_state, launch_browser
            from playwright.sync_api import sync_playwright
            if self.config.get('browser_path'):os.environ['PLAYWRIGHT_BROWSERS_PATH']=self.config['browser_path']
            with sync_playwright() as p:
                browser=launch_browser(p,headless=True)
                try:
                    context=browser.new_context(storage_state=load_state(state),locale='ko-KR')
                    page=context.new_page()
                    page.goto(f'https://blog.naver.com/{self.config["blog_id"]}/postwrite',wait_until='domcontentloaded',timeout=40000)
                    end=time.monotonic()+25
                    found=False
                    while time.monotonic()<end:
                        if any(f.locator('.se-documentTitle').count() for f in page.frames):found=True;break
                        if 'nid.naver.com' in page.url:break
                        time.sleep(1)
                    if not found:raise RuntimeError('로그인/추가 인증이 필요하거나 편집기를 확인하지 못했습니다.')
                    self.connections['naver']={'state':'ok','message':'로그인·글쓰기 화면 확인됨 · 발행/이미지 통합검증은 별도'}
                finally:browser.close()
            self.record('naver_checked','전용 세션으로 글쓰기 화면 확인. 글 저장/발행은 수행하지 않음')
        except Exception as exc:
            self.connections['naver']={'state':'error','message':clean_error(exc)}
            self.record('naver_error',clean_error(exc))

    def check_mcp(self):
        url=self.config.get('remote_mcp_url','')
        if not url:
            self.connections['mcp']={'state':'setup','message':'원격 HTTPS MCP 주소를 먼저 설정하세요.'};return
        self.connections['mcp']={'state':'checking','message':'MCP 초기화 요청 중'}
        try:
            import requests
            headers={'Accept':'application/json, text/event-stream','Content-Type':'application/json'}
            secret=self.state_dir/'mcp-token.dpapi'
            if secret.exists():
                from auth import load_state
                headers['Authorization']='Bearer '+load_state(secret)['token']
            response=requests.post(url,headers=headers,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'naver-manager','version':'1.0'}}},timeout=15,allow_redirects=False)
            response.raise_for_status()
            if 'application/json' in response.headers.get('Content-Type',''):
                data=response.json()
            else:
                data=next(json.loads(x[6:]) for x in response.text.splitlines() if x.startswith('data: '))
            if 'error' in data or not data.get('result',{}).get('protocolVersion'):raise RuntimeError('MCP 초기화 응답이 올바르지 않습니다.')
            self.connections['mcp']={'state':'partial','message':'MCP 초기화 성공 · 뮤즈 왕복/권한/작업큐 검증 필요'}
            self.record('mcp_handshake','원격 MCP 초기화만 확인 · 작업 제출 없음')
        except Exception as exc:
            self.connections['mcp']={'state':'error','message':clean_error(exc)}
            self.record('mcp_error',clean_error(exc))

    def check_autostart(self):
        try:
            command=['powershell.exe','-NoProfile','-Command',f"$t=Get-ScheduledTask -TaskName '{TASK_NAME}' -ErrorAction SilentlyContinue; if($t){{[pscustomobject]@{{state=[string]$t.State;user=$t.Principal.UserId;logon=[string]$t.Principal.LogonType;boot=[bool]($t.Triggers | Where-Object {{$_.CimClass.CimClassName -eq 'MSFT_TaskBootTrigger'}})}}|ConvertTo-Json -Compress}} else {{'null'}}"]
            result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=15,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            data=json.loads(result.stdout.strip() or 'null')
            startup=Path(os.environ.get('APPDATA',''))/'Microsoft/Windows/Start Menu/Programs/Startup/N100 Blog Manager.lnk'
            if data and data.get('boot'):
                value={'mode':'boot','message':'부팅 시 자동 실행 등록됨 · 재부팅 실증 필요','detail':data}
            elif startup.exists():
                value={'mode':'logon','message':'Windows 로그인 후 자동 실행 · 로그인 전 부팅 실행은 추가 설정 필요'}
            else:value={'mode':'none','message':'자동 실행 미등록'}
            with self.lock,self.store() as store:store.set('autostart',value)
        except Exception as exc:
            with self.lock,self.store() as store:store.set('autostart',{'mode':'error','message':clean_error(exc)})

    def diagnose(self,doc_id,level):
        with self.lock:
            self.control['ai_busy']=True
        model=effort=''
        try:
            ai=self.config['codex']
            if not ai.get('enabled'):raise RuntimeError('AI 진단이 꺼져 있습니다.')
            # Keep stale/missing quotas from causing unbounded AI usage.
            if self.usage.get('error') or not self.usage.get('checked_at') or time.time()-self.usage['checked_at']>900:
                raise RuntimeError('최근 사용량 조회에 성공한 뒤 AI 진단을 실행하세요.')
            remaining=[w['remaining'] for b in self.usage.get('buckets',[]) for w in b['windows'] if w['remaining'] is not None]
            if not remaining or min(remaining)<ai.get('low_quota_threshold',10):raise RuntimeError('사용량 보호 기준에 따라 AI 진단을 보류합니다.')
            with self.store() as store:
                count=store.db.execute('SELECT count(*) FROM diagnostics WHERE at>=?',(time.time()-86400,)).fetchone()[0]
                if count>=ai.get('daily_limit',10):raise RuntimeError('24시간 AI 진단 횟수 상한에 도달했습니다.')
            snap=self.snapshot()
            doc=next((d for d in snap['documents'] if d['id']==doc_id),None)
            if not doc:raise ValueError('진단할 원고를 선택하세요.')
            from diagnostics import run_diagnostic
            prefix='complex' if level=='complex' else 'normal'
            model,effort=ai[prefix+'_model'],ai[prefix+'_effort']
            with self.store() as store:
                store.db.execute('INSERT INTO diagnostics(at,model,effort,status,summary,tokens) VALUES(?,?,?,?,?,?)',(time.time(),model,effort,'started','진단 중','null'))
                record_id=store.db.execute('SELECT last_insert_rowid()').fetchone()[0];store.db.commit()
            try:
                result,tokens=run_diagnostic(self.config.get('codex_path'),model,effort,{'path':doc['path'],'status':doc['status'],'errors':doc['message'],'category':doc['category'],'revision':doc['revision']},self.state_dir)
                with self.store() as store:
                    store.db.execute('UPDATE diagnostics SET status=?,summary=?,tokens=? WHERE id=?',('completed',json.dumps(result,ensure_ascii=False),json.dumps(tokens),record_id));store.db.commit()
                self.record('ai_diagnostic_completed',f'{model} / {effort}',doc_id)
            except Exception as exc:
                with self.store() as store:
                    store.db.execute('UPDATE diagnostics SET status=?,summary=? WHERE id=?',('failed',clean_error(exc),record_id));store.db.commit()
                raise
        except Exception as exc:self.record('ai_diagnostic_error',clean_error(exc),doc_id or 'system')
        finally:
            self.control['ai_busy']=False
            self.wake_usage.set()


class Handler(BaseHTTPRequestHandler):
    server_version='BlogManager/1.0'
    def log_message(self,*args):pass
    @property
    def manager(self):return self.server.manager
    def valid_host(self):
        return self.headers.get('Host','') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
    def reply(self,status,data,content_type='application/json; charset=utf-8'):
        if isinstance(data,(dict,list)):data=json.dumps(data,ensure_ascii=False).encode()
        elif isinstance(data,str):data=data.encode()
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def authorized(self):return hmac.compare_digest(self.headers.get('X-Manager-Token',''),self.manager.token)
    def do_GET(self):
        if not self.valid_host():self.reply(403,{'error':'허용되지 않은 호스트'});return
        path=urllib.parse.urlparse(self.path).path
        if path=='/health':self.reply(200,{'app':'n100-blog-manager','pid':os.getpid()});return
        if path=='/api/state':
            if not self.authorized():self.reply(403,{'error':'관리 인증 필요'});return
            self.reply(200,self.manager.snapshot());return
        if path in ('/','/index.html'):
            html=(BASE/'web/index.html').read_text('utf8').replace('__MANAGER_TOKEN__',self.manager.token)
            self.reply(200,html,'text/html; charset=utf-8');return
        assets={'/app.js':('web/app.js','text/javascript; charset=utf-8'),'/style.css':('web/style.css','text/css; charset=utf-8'),'/favicon.svg':('web/favicon.svg','image/svg+xml')}
        if path in assets:
            file,kind=assets[path];self.reply(200,(BASE/file).read_bytes(),kind);return
        self.reply(404,{'error':'페이지를 찾을 수 없습니다.'})
    def do_POST(self):
        if not self.valid_host() or not self.authorized():self.reply(403,{'error':'관리 인증 필요'});return
        origin=self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
            self.reply(403,{'error':'다른 웹사이트에서 보낸 제어 요청은 허용하지 않습니다.'});return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=65536:raise ValueError('요청 크기를 확인하세요.')
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict):raise ValueError('잘못된 요청')
            action=self.path.removeprefix('/api/')
            result=self.manager.command(action,body)
            self.reply(200,result)
        except (ValueError,KeyError,TypeError) as exc:self.reply(400,{'error':clean_error(exc)})
        except Exception as exc:
            self.manager.record('control_error',clean_error(exc))
            self.reply(500,{'error':clean_error(exc)})


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--state-dir',default=str(Path(os.environ.get('LOCALAPPDATA',str(Path.cwd()))) / 'NaverBlogManager/data'))
    ap.add_argument('--open',action='store_true')
    ap.add_argument('--background',action='store_true')
    ap.add_argument('--login',action='store_true')
    ap.add_argument('--blog-id',default='3700708')
    args=ap.parse_args()
    if args.login:
        status_file=Path(args.state_dir)/'login-status.json'
        try:
            atomic_json(status_file,{'state':'starting','message':'브라우저 실행 준비 중','at':time.time()})
            from auth import login
            login(args.state_dir,args.blog_id)
            atomic_json(status_file,{'state':'saved','message':'전용 로그인 저장 완료','at':time.time()})
        except Exception as exc:
            atomic_json(status_file,{'state':'error','message':clean_error(exc),'at':time.time()})
        return
    state=Path(args.state_dir).resolve();state.mkdir(parents=True,exist_ok=True)
    lock_file=open(state/'instance.lock','a+b')
    try:
        if os.name=='nt':
            import msvcrt
            lock_file.seek(0);lock_file.write(b'0');lock_file.flush();lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        if args.open or not args.background:webbrowser.open('http://127.0.0.1:8765')
        return
    manager=Manager(state)
    server=ThreadingHTTPServer(('127.0.0.1',manager.config.get('dashboard_port',8765)),Handler)
    server.daemon_threads=True
    server.manager=manager
    manager.start()
    threading.Thread(target=manager.check_autostart,daemon=True).start()
    if args.open or not args.background:webbrowser.open(f'http://127.0.0.1:{server.server_port}')
    try:server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:pass
    finally:
        manager.stop_event.set();server.server_close();lock_file.close()


if __name__=='__main__':main()
