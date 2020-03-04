# encoding:UTF-8
import unittest
from werkzeug.routing import *


class UrlTest(unittest.TestCase):
    def setUp(self) -> None:
        # <converter:variable> or <converter(100[name=100...]):,variable>
        self.test_string = "<int(100):age>"

    def test_equal_string(self):
        rule_match = list(parse_rule(self.test_string))[0]
        # first argument is converter,converter args,variable
        # print(rule_match)
        self.assertEqual(rule_match[0], "int", "Not equal")
        converter_args = parse_converter_args(rule_match[1])
        print(converter_args, "converter_args")
        self.assertEqual(int(rule_match[1]), 100)

    def test_rule_templete(self):
        test_rule = Rule("/foo")
        rule_match = list(parse_rule("www.baidu.com/<int(100):age>"))
        print(f"{test_rule!r}")
