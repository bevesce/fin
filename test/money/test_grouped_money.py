import unittest
from finanse import GroupedMoney
from finanse import Money


class GroupedMoneyTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(
            GroupedMoney({'test': Money('10zł')}),
            GroupedMoney({'test': Money('10zł')})
        )

    def test_get_item(self):
        self.assertEqual(
            GroupedMoney({'test': Money('10zł')})['test'],
            Money('10zł')
        )

    def test_str(self):
        self.assertEqual(
            str(GroupedMoney({
                'test1': Money('10zł'),
                'test2': Money('20zł'),
            })),
            """test1: 10,00 zł
test2: 20,00 zł"""
        )

    def test_len(self):
        self.assertEqual(
            len(GroupedMoney({
                'test1': Money('10zł'),
                'test2': Money('20zł'),
            })),
            2
        )

    def test_iter(self):
        self.assertEqual(
            list(GroupedMoney({
               'test1': Money('10zł'),
               'test2': Money('20zł'),
            })),
            ['test1', 'test2']
        )

    def test_map(self):
        self.assertEqual(
            GroupedMoney({
               'test1': Money('10zł'),
               'test2': Money('20zł'),
            }).map(lambda t: t * 2),
            GroupedMoney({
               'test1': Money('20zł'),
               'test2': Money('40zł'),
            })
        )

    def test_sum(self):
        self.assertEqual(
            GroupedMoney({
               'test1': Money('10zł'),
               'test2': Money('30zł'),
            }).sum(),
            Money('40zł')
        )

    def test_groups(self):
        self.assertEqual(
            GroupedMoney({
               'test1': Money('10zł'),
               'test2': Money('20zł'),
            }).groups(),
            ['test1', 'test2']
        )

    def test_items(self):
        self.assertEqual(
            list(GroupedMoney({
               'test1': Money('10zł'),
               'test2': Money('20zł'),
            }).items()),
            [
                ('test1', Money('10zł')),
                ('test2', Money('20zł'))
            ]
        )

    def test_transactions(self):
        for m in (
            GroupedMoney({
               'test1': Money('10zł'),
               'test2': Money('20zł'),
            }).money()
        ):
            self.assertTrue(m in [Money('10zł'), Money('20zł')])

    def test_add(self):
        g1 = GroupedMoney({
            '1': Money('1zł'),
            '2': Money('2zł')
        })
        g2 = GroupedMoney({
            '2': Money('2zł'),
            '3': Money('3zł')
        })
        self.assertEqual(
            g1 + g2,
            GroupedMoney({
                '1': Money('1zł'),
                '2': Money('4zł'),
                '3': Money('3zł')
            })
        )

    def test_sub(self):
        g1 = GroupedMoney({
            '1': Money('1zł'),
            '2': Money('2zł')
        })
        g2 = GroupedMoney({
            '2': Money('2zł'),
            '3': Money('3zł')
        })
        self.assertEqual(
            g1 - g2,
            GroupedMoney({
                '1': Money('1zł'),
                '2': Money('0zł'),
                '3': Money('-3zł')
            })
        )

if __name__ == '__main__':
    unittest.main()
