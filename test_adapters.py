import sys, types, unittest
from unittest.mock import patch
from core import action, defaults
from browser_agent import perform

class AutomationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.cfg={**defaults(),"allow_gui":True,"allow_browser":True,
                  "browser_hosts":["example.com"]}
    def test_gui_type_with_fake_driver(self):
        driver=types.ModuleType("pyautogui")
        sent=[]
        driver.write=lambda text,interval:sent.append(text)
        with patch.dict(sys.modules,{"pyautogui":driver}):
            result=action("gui_type",{"text":"safe text"},self.cfg)
        self.assertEqual(result["typed_characters"],9)
        self.assertEqual(sent,["safe text"])
    def test_gui_type_rejects_oversize(self):
        with self.assertRaises(ValueError):
            action("gui_type",{"text":"a"*4000},self.cfg)
    def test_gui_hotkey_rejects_unapproved(self):
        with self.assertRaises(PermissionError):
            action("gui_hotkey",{"keys":["alt","f4"]},self.cfg)
    def test_browser_fill_password_denied(self):
        class Field:
            def get_attribute(self,name):return "password"
        class Locator:
            first=Field()
        class Page:
            url="https://example.com/"
            def locator(self,selector):return Locator()
        with patch("browser_agent.start",return_value=Page()):
            with self.assertRaises(PermissionError):
                perform("browser_fill",{"selector":"#pass","text":"secret"},self.cfg)
    def test_browser_fill_allowed(self):
        filled=[]
        class Field:
            def get_attribute(self,name):return "text"
            def fill(self,value,timeout):filled.append(value)
        class Locator:
            first=Field()
        class Page:
            url="https://example.com/"
            def locator(self,selector):return Locator()
        with patch("browser_agent.start",return_value=Page()):
            result=perform("browser_fill",{"selector":"#q","text":"hello"},self.cfg)
        self.assertEqual(filled,["hello"])
        self.assertEqual(result["characters"],5)
    def test_browser_host_denied(self):
        from browser_agent import _check
        with self.assertRaises(PermissionError):
            _check("http://example.com",self.cfg)
        with self.assertRaises(PermissionError):
            _check("https://not-example.com",self.cfg)

if __name__=="__main__":unittest.main(verbosity=2)
