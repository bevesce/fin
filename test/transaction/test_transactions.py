import unittest
from finanse import GroupedTransactions
from finanse import Transactions
from finanse import Transaction
from finanse import Money
from finanse import TransactionParseError


class TransactionsTest(unittest.TestCase):
    def test_eq(self):
        self.assertTrue(
            Transactions(
                '2016-01-02 03:04 tag1 tag2 10zł'
            ) == Transactions(
                '2016-01-02 03:04 tag1 tag2 10zł'
            )
        )

    def test_eq_with_different_count(self):
        self.assertFalse(
            Transactions(
                '2016-01-02 t 10zł\n2016-01-02 t 10zł'
            ) == Transactions(
                '2016-01-02 t 10zł'
            )
        )

    def test_eq(self):
        self.assertTrue(
            Transactions(
                '2016-01-02 03:04 tag1 tag2 10zł'
            ) == Transactions(
                '2016-01-02 03:04 tag1 tag2 10zł'
            )
        )

    def test_len(self):
        self.assertEqual(
            len(Transactions("""
2016-01-01 test 10zł
# comment
2016-01-01 test 10zł
        """)), 2)

    def test_get_item(self):
        self.assertEqual(
            Transactions("""
2016-01-01 test 10zł
# comment
2016-01-01 test 10zł
        """)[1], Transaction('2016-01-01 test 10,00 zł'))

    def test_add(self):
        self.assertEqual(
            Transactions('2016-01-01 test 10zł') + Transactions('2016-01-02 test 10zł'),
            Transactions('2016-01-01 test 10zł\n2016-01-02 test 10zł')
        )

    def test_append(self):
        self.assertEqual(
            Transactions('2016-01-01 test 10zł').append(Transaction('2016-01-02 test 10zł')),
            Transactions('2016-01-01 test 10zł\n2016-01-02 test 10zł')
        )

    def test_map(self):
        self.assertEqual(
            Transactions('2016-01-01 test 10zł').map(
                lambda t: Transaction(t.date, t.tags, t.money * 2)
            ),
            Transactions('2016-01-01 test 20zł')
        )

    def test_filter(self):
        self.assertEqual(
            Transactions("""
2016-01-01 test1 10zł
2016-01-01 test2 10zł
        """).filter(lambda t: 'test1' in t.tags),
            Transactions('2016-01-01 test1 10,00 zł')
        )

    def test_filter_with_query(self): pass

    def test_sum(self):
        self.assertEqual(
            Transactions("""
2016-01-01 test1 10zł
2016-01-01 test2 20zł
        """).sum(),
            Money('30zł')
        )

    def test_group(self):
        self.assertEqual(
            Transactions("""
2016-01-01 test1 10zł
2017-01-01 test2 20zł
        """).group(lambda t: t.date.strftime('%Y')),
            GroupedTransactions({
                '2016': Transactions('2016-01-01 test1 10zł'),
                '2017': Transactions('2017-01-01 test2 20zł')
            })
        )

    def test_group_with_query(self): pass

    def test_parse_invalid_transaction(self):
        with self.assertRaises(TransactionParseError) as cm:
            Transactions('x')
        self.assertEqual(str(cm.exception), "can't parse 'x' as date from 'x' at line: 1")


    def test_parse_invalid_transaction_at_second_line(self):
        with self.assertRaises(TransactionParseError) as cm:
            Transactions('2016-01-01 10zł\nx')
        self.assertEqual(str(cm.exception), "can't parse 'x' as date from 'x' at line: 2")


if __name__ == '__main__':
    unittest.main()
