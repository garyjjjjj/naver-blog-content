import json
from pathlib import Path, PurePosixPath
from urllib.parse import quote
import requests
import yaml
from content import parse_post, local_image, InvalidPost


class Repository:
    def __init__(self, config, state_dir):
        self.config = config
        self.cache = Path(state_dir) / 'snapshots'
        self.cache.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({'Accept':'application/vnd.github+json','User-Agent':'N100-Naver-Publisher/1.0','X-GitHub-Api-Version':'2022-11-28'})
        # Optional credentials are explicitly provisioned, never taken from another gh account.
        secret = Path(state_dir) / 'github-token.dpapi'
        if secret.exists():
            from auth import load_state
            self.session.headers['Authorization'] = 'Bearer ' + load_state(secret)['token']

    def api(self, endpoint):
        url = f'https://api.github.com/repos/{self.config["repository"]}/{endpoint}'
        r = self.session.get(url, timeout=30)
        if r.status_code == 403 or r.status_code == 429:
            raise RuntimeError('GitHub 요청 한도 또는 권한 오류. 다음 주기에 재시도합니다.')
        r.raise_for_status()
        return r.json()

    def head(self):
        return self.api('commits/' + quote(self.config['branch'],safe=''))['sha']

    def raw(self, commit, path, limit):
        url = f'https://raw.githubusercontent.com/{self.config["repository"]}/{commit}/{quote(path,safe="/")}'
        r = self.session.get(url, timeout=45, stream=True)
        r.raise_for_status()
        chunks, size = [], 0
        for chunk in r.iter_content(65536):
            size += len(chunk)
            if size > limit:
                r.close()
                raise InvalidPost('파일 크기 제한 초과')
            chunks.append(chunk)
        return b''.join(chunks)

    def scan(self, commit):
        cache_file = self.cache / f'{commit}.json'
        if cache_file.exists():
            records = json.loads(cache_file.read_text('utf8'))
        else:
            tree = self.api(f'git/trees/{commit}?recursive=1')
            if tree.get('truncated'):
                raise RuntimeError('GitHub 파일 목록이 잘렸습니다. 저장소를 분리하세요.')
            records = []
            for item in tree['tree']:
                p = PurePosixPath(item['path'])
                if len(p.parts) == 4 and p.parts[0] == 'posts' and p.name == 'post.md':
                    if item['type'] != 'blob' or item['mode'] != '100644':
                        raise InvalidPost('원고는 일반 파일이어야 합니다.')
                    records.append({'path':str(p),'source':self.raw(commit,str(p),1024*1024).decode('utf-8-sig')})
            cache_file.write_text(json.dumps(records, ensure_ascii=False), 'utf8')
        posts, errors = [], []
        for record in records:
            try:
                source, path = record['source'], record['path']
                # Parse metadata first solely to identify declared local assets.
                meta = yaml.safe_load(source.split('---',2)[1]) if source.startswith('---') else {}
                if not isinstance(meta,dict) or meta.get('status') != 'ready':
                    continue
                assets = {}
                for asset in meta.get('assets', []):
                    name = local_image(asset['path'])
                    asset_path = str(PurePosixPath(path).parent / name)
                    local = self.cache / commit / asset_path
                    if not local.exists():
                        local.parent.mkdir(parents=True, exist_ok=True)
                        local.write_bytes(self.raw(commit,asset_path,20*1024*1024))
                    assets[name] = local.read_bytes()
                post = parse_post(path,source,assets,self.config['blog_id'])
                if post:
                    posts.append(post)
            except Exception as exc:
                errors.append({'path':record['path'],'error':str(exc)})
        ids = [p.meta['post_id'] for p in posts]
        duplicates = {x for x in ids if ids.count(x)>1}
        if duplicates:
            errors.extend({'path':p.path,'error':'글ID 중복'} for p in posts if p.meta['post_id'] in duplicates)
            posts = [p for p in posts if p.meta['post_id'] not in duplicates]
        return posts, errors
