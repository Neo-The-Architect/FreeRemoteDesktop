import http.client, http.server, json, threading, unittest
from local_studio import Handler, Studio

class StudioHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
        Handler.port=cls.server.server_address[1]
        Handler.token="unit-test-only-token"
        Handler.studio=Studio()
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
    def request(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection("127.0.0.1",Handler.port,timeout=3)
        conn.request(method,path,json.dumps(body).encode() if body is not None else None,headers or {})
        response=conn.getresponse()
        code=response.status
        data=response.read()
        conn.close()
        return code,data
    def test_assets_load(self):
        for path in ("/","/studio.js","/style.css","/api/bootstrap"):
            code,data=self.request("GET",path)
            self.assertEqual(code,200,path)
            self.assertTrue(data)
    def test_host_rebinding_denied(self):
        code,_=self.request("GET","/api/bootstrap",headers={"Host":"attacker.invalid"})
        self.assertEqual(code,403)
    def test_post_origin_denied(self):
        code,_=self.request("POST","/api/chat",{"message":"hi"},headers={
            "Content-Type":"application/json","X-FRD-Session":Handler.token,
            "Origin":"https://attacker.invalid"})
        self.assertEqual(code,403)
    def test_post_wrong_token_denied(self):
        code,_=self.request("POST","/api/chat",{"message":"hi"},headers={
            "Content-Type":"application/json","X-FRD-Session":"wrong",
            "Origin":f"http://127.0.0.1:{Handler.port}"})
        self.assertEqual(code,403)
    def test_post_models_unavailable(self):
        headers={"Content-Type":"application/json","X-FRD-Session":Handler.token,
                 "Origin":f"http://127.0.0.1:{Handler.port}"}
        code,data=self.request("POST","/api/chat",{"message":"hi","model":"nonexistent"},headers)
        self.assertEqual(code,400)
        self.assertIn("Select an installed",data.decode())
    def test_offline_recipe_policy(self):
        headers={"Content-Type":"application/json","X-FRD-Session":Handler.token,
                 "Origin":f"http://127.0.0.1:{Handler.port}"}
        code,data=self.request("POST","/api/recipes",{"recipe":"python_compile","workspace":"C:/not-approved"},headers)
        self.assertEqual(code,400)
        self.assertIn("error",data.decode())

if __name__=="__main__":unittest.main(verbosity=2)
