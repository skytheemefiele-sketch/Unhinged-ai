import unittest
from unhinged.parser import extract_tool_calls

class ParserTests(unittest.TestCase):
    def test_json_and_fenced_json(self):
        text='Tool: ```json\\n{"tool":"file_list","arguments":{"path":"."}}\\n```'
        self.assertEqual(extract_tool_calls(text)[0]["tool"],"file_list")
    def test_malformed_is_ignored(self):
        self.assertEqual(extract_tool_calls('{"tool":'),[])
