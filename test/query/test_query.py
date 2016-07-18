# -*- coding: utf-8 -*-
import unittest
from finanse import query
from finanse import Transaction

class QueryTest(unittest.TestCase):
    def test_tag(self):
        self.assertTrue(
            query('test')(Transaction('2016-01-01 test 10zł'))
        )
        self.assertFalse(
            query('foo')(Transaction('2016-01-01 test 10zł'))
        )

    def test_tag_param(self):
        self.assertTrue(
            query('test = foo')(Transaction('2016-01-01 test(foo) 10zł'))
        )
        self.assertFalse(
            query('test = bar')(Transaction('2016-01-01 test 10zł'))
        )

    def test_and(self):
        self.assertTrue(
            query('test and foo')(Transaction('2016-01-01 test foo 10zł'))
        )
        self.assertFalse(
            query('test and foo')(Transaction('2016-01-01 test bar 10zł'))
        )

    def test_or(self):
        self.assertTrue(
            query('test or foo')(Transaction('2016-01-01 test bar 10zł'))
        )
        self.assertFalse(
            query('test or foo')(Transaction('2016-01-01 bar 10zł'))
        )

    def test_not(self):
        self.assertTrue(
            query('not test')(Transaction('2016-01-01 bar 10zł'))
        )
        self.assertFalse(
            query('not test')(Transaction('2016-01-01 test 10zł'))
        )

    def test_date(self):
        self.assertTrue(
            query('date = 2016-01-01')(Transaction('2016-01-01 bar 10zł'))
        )
        self.assertTrue(
            query('date = today')(Transaction('2016-07-17 bar 10zł'))
        )
        self.assertFalse(
            query('date = 2016-01-02')(Transaction('2016-01-01 test 10zł'))
        )

    def test_money(self):
        self.assertTrue(
            query('money = 10zł')(Transaction('2016-01-01 bar 10zł'))
        )
        self.assertTrue(
            query('money = "10 zł"')(Transaction('2016-01-01 bar 10zł'))
        )
        self.assertFalse(
            query('money = 20zł')(Transaction('2016-01-01 test 10zł'))
        )

    def test_currency(self):
        self.assertTrue(
            query('currency = zł')(Transaction('2016-01-01 bar 10zł'))
        )
        self.assertFalse(
            query('currency = eur')(Transaction('2016-01-01 test 10zł'))
        )

    def test_eq(self):
        self.assertTrue(
            query('test = bar')(Transaction('2016-01-01 test(bar) 10zł'))
        )
        self.assertFalse(
            query('test = bar')(Transaction('2016-01-01 test(foo) 10zł'))
        )

    def test_neq(self):
        self.assertTrue(
            query('test != foo')(Transaction('2016-01-01 test(bar) 10zł'))
        )
        self.assertFalse(
            query('test != foo')(Transaction('2016-01-01 test(foo) 10zł'))
        )

    def test_leq(self):
        self.assertTrue(
            query('test <= b')(Transaction('2016-01-01 test(a) 10zł'))
        )
        self.assertTrue(
            query('test <= b')(Transaction('2016-01-01 test(b) 10zł'))
        )
        self.assertFalse(
            query('test <= b')(Transaction('2016-01-01 test(c) 10zł'))
        )

    def test_geq(self):
        self.assertFalse(
            query('test >= b')(Transaction('2016-01-01 test(a) 10zł'))
        )
        self.assertTrue(
            query('test >= b')(Transaction('2016-01-01 test(b) 10zł'))
        )
        self.assertTrue(
            query('test >= b')(Transaction('2016-01-01 test(c) 10zł'))
        )

    def test_lt(self):
        self.assertTrue(
            query('test < b')(Transaction('2016-01-01 test(a) 10zł'))
        )
        self.assertFalse(
            query('test < b')(Transaction('2016-01-01 test(b) 10zł'))
        )
        self.assertFalse(
            query('test < b')(Transaction('2016-01-01 test(c) 10zł'))
        )

    def test_gt(self):
        self.assertFalse(
            query('test > b')(Transaction('2016-01-01 test(a) 10zł'))
        )
        self.assertFalse(
            query('test > b')(Transaction('2016-01-01 test(b) 10zł'))
        )
        self.assertTrue(
            query('test > b')(Transaction('2016-01-01 test(c) 10zł'))
        )

    def test_in(self):
        self.assertTrue(
            query('test *= b')(Transaction('2016-01-01 test(aba) 10zł'))
        )
        self.assertFalse(
            query('test *= b')(Transaction('2016-01-01 test(aaa) 10zł'))
        )

    def test_starts(self):
        self.assertTrue(
            query('test ^= b')(Transaction('2016-01-01 test(baa) 10zł'))
        )
        self.assertFalse(
            query('test ^= b')(Transaction('2016-01-01 test(abb) 10zł'))
        )

    def test_ends(self):
        self.assertTrue(
            query('test $= b')(Transaction('2016-01-01 test(aab) 10zł'))
        )
        self.assertFalse(
            query('test $= b')(Transaction('2016-01-01 test(baa) 10zł'))
        )

    def test_logical_and_operational(self):
        self.assertTrue(
            query('test = b and foo')(Transaction('2016-01-01 test(b) foo 10zł'))
        )
        self.assertFalse(
            query('test = b and foo')(Transaction('2016-01-01 test(b) 10zł'))
        )
        self.assertFalse(
            query('test = b and foo')(Transaction('2016-01-01 foo 10zł'))
        )

if __name__ == '__main__':
    unittest.main()
