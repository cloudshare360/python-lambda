"""Unit tests for calc_service business logic."""

import unittest

from src.common.errors import ValidationError
from src.services import calc_service


class TestCalcService(unittest.TestCase):
    def test_add(self):
        self.assertEqual(calc_service.operate("add", 10, 5), 15.0)

    def test_sub(self):
        self.assertEqual(calc_service.operate("sub", 10, 5), 5.0)

    def test_mul(self):
        self.assertEqual(calc_service.operate("mul", 10, 5), 50.0)

    def test_div(self):
        self.assertEqual(calc_service.operate("div", 10, 4), 2.5)

    def test_div_by_zero(self):
        with self.assertRaises(ValidationError) as ctx:
            calc_service.operate("div", 10, 0)
        self.assertEqual(str(ctx.exception), "Cannot divide by zero")

    def test_unknown_operation(self):
        with self.assertRaises(ValidationError) as ctx:
            calc_service.operate("mod", 10, 5)
        self.assertEqual(str(ctx.exception), "Unsupported operation: mod")

    def test_non_numeric_operand(self):
        with self.assertRaises(ValidationError):
            calc_service.operate("add", "ten", 5)


if __name__ == "__main__":
    unittest.main()
