# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

from fin import TagsHierarchy
from fin import Transactions


class TagsHierarchyTest(unittest.TestCase):
    def test_tags_hierarchy_level_0_1(self):
        self.assertEqual(
            str(TagsHierarchy(tag='test')),
            '- test'
        )

    def test_tags_hierarchy_level_0_2(self):
        self.assertEqual(
            str(TagsHierarchy(tag='*test*')),
            '- *test*'
        )

    def test_tags_hierarchy_level_1_1(self):
        self.assertEqual(
            str(TagsHierarchy(tag='test', children=[TagsHierarchy(tag='test1'), TagsHierarchy(tag='test2')])),
            '- test\n' +
            '    - test1\n' +
            '    - test2'
        )

    def test_tags_hierarchy_level_0_parse(self):
        hierarchy_str = """
- a
- b
"""
        self.assertEqual(
            str(TagsHierarchy(hierarchy_str)),
            hierarchy_str.strip()
        )

    def test_tags_hierarchy_level_1_parse(self):
        hierarchy_str = """
- a
    - c
    - *d*
- b
"""
        self.assertEqual(
            str(TagsHierarchy(hierarchy_str)),
            hierarchy_str.strip()
        )

    def test_get_exclusive_tags(self):
        hierarchy_str = """
- a
    - c
    - *d*
        - e
- *b*
- f
"""
        th = TagsHierarchy(hierarchy_str)
        self.assertEqual(
            th.get_exclusive_tags(),
            set(('a', 'c', 'e', 'f'))
        )

    def test_format_transactions_1(self):
        hierarchy_str = """
- a
"""
        transactions = Transactions("""
2018-07-12 a 10€
""")
        output = '- a: 10,00 €'
        self.assertEqual(TagsHierarchy(hierarchy_str).format_transactions(transactions), output)

    def test_format_transactions_2(self):
        hierarchy_str = """
- a
- b
"""
        transactions = Transactions("""
2018-07-12 a 10€\n2018-07-12 b 20€
""")
        output = """- a: 10,00 €
- b: 20,00 €"""
        self.assertEqual(TagsHierarchy(hierarchy_str).format_transactions(transactions), output)

    def test_format_transactions_3(self):
        hierarchy_str = """
- a
    - c
- b
"""
        transactions = Transactions("""
2018-07-12 a 10€
2018-07-12 b 20€
2018-07-12 c 30€
""")
        output = """- a: 40,00 €
    - c: 30,00 €
- b: 20,00 €"""
        self.assertEqual(TagsHierarchy(hierarchy_str).format_transactions(transactions), output)

    def test_format_transactions_3(self):
        hierarchy_str = """
- a
    - *c*
- b
    - *c*
"""
        transactions = Transactions("""
2018-07-12 a 10€
2018-07-12 a c 1€
2018-07-12 b c 2€
""")
        expected = """- a: 11,00 €
    - *c*: 1,00 €
    - ?: 10,00 €
- b: 2,00 €
    - *c*: 2,00 €"""
        output = TagsHierarchy(hierarchy_str).format_transactions(transactions)
        self.assertEqual(expected, output)

    def test_format_transactions_4(self):
        hierarchy_str = """
- a
"""
        transactions = Transactions("""
2018-07-12 a 10€
2018-07-12 x 20€
""")
        expected = """- a: 10,00 €
- ?: 20,00 €"""
        output = TagsHierarchy(hierarchy_str).format_transactions(transactions)
        self.assertEqual(output, expected)

    def test_format_transactions_5(self):
        hierarchy_str = """
- a
    - c
- b
"""
        transactions = Transactions("""
2018-07-12 a 10€
2018-07-12 a c 20€
2018-07-12 b 13€
2018-07-12 x 31€
""")
        expected = """- a: 30,00 €
    - c: 20,00 €
    - ?: 10,00 €
- b: 13,00 €
- ?: 31,00 €"""
        output = TagsHierarchy(hierarchy_str).format_transactions(transactions)
        self.assertEqual(output, expected)

    def test_format_transactions_6(self):
        hierarchy_str = """
- a
    - c
- b
"""
        transactions = Transactions("""
2018-07-12 a 10€
2018-07-12 c 20€
2018-07-12 b 13€
2018-07-12 x 31€
""")
        expected = """- a: 30,00 €
    - c: 20,00 €
    - ?: 10,00 €
- b: 13,00 €
- ?: 31,00 €"""
        output = TagsHierarchy(hierarchy_str).format_transactions(transactions)
        self.assertEqual(output, expected)

    def test_apply_transactions_1(self):
        hierarchy_str = """
- a
    - c
- b
"""
        transactions = Transactions("""
2018-07-12 a 10€
2018-07-12 c 20€
2018-07-12 b 13€
2018-07-12 x 31€
""")
        applied = TagsHierarchy(hierarchy_str).apply(transactions)
        self.assertEqual(str(applied.children[0].transactions), """2018-07-12 a 10,00 €
2018-07-12 c 20,00 €""")
        self.assertEqual(str(applied.children[1].transactions), """2018-07-12 b 13,00 €""")
        self.assertEqual(str(applied.children[2].transactions), """2018-07-12 x 31,00 €""")
        self.assertEqual(str(applied.children[0].children[0].transactions), """2018-07-12 c 20,00 €""")

if __name__ == '__main__':
    unittest.main()
