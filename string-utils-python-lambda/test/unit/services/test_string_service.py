import unittest

from src.common.errors import ValidationError
from src.services.string_service import operate


class StringServiceTest(unittest.TestCase):
    def test_upper(self):
        self.assertEqual(operate("upper", "hello", ""), "HELLO")

    def test_lower(self):
        self.assertEqual(operate("lower", "HeLLo", ""), "hello")

    def test_reverse(self):
        self.assertEqual(operate("reverse", "hello", ""), "olleh")

    def test_concat(self):
        self.assertEqual(operate("concat", "foo", "bar"), "foobar")

    def test_concat_with_empty_b(self):
        self.assertEqual(operate("concat", "foo", ""), "foo")

    def test_non_string_input_is_stringified(self):
        self.assertEqual(operate("upper", 123, ""), "123")

    def test_unknown_operation(self):
        with self.assertRaises(ValidationError) as ctx:
            operate("unknown", "hello", "")
        self.assertEqual(str(ctx.exception), "Unsupported operation: unknown")


if __name__ == "__main__":
    unittest.main()
