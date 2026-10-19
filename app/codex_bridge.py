"""Read official local Codex App Server APIs; never opens credential files."""
import json
import queue
import shutil
import subprocess
import threading
import time


class CodexError(RuntimeError):
    pass


class CodexRPC:
    def __init__(self, executable=None, timeout=35):
        self.executable = executable or shutil.which('codex')
        if not self.executable:
            raise CodexError('Codex CLI를 찾을 수 없습니다. 연결 설정에서 실행 파일을 지정하세요.')
        self.timeout = timeout
        self.process = None
        self.messages = queue.Queue()
        self.counter = 0

    def __enter__(self):
        flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        self.process = subprocess.Popen([self.executable, 'app-server', '--stdio'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding='utf-8', bufsize=1,
            creationflags=flags)
        def read():
            try:
                for line in self.process.stdout:
                    try:
                        self.messages.put(json.loads(line))
                    except ValueError:
                        pass
            finally:
                self.messages.put({'closed':True})
        threading.Thread(target=read, daemon=True).start()
        try:
            self.request('initialize', {'clientInfo':{'name':'naver_blog_manager','title':'Blog Publisher Manager','version':'1.0.0'},'capabilities':{'experimentalApi':True}})
            self.notify('initialized')
        except Exception:
            self.__exit__()
            raise
        return self

    def send(self, obj):
        if not self.process or self.process.poll() is not None:
            raise CodexError('Codex App Server 연결이 종료되었습니다.')
        self.process.stdin.write(json.dumps(obj,ensure_ascii=False)+'\n')
        self.process.stdin.flush()

    def notify(self, method, params=None):
        self.send({'method':method, **({'params':params} if params is not None else {})})

    def request(self, method, params=None):
        self.counter += 1
        request_id = self.counter
        self.send({'id':request_id,'method':method, **({'params':params} if params is not None else {})})
        deadline = time.monotonic()+self.timeout
        while time.monotonic()<deadline:
            try:
                msg = self.messages.get(timeout=max(.1,deadline-time.monotonic()))
            except queue.Empty:
                break
            if msg.get('closed'):
                raise CodexError('Codex App Server가 응답 전에 종료되었습니다.')
            if msg.get('id') == request_id:
                if 'error' in msg:
                    err = msg['error']
                    raise CodexError(f'{method}: {err.get("message","조회 실패")}')
                return msg.get('result',{})
            # Never approve commands, writes or authentication on behalf of this reader.
            if 'id' in msg and 'method' in msg:
                self.send({'id':msg['id'],'error':{'code':-32601,'message':'Read-only manager client'}})
        raise CodexError('Codex 조회 시간이 초과됐습니다. 마지막 정상 값을 표시합니다.')

    def __exit__(self, *args):
        if self.process:
            try:
                self.process.stdin.close()
                self.process.wait(timeout=3)
            except Exception:
                self.process.kill()
                self.process.wait(timeout=3)


def normalize_limits(result):
    buckets = result.get('rateLimitsByLimitId')
    if not buckets:
        single = result.get('rateLimits') or {}
        buckets = {single.get('limitId') or 'codex':single} if single else {}
    normalized = []
    for bucket_id, bucket in buckets.items():
        windows = []
        for key in ('primary','secondary'):
            value = bucket.get(key)
            if not value:
                continue
            used = value.get('usedPercent')
            minutes = value.get('windowDurationMins')
            remaining = max(0,min(100,100-used)) if isinstance(used,(int,float)) else None
            windows.append({'minutes':minutes,'used':used,'remaining':remaining,'resets_at':value.get('resetsAt'),
                'label':'5시간' if minutes==300 else '주간' if minutes==10080 else f'{minutes}분' if minutes else '기간 미제공'})
        normalized.append({'id':bucket_id,'name':bucket.get('limitName') or bucket_id,'plan':bucket.get('planType'),
            'windows':windows,'reached':bucket.get('rateLimitReachedType')})
    return {'buckets':normalized,'checked_at':time.time(),'error':None}


def read_account(executable=None, include_models=True):
    with CodexRPC(executable) as rpc:
        usage = normalize_limits(rpc.request('account/rateLimits/read'))
        models = []
        if include_models:
            cursor = None
            for _ in range(10):
                result = rpc.request('model/list',{'limit':100,'includeHidden':False, **({'cursor':cursor} if cursor else {})})
                for item in result.get('data',[]):
                    if item.get('hidden'):
                        continue
                    models.append({'id':item.get('model') or item.get('id'),'name':item.get('displayName') or item.get('id'),
                        'description':item.get('description',''),'default_effort':item.get('defaultReasoningEffort'),
                        'efforts':[x.get('reasoningEffort') or x.get('effort') for x in item.get('supportedReasoningEfforts',[])],
                        'is_default':item.get('isDefault',False)})
                cursor = result.get('nextCursor')
                if not cursor:
                    break
        return usage,models


if __name__ == '__main__':
    usage,models = read_account()
    print(json.dumps({'usage':usage,'models':models},ensure_ascii=False,indent=2))
