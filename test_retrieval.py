import pathlib,tempfile,unittest
from core import defaults
from retrieval import read_lines,search_text

class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.temp.name)
        self.cfg={**defaults(),"roots":[str(self.root)]}
        (self.root/"a.py").write_text("alpha\nTARGET term\nomega\n",encoding="utf-8")
        (self.root/".env").write_text("TARGET PRIVATE",encoding="utf-8")
    def tearDown(self):self.temp.cleanup()
    def test_scoped_lines(self):
        r=read_lines(str(self.root/"a.py"),2,2,self.cfg)
        self.assertEqual(r["lines"],["2: TARGET term"])
    def test_search(self):
        r=search_text(str(self.root),"target",self.cfg)
        self.assertEqual(len(r["matches"]),1)
        self.assertEqual(r["matches"][0]["line"],2)
        self.assertEqual(r["model_calls"],0)
    def test_search_skips_secrets(self):
        r=search_text(str(self.root),"PRIVATE",self.cfg)
        self.assertEqual(r["matches"],[])
    def test_outside_root_denied(self):
        with self.assertRaises(PermissionError):
            read_lines(str(self.root.parent/"not_authorized.txt"),1,1,self.cfg)
    def test_large_range_denied(self):
        with self.assertRaises(ValueError):
            read_lines(str(self.root/"a.py"),1,151,self.cfg)
    def test_short_query_denied(self):
        with self.assertRaises(ValueError):
            search_text(str(self.root),"a",self.cfg)

if __name__=="__main__":unittest.main(verbosity=2)
