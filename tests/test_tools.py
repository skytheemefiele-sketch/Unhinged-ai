import tempfile, unittest
from pathlib import Path
from unhinged.tools import ToolBox, ToolError

class ToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.box=ToolBox(self.tmp.name,{})
    def tearDown(self): self.tmp.cleanup()
    def test_read_write_patch(self):
        self.box.file_write("a.txt","hello")
        self.box.file_patch("a.txt","hello","world")
        self.assertEqual(self.box.file_read("a.txt"),"world")
    def test_path_traversal_blocked(self):
        with self.assertRaises(ToolError): self.box.file_read("../secret")
    def test_shell_requires_confirmation(self):
        with self.assertRaises(ToolError): self.box.shell_exec("echo hi")
