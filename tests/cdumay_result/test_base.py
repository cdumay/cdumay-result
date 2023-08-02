# /usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>

"""

import unittest

from cdumay_error.types import ValidationError
from cdumay_result import Result, ResultSchema


class TestResult(unittest.TestCase):
    """Tests for class Result"""

    def test_init(self):
        """Test Result init"""
        result = Result()
        self.assertEqual(result.retcode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.retval, {})
        self.assertRegex(result.uuid, r'^[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}$')

    def test_prints(self):
        """Test Print methods"""
        result = Result(stderr="Error: ", stdout="Success: ")
        result.print_err("No")
        result.print("Yes")
        self.assertEqual(result.stdout, "Success: Yes\n")
        self.assertEqual(result.stderr, "Error: No\n")

    def test_exception_serialization(self):
        """Serialization from Exception"""
        result = Result.from_exception(RuntimeError(), '7e16180d-7840-4b06-bb5c-a28afe84b1da')
        self.assertEqual(result.uuid, '7e16180d-7840-4b06-bb5c-a28afe84b1da')
        self.assertEqual(result.retcode, 500)
        self.assertEqual(result.stderr, "Internal Error")
        self.assertEqual(result.stdout, "")
        self.assertEqual(
            result.retval,
            {'error': {
                'code': 500,
                'extra': {'uuid': '7e16180d-7840-4b06-bb5c-a28afe84b1da'},
                'message': 'Internal Error',
                'msgid': 'ERR-29885',
                'name': 'InternalError',
                'stack': None
            }}
        )

    def test_search(self):
        """Search in retval using xpath"""
        result = Result(retval={"user": {"id": 5, "name": "john", "children": ['Kevin', 'Britney']}})
        self.assertEqual(result.search_value("user.id"), 5)
        self.assertEqual(result.search_value("user.children"), ['Kevin', 'Britney'])
        self.assertIsNone(result.search_value("user.age"))
        self.assertEqual(result.search_value("user.age", default=40), 40)
        with self.assertRaises(ValidationError) as context:
            self.assertIsNone(result.search_value("user.age", fail_if_no_match=True))
        self.assertEqual(context.exception.message, "No value found for xpath: 'user.age'")

    def test_stringify(self):
        self.assertEqual(str(Result(stdout="Success: Yes")), "Success: Yes")
        self.assertEqual(str(Result(retcode=1, stderr="Error: No")), "Error: No")
        self.assertEqual(repr(Result(retcode=400)), "Result<retcode='400'>")

    def test_add(self):
        """Add 2 results"""
        res1 = Result(stdout="Success!", retval={"a": 5, "b": 8})
        res2 = Result(retcode=1, stderr="Error!", retval={"b": 5, "c": 4})
        result = res1 + res2
        self.assertEqual(result.uuid, res1.uuid)
        self.assertEqual(result.retcode, 1)
        self.assertEqual(result.stderr, "Error!")
        self.assertEqual(result.stdout, "Success!")
        self.assertEqual(result.retval, {"a": 5, "b": 5, "c": 4})

    def test_serialization(self):
        """Serialize result"""
        result = ResultSchema().dump(Result(stdout="Success!", retval={"a": 5, "b": 8}))
        self.assertRegex(result['uuid'], r'^[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}$')
        self.assertEqual(result['retcode'], 0)
        self.assertEqual(result['stderr'], "")
        self.assertEqual(result['stdout'], "Success!")
        self.assertEqual(result['retval'], {"a": 5, "b": 8})
