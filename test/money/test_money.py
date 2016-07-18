# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from collections import defaultdict

from finanse import Money
from finanse import currency
from finanse import MoneyParseError


currency.cache = {'2016-01-01': {'PLN': {'EUR': 0.25}, 'USD': {'EUR': 0.5}}}


class MoneyParsingTest(unittest.TestCase):
    def setUp(self):
        Money.convert_currency = lambda x, f, t: x if f == t else 2 * x

    def test_creation(self):
        amounts = defaultdict(lambda: 0)
        amounts['zł'] = 10 * 100
        zloty10 = Money(amounts)
        self.assertEqual(str(zloty10), '10,00 zł')

    def test_multicurrency_creation(self):
        zloty10euro20 = Money('10 zł + 20,00€')
        self.assertEqual(str(zloty10euro20), '10,00 zł + 20,00 €')

    def test_parsing(self):
        zloty10 = Money('10 zł')
        self.assertEqual(str(zloty10), '10,00 zł')

    def test_parsing_with_fractions(self):
        zloty10 = Money('10,13 zł')
        self.assertEqual(str(zloty10), '10,13 zł')

    def test_parsing_with_single_digit_fractions(self):
        zloty10 = Money('10,3 zł')
        self.assertEqual(str(zloty10), '10,30 zł')

    def test_parsing_with_fractions_with_dot(self):
        zloty10 = Money('10.13 zł')
        self.assertEqual(str(zloty10), '10,13 zł')

    def test_parsing_without_space(self):
        zloty10 = Money('10zł')
        self.assertEqual(str(zloty10), '10,00 zł')

    def test_parsing_without_space_with_fraction(self):
        zloty10 = Money('10,13zł')
        self.assertEqual(str(zloty10), '10,13 zł')

    def test_addition(self):
        zloty10 = Money('10zł')
        zloty20 = Money('20zł')
        self.assertEqual(
            str(zloty10 + zloty20),
            '30,00 zł'
        )

    def test_parsing_invalid_base_unit(self):
        with self.assertRaises(MoneyParseError) as cm:
            Money('xx zł')
        self.assertEqual(str(cm.exception), "can't parse 'xx zł' as money")

    def test_parsing_invalid_subunit(self):
        with self.assertRaises(MoneyParseError) as cm:
            print(Money('0,x0zł'))
        self.assertEqual(str(cm.exception), "can't parse '0,x0zł' as money")

    def test_parsing_missing_currency(self):
        with self.assertRaises(MoneyParseError) as cm:
            print(Money('0,0'))
        self.assertEqual(str(cm.exception), "can't parse '0,0' as money")


class MoneyOperationsTest(unittest.TestCase):
    def test_lt(self):
        zloty10 = Money('10 zł')
        euro10 = Money('20 zł')
        self.assertTrue(zloty10 < euro10)
        self.assertFalse(euro10 < zloty10)

    def test_lte(self):
        zloty10 = Money('10 zł')
        euro10 = Money('20 zł')
        self.assertTrue(zloty10 <= euro10)
        self.assertFalse(euro10 <= zloty10)

    def test_gt(self):
        zloty10 = Money('10 zł')
        euro10 = Money('20 zł')
        self.assertFalse(zloty10 > euro10)
        self.assertTrue(euro10 > zloty10)

    def test_gte(self):
        zloty10 = Money('10 zł')
        euro10 = Money('20 zł')
        self.assertFalse(zloty10 >= euro10)
        self.assertTrue(euro10 >= zloty10)

    def test_substraction(self):
        zloty10 = Money('10 zł')
        zloty20 = Money('20 zł')
        self.assertEqual(
            str(zloty10 - zloty20),
            '-10,00 zł'
        )

    def test_division(self):
        zloty10 = Money('10zł')
        self.assertEqual(
            str(zloty10 / 2),
            '5,00 zł'
        )

    def test_multiple_currencies_addition(self):
        zloty10 = Money('10zł')
        euro10 = Money('10€')
        self.assertEqual(
            str(zloty10 + euro10),
            '10,00 zł + 10,00 €'
        )

    def test_amount(self):
        self.assertEqual(Money('19zł').amount('zł'), 19)


class MoneyConversionTest(unittest.TestCase):
    def test_convert_money(self):
        zloty40_in_euro = Money('40zł').convert('€', datetime(2016, 1, 1))
        self.assertEqual(
            zloty40_in_euro,
            '10,00 €'
        )

    def test_convert_money_from_multiple_currencies(self):
        zloty40_in_euro = Money('40zł + 20$').convert('€', datetime(2016, 1, 1))
        self.assertEqual(
            zloty40_in_euro,
            '20,00 €'
        )

if __name__ == '__main__':
    unittest.main()
