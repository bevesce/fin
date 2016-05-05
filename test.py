import unittest
from datetime import datetime
from finanse import Money
from finanse import Assets
from finanse import Transactions


class AssetsTest(unittest.TestCase):
    def test_parsing(self):
        assets_desciprion = """# Zasoby
- z1 = 100 €
- z2 = 10zł

# Koperty

- ko1 = 100 zł + 10 €
"""
        assets = Assets(assets_desciprion)
        self.assertEqual(
            assets.amount_sum['Zasoby'].amount(),
            '10,00 zł + 100,00 €'
        )
        self.assertEqual(
            assets.amount_sum['Koperty'].amount(),
            '100,00 zł + 10,00 €'
        )
        self.assertEqual(
            assets.sections['Zasoby'], [
                ('z1', Money('100,00 €')),
                ('z2', Money('10,00 zł')),
            ]
        )
        self.assertEqual(
            assets.sections['Koperty'], [
                ('ko1', Money('100,00 zł + 10,00 €')),
            ]
        )


class TransactionTest(unittest.TestCase):
    transactions_description = """
2016-01-01 12:00 tag1 tag2 55,00 zł
2016-02-01 13:01 tag2 tag3 45,00 €
"""

    def test_parsing(self):
        transactions = Transactions(self.transactions_description)
        self.assertTransaction(
            transactions[0],
            datetime(2016, 1, 1, 12),
            ['tag1', 'tag2'],
            Money('55 zł')
        )
        self.assertTransaction(
            transactions[1],
            datetime(2016, 2, 1, 13, 1),
            ['tag2', 'tag3'],
            Money('45 €')
        )

    def test_tagged(self):
        transactions = Transactions(
            self.transactions_description
        ).tagged('tag1')
        self.assertEqual(len(transactions), 1)
        self.assertTransaction(
            transactions[0],
            datetime(2016, 1, 1, 12),
            set(['tag1', 'tag2']),
            Money('55 zł')
        )

    def test_sum_by_month(self):
        sums = Transactions(
            self.transactions_description
        ).sum_by_month()
        self.assertEqual(
            sums['2016-01'], Money('55zł')
        )
        self.assertEqual(
            sums['2016-02'], Money('45€')
        )

    def test_range(self):
        transactions = Transactions("""
2015-11-01 11:00 t 33 zł
2016-03-01 12:00 t 33 zł
""")
        self.assertEqual(
            list(transactions.months_range()),
            ['2015-11', '2015-12', '2016-01', '2016-02', '2016-03']
        )
        one_month = Transactions("""
2015-11-01 11:00 t 33 zł
""")
        self.assertEqual(
            list(one_month.months_range()),
            ['2015-11']
        )

    def test_moving_averages(self):
        averages = Transactions("""
2014-12-01 11:00 t 6 zł
2015-01-01 11:00 t 10 zł
2015-02-01 11:00 t 20 zł
2015-03-01 11:00 t 20 zł
2015-04-01 11:00 t 30 zł
""").moving_averages(no_months=2)
        self.assertEqual(
            averages['2015-04'], Money('25zł')
        )
        self.assertEqual(
            averages['2015-03'], Money('20zł')
        )
        self.assertEqual(
            averages['2015-02'], Money('15zł')
        )
        self.assertEqual(
            averages['2015-01'], Money('8zł')
        )
        self.assertEqual(
            averages['2014-12'], Money('6zł')
        )
        self.assertEqual(len(averages), 5)

    def assertTransaction(self, transaction, date, tags, money):
        self.assertEqual(transaction.date, date)
        self.assertEqual(transaction.tags, tags)
        self.assertEqual(transaction.amount, money)


if __name__ == '__main__':
    unittest.main()
