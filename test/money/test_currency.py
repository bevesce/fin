# -*- coding: utf-8 -*-
import unittest
import os
from finanse import currency
from datetime import date




class ConvertTest(unittest.TestCase):
    def setUp(self):
        currency.cache = {}

    def test_convert(self):
        self.assertEqual(2 * 4.2732, currency.convert(2, 'EUR', 'PLN', date(2015, 1, 1)))

    def test_redundant_convert(self):
        self.assertEqual(2, currency.convert(2, 'EUR', 'EUR', date(2015, 1, 1)))

    def test_convert_using_aliases(self):
        self.assertEqual(4.2732, currency.convert(1, '€', 'zł', date(2015, 1, 1)))

    def test_attemt_convert_with_invalid_from_currency(self):
        raised = False
        try:
            currency.convert(1, 'test', 'zł', date(2015, 1, 1))
        except Exception as e:
            print(e)
            self.assertEqual(
                "Couldn't download conversion rates for base: 'test' at date: '2015-01-01', because: [422] Invalid base",
                str(e)
            )
            raised = True
        self.assertTrue(raised)

    def test_attemt_convert_with_invalid_to_currency(self):
        raised = False
        try:
            currency.convert(1, '€', 'test', date(2015, 1, 1))
        except Exception as e:
            self.assertEqual(
                "Currency 'test' is not supported by fixer.io",
                str(e)
            )
            raised = True
        self.assertTrue(raised)


    def test_saves_ratios_in_cache(self):
        currency.convert(1, 'EUR', 'PLN', date(2015, 1, 1))
        self.assertEqual(
            4.2732,
            currency.cache['2015-01-01']['EUR']['PLN']
        )

    def test_saves_cache_to_file(self):
        currency.setup_cache('test_ratios.json')
        currency.cache = 'test'
        currency._save_cache()
        with open('test_ratios.json', 'r', encoding='utf-8') as f:
            self.assertEqual('"test"', f.read())
        currency.setup_cache(None)
        os.remove('test_ratios.json')


if __name__ == '__main__':
    print('tests e2e integration with fixer.io API')
    unittest.main()
