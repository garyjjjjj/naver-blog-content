import copy
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from publication_proof import validate_publication, UnconfirmedPublication
from store import Store


class PublicationProofTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name)/'test.sqlite')
        self.post = SimpleNamespace(path='posts/muse-01/example/post.md',
            meta={'post_id':'example','revision':1,'title':'뮤즈의 원래 제목'},fingerprint='a'*64,images=['a.jpg','b.jpg'])
        self.store.ingest(self.post,'c'*40)
        self.store.transition('example','submitting')
        self.proof = dict(url='https://blog.naver.com/3700708/123456',editor_open=False,
            viewer_reloaded=True,body_verified=True,image_order_verified=True,title=self.post.meta['title'],
            category_id=15,visibility='public',image_count=2,post_id='example',revision=1,
            fingerprint=self.post.fingerprint,source_commit='c'*40,checked_at=time.time())

    def tearDown(self):
        self.store.db.close()
        self.temp.cleanup()

    def test_click_or_url_alone_cannot_mark_success(self):
        with self.assertRaises(ValueError):self.store.transition('example','published',url=self.proof['url'])
        with self.assertRaises(UnconfirmedPublication):self.store.confirm_publication(self.post,{'url':self.proof['url']},blog_id='3700708',category_id=15)
        self.assertEqual(self.store.row('example')['status'],'submitting')

    def test_partial_wrong_and_stale_results_are_rejected(self):
        for field,value in [('url','https://blog.naver.com/other/123456'),('editor_open',True),
            ('viewer_reloaded',False),('title','다른 제목'),('category_id',16),('visibility','private'),
            ('image_count',1),('body_verified',False),('image_order_verified',False),
            ('revision',2),('fingerprint','b'*64),('source_commit','d'*40),('checked_at',time.time()-301)]:
            with self.subTest(field=field):
                evidence={**self.proof,field:value}
                with self.assertRaises(UnconfirmedPublication):self.store.confirm_publication(self.post,evidence,blog_id='3700708',category_id=15)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM publication_proofs').fetchone()[0],0)

    def test_evidence_and_completion_are_persisted_together(self):
        self.store.confirm_publication(self.post,self.proof,blog_id='3700708',category_id=15)
        self.assertEqual(self.store.row('example')['published_fingerprint'],self.post.fingerprint)
        self.assertEqual(self.store.db.execute('SELECT url FROM publication_proofs').fetchone()[0],self.proof['url'])
        with self.assertRaises(ValueError):self.store.retry('example','再試行')

    def test_update_must_keep_original_post_number(self):
        self.store.confirm_publication(self.post,self.proof,blog_id='3700708',category_id=15)
        revised=copy.deepcopy(self.post);revised.meta['revision']=2;revised.fingerprint='b'*64
        self.store.ingest(revised,'d'*40);self.store.transition('example','submitting')
        evidence={**self.proof,'revision':2,'fingerprint':'b'*64,'source_commit':'d'*40,'url':'https://blog.naver.com/3700708/999999'}
        with self.assertRaises(UnconfirmedPublication):self.store.confirm_publication(revised,evidence,blog_id='3700708',category_id=15)
        evidence['url']=self.proof['url']
        self.store.confirm_publication(revised,evidence,blog_id='3700708',category_id=15)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM publication_proofs').fetchone()[0],2)

    def test_interrupted_submission_never_becomes_retry(self):
        self.store.recover()
        with self.assertRaises(ValueError):self.store.retry('example','자동 재시도')
        self.assertEqual(self.store.row('example')['status'],'uncertain')


if __name__=='__main__':unittest.main()
