# -*- coding: utf-8 -*-
import unittest
from finanse import GroupedTransactions
from finanse import Transactions
from finanse import Transaction
from finanse import Money
from finanse import GroupedMoney


class GroupedTransactionsTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(
            GroupedTransactions({'test': Transactions('2016-01-01 test 10zł')}),
            GroupedTransactions({'test': Transactions('2016-01-01 test 10zł')})
        )

    def test_get_item(self):
        self.assertEqual(
            GroupedTransactions({'test': Transactions('2016-01-01 test 10zł')})['test'],
            Transactions('2016-01-01 test 10zł')
        )

    def test_str(self):
        self.assertEqual(
            str(GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            })),
            """test1:
2016-01-01 test 10,00 zł

test2:
2016-01-01 test 20,00 zł"""
        )

    def test_len(self):
        self.assertEqual(
            len(GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            })),
            2
        )

    def test_iter(self):
        self.assertEqual(
            list(GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            })),
            ['test1', 'test2']
        )

    def test_map(self):
        self.assertEqual(
            GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            }).map(lambda t: Transaction(t.date, t.tags, t.money * 2)),
            GroupedTransactions({
                'test1': Transactions('2016-01-01 test 20zł'),
                'test2': Transactions('2016-01-01 test 40zł'),
            })
        )

    def test_filter(self):
        self.assertEqual(
            GroupedTransactions({
                'test1': Transactions('2016-01-01 test1 10zł'),
                'test2': Transactions('2016-01-01 test2 20zł'),
            }).filter(lambda t: 'test1' in t.tags),
            GroupedTransactions({
                'test1': Transactions('2016-01-01 test1 10zł'),
                'test2': Transactions(),
            })
        )

    def test_sum(self):
        self.assertEqual(
            GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł\n2017-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 30zł'),
            }).sum(),
            GroupedMoney({
                'test1': Money('20zł'),
                'test2': Money('30zł'),
            })
        )

    def test_group(self):
        self.assertEqual(
            GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł\n2017-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            }).group(lambda t: t.date.strftime('%Y')),
            GroupedTransactions({
               'test1': GroupedTransactions({
                    '2016': Transactions('2016-01-01 test 10zł'),
                    '2017': Transactions('2017-01-01 test 10zł')
                }),
               'test2': GroupedTransactions({
                    '2016': Transactions('2016-01-01 test 20zł')
                }),
            })
        )

    def test_groups(self):
        self.assertEqual(
            GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            }).groups(),
            ['test1', 'test2']
        )

    def test_items(self):
        self.assertEqual(
            list(GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            }).items()),
            [
                ('test1', Transactions('2016-01-01 test 10zł')),
                ('test2', Transactions('2016-01-01 test 20zł'))
            ]
        )

    def test_transactions(self):
        self.assertEqual(
            list(GroupedTransactions({
                'test1': Transactions('2016-01-01 test 10zł'),
                'test2': Transactions('2016-01-01 test 20zł'),
            }).transactions()),
            [
                Transactions('2016-01-01 test 10zł'),
                Transactions('2016-01-01 test 20zł')
            ]
        )

    def test_add(self):
        g1 = GroupedTransactions({
            '1': Transactions('2016-01-01 test1 10zł'),
            '2': Transactions('2016-01-01 test2 20zł'),
        })
        g2 = GroupedTransactions({
            '2': Transactions('2016-01-01 test22 10zł'),
            '3': Transactions('2016-01-01 test3 20zł'),
        })
        self.assertEqual(
            g1 + g2,
            GroupedTransactions({
                '1': Transactions('2016-01-01 test1 10zł'),
                '2': Transactions('2016-01-01 test2 20zł\n2016-01-01 test22 10zł'),
                '3': Transactions('2016-01-01 test3 20zł'),
            })
        )

if __name__ == '__main__':
    unittest.main()
