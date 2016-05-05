import unittest
from datetime import datetime

from finanse.transaction import Transaction
from finanse.transaction import Transactions
from finanse.transaction import GroupedTransactions
from finanse.money import Money


class TransactionParsingTest(unittest.TestCase):
    def assertTransaction(self, transaction, date, tags, amount):
        self.assertEqual(transaction.date, date)
        self.assertEqual(transaction.tags, tuple(tags))
        self.assertEqual(transaction.amount, amount)

    def test_creation(self):
        self.assertTransaction(
            Transaction(
                datetime(2016, 12, 11, 11, 10), ('tag1', 'tag2'), Money('10zł')
            ),
            datetime(2016, 12, 11, 11, 10),
            ('tag1', 'tag2'),
            Money('10zł')
        )

    def test_parse_with_space_before_currency(self):
        self.assertTransaction(
            Transaction('2016-01-02 03:04 tag1 tag2 10 zł'),
            datetime(2016, 1, 2, 3, 4), ('tag1', 'tag2'), Money('10zł')
        )

    def test_parse_without_space_before_currency(self):
        self.assertTransaction(
            Transaction('2016-01-02 03:04 tag1 tag2 10zł'),
            datetime(2016, 1, 2, 3, 4), ('tag1', 'tag2'), Money('10zł')
        )


class TransactionsTest(unittest.TestCase):
    def test_transaction_eq(self):
        self.assertTrue(
            Transactions(
                '2016-01-02 03:04 tag1 tag2 10zł'
            ) == Transactions(
                '2016-01-02 03:04 tag1 tag2 10zł'
            )
        )

    def test_transaction_group(self):
        transactions = Transactions("""
2016-01-02 03:04 tag1 tag2 11zł
2016-01-02 03:05 tag1 tag2 12zł
2016-02-02 03:06 tag1 tag2 13zł
2016-03-02 03:07 tag1 tag2 14zł
        """)
        grouped_transactions = transactions.group(lambda t: t.date.strftime('%Y-%m'))
        self.assertEqual(
            grouped_transactions,
            GroupedTransactions({
                '2016-01': Transactions("""
2016-01-02 03:04 tag1 tag2 11zł
2016-01-02 03:05 tag1 tag2 12zł
                """),
                '2016-02': Transactions("""
2016-02-02 03:06 tag1 tag2 13zł
                """),
                '2016-03': Transactions("""
2016-03-02 03:07 tag1 tag2 14zł
                """)
            })
        )


if __name__ == '__main__':
    unittest.main()
