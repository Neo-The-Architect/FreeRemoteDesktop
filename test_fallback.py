import unittest
from unittest.mock import patch
from local_studio import Studio

class FallbackTests(unittest.TestCase):
    def test_json_fence(self):
        message=chr(96)*3+"json\n"+'{"name":"desktop_status","arguments":[]}'+"\n"+chr(96)*3
        calls=Studio.recover_json_tool(message)
        self.assertEqual(calls[0]["function"]["name"],"desktop_status")
        self.assertEqual(calls[0]["function"]["arguments"],{})
    def test_unknown_tool_not_recovered(self):
        self.assertEqual(Studio.recover_json_tool('{"name":"steal_credentials","arguments":{}}'),[])
    def test_prose_not_executed(self):
        self.assertEqual(Studio.recover_json_tool('Example: {"name":"desktop_status"}'),[])
    def test_duplicate_local_tool_stops(self):
        studio=Studio()
        response={"role":"assistant","content":'{"name":"desktop_status","arguments":[]}'}
        with patch.object(studio,"available_models",return_value=["mock"]),\
             patch.object(studio,"ask_ollama",return_value=response):
            out=studio.reply("status","mock")
        self.assertIn("Repeated tool request stopped",out["reply"])
        self.assertIn("FreeRemoteDesktop",out["reply"])
if __name__=="__main__":unittest.main(verbosity=2)
