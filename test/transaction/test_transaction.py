# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

from finanse import Transaction
from finanse import TransactionParseError
from finanse import Money
from finanse import currency


def empty(*tags):
    return {t: None for t in tags}


class TransactionParsingTest(unittest.TestCase):
    def assertTransaction(self, transaction, date, tags, money):
        self.assertEqual(transaction.date, date)
        self.assertEqual(transaction.tags, tags)
        self.assertEqual(transaction.money, money)

    def test_parse_empty_tags(self):
        self.assertTransaction(
            Transaction('2016-01-02 10 zł'),
            datetime(2016, 1, 2), {}, Money('10zł')
        )

    def test_parse_single_tag(self):
        self.assertTransaction(
            Transaction('2016-01-02 t1 10 zł'),
            datetime(2016, 1, 2), empty('t1'), Money('10zł')
        )

    def test_parse_two_tags(self):
        self.assertTransaction(
            Transaction('2016-01-02 t1 t2 10 zł'),
            datetime(2016, 1, 2), empty('t1', 't2'), Money('10zł')
        )

    def test_parse_single_tag_with_parameter(self):
        self.assertTransaction(
            Transaction('2016-01-02 t1(foo) 10 zł'),
            datetime(2016, 1, 2), {'t1': 'foo'}, Money('10zł')
        )

    def test_parse_two_tags_with_parameters(self):
        self.assertTransaction(
            Transaction('2016-01-02 t1(foo) t2(bar) 10 zł'),
            datetime(2016, 1, 2), {'t1': 'foo', 't2': 'bar'}, Money('10zł')
        )

    def test_balancing_parentheis(self):
        self.assertTransaction(
            Transaction('2016-01-02 t1(foo(bar)) 10 zł'),
            datetime(2016, 1, 2), {'t1': 'foo(bar)'}, Money('10zł')
        )

    def test_balancing_parentheis_and_spaces(self):
        self.assertTransaction(
            Transaction('2016-01-02 t1(foo bar) 10 zł'),
            datetime(2016, 1, 2), {'t1': 'foo bar'}, Money('10zł')
        )

    def test_balancing_parentheis_and_tabs(self):
        self.assertTransaction(
            Transaction('2016-01-02 t1(foo\tbar) 10 zł'),
            datetime(2016, 1, 2), {'t1': 'foo\tbar'}, Money('10zł')
        )

    def test_creation(self):
        self.assertTransaction(
            Transaction(
                datetime(2016, 12, 11, 11, 10), {'tag1': None, 'tag2': None}, Money('10zł')
            ),
            datetime(2016, 12, 11, 11, 10),
            {'tag1': None, 'tag2': None},
            Money('10zł')
        )

    def test_parse_with_space_before_currency(self):
        self.assertTransaction(
            Transaction('2016-01-02 tag1 tag2 10 zł'),
            datetime(2016, 1, 2), empty('tag1', 'tag2'), Money('10zł')
        )

    def test_parse_without_space_before_currency(self):
        self.assertTransaction(
            Transaction('2016-01-02 tag1 tag2 10zł'),
            datetime(2016, 1, 2), empty('tag1', 'tag2'), Money('10zł')
        )

    def test_parse_invalid_date(self):
        with self.assertRaises(TransactionParseError) as cm:
            Transaction('2016-0x-02 re 10zł')
        self.assertEqual(
            str(cm.exception),
            "can't parse '2016-0x-02' as date from '2016-0x-02 re 10zł'"
        )

    def test_parse_invalid_money(self):
        with self.assertRaises(TransactionParseError) as cm:
            print(Transaction('2016-01-02 re 10,x0zł'))
        self.assertEqual(
            str(cm.exception),
            "can't parse 're 10,x0zł or 10,x0zł' as money from '2016-01-02 re 10,x0zł'"
        )


class TransactionConversionTest(unittest.TestCase):
    def test_convert_currency(self):
        currency.cache = {
            '2016-01-01': {'PLN': {'EUR': 0.25}}
        }
        self.assertEqual(
            str(Transaction('2016-01-01 test 10zł').convert('€')),
            '2016-01-01 test 2,50 €'
        )


if __name__ == '__main__':
    unittest.main()
