import unittest
from datetime import datetime
from collections import defaultdict

from finanse.money import Money


class MoneyParsingTest(unittest.TestCase):
    def setUp(self):
        Money.convert_currency = lambda x, f, t: x if f == t else 2 * x

    def test_creation(self):
        amounts = defaultdict(lambda: 0)
        amounts['zł'] = 10 * 100
        zloty10 = Money(amounts)
        self.assertEqual(zloty10(), '10,00 zł')

    def test_multicurrency_creation(self):
        zloty10euro20 = Money('10 zł + 20,00€')
        self.assertEqual(zloty10euro20(), '10,00 zł + 20,00 €')

    def test_parsing(self):
        zloty10 = Money('10 zł')
        self.assertEqual(zloty10('zł'), '10,00 zł')

    def test_parsing_with_fractions(self):
        zloty10 = Money('10,13 zł')
        self.assertEqual(zloty10('zł'), '10,13 zł')

    def test_parsing_with_single_digit_fractions(self):
        zloty10 = Money('10,3 zł')
        self.assertEqual(zloty10('zł'), '10,30 zł')

    def test_parsing_with_fractions_with_dot(self):
        zloty10 = Money('10.13 zł')
        self.assertEqual(zloty10('zł'), '10,13 zł')

    def test_parsing_without_space(self):
        zloty10 = Money('10zł')
        self.assertEqual(zloty10('zł'), '10,00 zł')

    def test_parsing_without_space_with_fraction(self):
        zloty10 = Money('10,13zł')
        self.assertEqual(zloty10('zł'), '10,13 zł')

    def test_addition(self):
        zloty10 = Money('10zł')
        zloty20 = Money('20zł')
        self.assertEqual(
            (zloty10 + zloty20)('zł'),
            '30,00 zł'
        )


class MoneyOperationsTest(unittest.TestCase):
    def setUp(self):
        Money.convert_currency = lambda x, f, t: x if f == t else 2 * x

    def test_substraction(self):
        zloty10 = Money('10 zł')
        zloty20 = Money('20 zł')
        self.assertEqual(
            (zloty10 - zloty20)('zł'),
            '-10,00 zł'
        )

    def test_division(self):
        zloty10 = Money('10zł')
        self.assertEqual(
            (zloty10 / 2)('zł'),
            '5,00 zł'
        )

    def test_multiple_currencies_addition(self):
        zloty10 = Money('10zł')
        euro10 = Money('10€')
        self.assertEqual(
            (zloty10 + euro10)(),
            '10,00 zł + 10,00 €'
        )
        self.assertTrue(
            (zloty10 + euro10)('zł') == '30,00 zł'
        )


if __name__ == '__main__':
    unittest.main()
