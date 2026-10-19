import json
import sqlite3
import time


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS posts(
            id TEXT PRIMARY KEY,path TEXT NOT NULL,revision INTEGER NOT NULL,
            fingerprint TEXT NOT NULL,source_commit TEXT NOT NULL,title TEXT NOT NULL,
            status TEXT NOT NULL,seen REAL NOT NULL,retry_at REAL DEFAULT 0,
            attempts INTEGER DEFAULT 0,url TEXT DEFAULT '',message TEXT DEFAULT '',
            updated REAL NOT NULL, published_fingerprint TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS events(
            seq INTEGER PRIMARY KEY AUTOINCREMENT,at REAL,id TEXT,event TEXT,detail TEXT);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS publication_proofs(
            id TEXT NOT NULL,revision INTEGER NOT NULL,fingerprint TEXT NOT NULL,
            source_commit TEXT NOT NULL,url TEXT NOT NULL,evidence TEXT NOT NULL,at REAL NOT NULL,
            PRIMARY KEY(id,revision));
        ''')
        self.db.commit()

    def event(self, post_id, event, detail=''):
        self.db.execute('INSERT INTO events(at,id,event,detail) VALUES(?,?,?,?)', (time.time(), post_id, event, detail))

    def get(self, key, default=None):
        row = self.db.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self, key, value):
        self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', (key, json.dumps(value, ensure_ascii=False)))
        self.db.commit()

    def row(self, post_id):
        row = self.db.execute('SELECT * FROM posts WHERE id=?', (post_id,)).fetchone()
        return dict(row) if row else None

    def ingest(self, post, commit):
        m, now = post.meta, time.time()
        old = self.row(m['post_id'])
        if old:
            if old['path'] != post.path:
                raise ValueError('동일 글ID가 다른 경로에서 사용되었습니다.')
            if old['status'] in ('submitting', 'uncertain'):
                return # Must reconcile previous side effect before accepting new content.
            if old['fingerprint'] == post.fingerprint:
                if m['revision'] < old['revision']:
                    raise ValueError('revision이 이전 값보다 작습니다.')
                if old['status'] == 'cancelled':
                    self.db.execute("UPDATE posts SET status='pending',seen=?,source_commit=?,updated=? WHERE id=?", (now, commit, now, m['post_id']))
                else:
                    self.db.execute('UPDATE posts SET source_commit=?,revision=?,updated=? WHERE id=?', (commit, m['revision'], now, m['post_id']))
                self.db.commit()
                return
            if m['revision'] <= old['revision']:
                raise ValueError('수정본은 revision을 증가시켜야 합니다.')
            self.db.execute("UPDATE posts SET revision=?,fingerprint=?,source_commit=?,title=?,status='pending',seen=?,retry_at=0,attempts=0,message='',updated=? WHERE id=?", (m['revision'], post.fingerprint, commit, m['title'], now, now, m['post_id']))
        else:
            self.db.execute('INSERT INTO posts(id,path,revision,fingerprint,source_commit,title,status,seen,updated) VALUES(?,?,?,?,?,?,?, ?,?)', (m['post_id'], post.path, m['revision'], post.fingerprint, commit, m['title'], 'pending', now, now))
        self.event(m['post_id'], 'queued', f'revision {m["revision"]}')
        self.db.commit()

    def cancel_missing(self, valid_ids):
        rows = self.db.execute("SELECT id FROM posts WHERE status IN ('pending','retry','blocked')").fetchall()
        for row in rows:
            if row['id'] not in valid_ids:
                self.db.execute("UPDATE posts SET status='cancelled',message='ready 원고가 아니거나 검증 오류',updated=? WHERE id=?", (time.time(), row['id']))
        self.db.commit()

    def transition(self, post_id, state, message='', url=None):
        if state == 'published':
            raise ValueError('발행 완료는 게시글 대조 증거를 첨부하여 확정해야 합니다.')
        values = [state, message, time.time(), post_id]
        self.db.execute('UPDATE posts SET status=?,message=?,updated=? WHERE id=?', values)
        if url:
            self.db.execute('UPDATE posts SET url=? WHERE id=?', (url, post_id))
        self.event(post_id, state, message)
        self.db.commit()

    def confirm_publication(self, post, evidence, *, blog_id, category_id):
        from publication_proof import validate_publication, UnconfirmedPublication
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.row(post.meta['post_id'])
            if not row or row['fingerprint'] != post.fingerprint or row['revision'] != post.meta['revision']:
                raise UnconfirmedPublication('현재 대기열의 원고와 다릅니다.')
            if row['status'] not in ('submitting', 'uncertain', 'published'):
                raise UnconfirmedPublication('제출 기록이 없는 글은 발행 완료로 바꿀 수 없습니다.')
            url = validate_publication(post, evidence, blog_id=blog_id, category_id=category_id,
                                       source_commit=row['source_commit'], previous_url=row['url'])
            owner = self.db.execute('SELECT id FROM publication_proofs WHERE url=? AND id<>?', (url,row['id'])).fetchone()
            if owner:
                raise UnconfirmedPublication('다른 글ID가 이미 사용하는 게시글 번호입니다.')
            self.db.execute('INSERT OR REPLACE INTO publication_proofs VALUES(?,?,?,?,?,?,?)',
                (row['id'],row['revision'],row['fingerprint'],row['source_commit'],url,json.dumps(evidence,ensure_ascii=False),time.time()))
            self.db.execute("UPDATE posts SET status='published',url=?,published_fingerprint=fingerprint,message='게시글 대조 완료',updated=? WHERE id=?",
                            (url,time.time(),row['id']))
            self.event(row['id'],'published','게시글 URL·버전·본문·이미지·카테고리 대조 완료')
            self.db.commit()
            return url
        except Exception:
            self.db.rollback()
            raise

    def retry(self, post_id, message):
        row = self.row(post_id)
        if not row or row['status'] in ('submitting','uncertain','published'):
            raise ValueError('제출 중·결과 불확정·발행 완료 글은 자동 재시도할 수 없습니다.')
        attempts = row['attempts'] + 1
        self.db.execute("UPDATE posts SET status='retry',attempts=?,retry_at=?,message=?,updated=? WHERE id=?", (attempts, time.time()+min(3600,60*2**min(attempts,6)),message,time.time(),post_id))
        self.event(post_id, 'retry', message)
        self.db.commit()

    def recover(self):
        self.db.execute("UPDATE posts SET status='retry',retry_at=0 WHERE status='preparing'")
        self.db.execute("UPDATE posts SET status='uncertain',message='발행 도중 중단: 게시 결과 대조 필요' WHERE status='submitting'")
        self.db.commit()

    def pending(self, settle):
        return [dict(r) for r in self.db.execute("SELECT * FROM posts WHERE status IN ('pending','retry') AND seen <= ? AND retry_at <= ? ORDER BY seen", (time.time()-settle,time.time()))]

    def snapshot(self):
        return {'settings':{r['key']:json.loads(r['value']) for r in self.db.execute('SELECT * FROM settings')},'posts':[dict(r) for r in self.db.execute('SELECT * FROM posts ORDER BY updated DESC LIMIT 200')],'events':[dict(r) for r in self.db.execute('SELECT * FROM events ORDER BY seq DESC LIMIT 100')]}
