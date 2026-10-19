import io
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from codex_bridge import normalize_limits
from manager import Manager, Handler, ThreadingHTTPServer
from auth import crypt


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.manager=Manager(self.temp.name)
    def tearDown(self):
        self.manager.stop_event.set()
        for handler in list(self.manager.log.handlers):
            handler.close();self.manager.log.removeHandler(handler)
        self.temp.cleanup()

    def test_missing_and_swapped_usage_windows(self):
        data=normalize_limits({'rateLimits':{'primary':{'usedPercent':27,'windowDurationMins':10080,'resetsAt':1},'secondary':{'usedPercent':73,'windowDurationMins':300,'resetsAt':2}}})
        windows={w['label']:w for w in data['buckets'][0]['windows']}
        self.assertEqual(windows['주간']['remaining'],73)
        self.assertEqual(windows['5시간']['remaining'],27)
        self.assertEqual(normalize_limits({})['buckets'],[])

    def test_quota_unavailable_is_not_zero(self):
        data=normalize_limits({'rateLimits':{'primary':{'usedPercent':None,'windowDurationMins':300}}})
        self.assertIsNone(data['buckets'][0]['windows'][0]['remaining'])

    def test_model_effort_validation_and_persistence(self):
        self.manager.models=[{'id':'known','efforts':['low'],'default_effort':'low'}]
        ai={'normal_model':'known','normal_effort':'low','complex_model':'known','complex_effort':'ultra','daily_limit':5}
        with self.assertRaises(ValueError):self.manager.update_settings({'codex':ai})
        ai['complex_effort']='low'
        self.manager.update_settings({'codex':ai})
        saved=json.loads(self.manager.config_path.read_text('utf8'))
        self.assertEqual(saved['codex']['normal_model'],'known')

    def test_pause_survives_restart(self):
        self.manager.command('pause',{})
        replacement=Manager(self.temp.name)
        self.assertEqual(replacement.control['mode'],'paused')

    def test_category_change_requires_explicit_ui_confirmation(self):
        with self.assertRaises(ValueError):
            self.manager.update_writer({'id':'muse-01','name':'Rumi','category_name':'다른 카테고리','category_id':20})

    def test_uncertain_job_cannot_be_retried(self):
        from types import SimpleNamespace
        with self.manager.store() as s:
            p=SimpleNamespace(path='posts/muse-01/test/post.md',meta={'post_id':'muse-01:test','revision':1,'title':'test'},fingerprint='abc')
            s.ingest(p,'commit');s.transition('muse-01:test','submitting');s.recover()
        with self.assertRaises(ValueError):self.manager.command('retry',{'id':'muse-01:test'})

    def test_dpapi_roundtrip(self):
        self.assertEqual(crypt(crypt(b'test-only-not-a-secret'),True),b'test-only-not-a-secret')

    def test_http_control_security(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.manager=self.manager
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with self.assertRaises(HTTPError) as error:urlopen(url+'/api/state')
            self.assertEqual(error.exception.code,403)
            request=Request(url+'/api/pause',data=b'{}',headers={'Content-Type':'application/json','X-Manager-Token':self.manager.token,'Origin':'https://evil.example'})
            with self.assertRaises(HTTPError) as error:urlopen(request)
            self.assertEqual(error.exception.code,403)
            request=Request(url+'/api/state',headers={'X-Manager-Token':self.manager.token})
            with urlopen(request) as r:self.assertIn('documents',json.load(r))
            request=Request(url+'/api/pause',data=b'{}',headers={'Content-Type':'application/json','X-Manager-Token':self.manager.token,'Origin':url})
            with urlopen(request) as r:self.assertIn('message',json.load(r))
        finally:server.shutdown();server.server_close()


if __name__=='__main__':unittest.main()
