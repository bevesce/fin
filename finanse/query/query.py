import datetime

from ..money import Money
from .parse_date import parse_date


def query(text):
    from .query_parser import parse_query
    return parse_query(text)


class Binary:
    def __init__(self, token, left, right):
        self.type = 'binary'
        self.operator = token.value
        self.left = left
        self.right = right

    def __call__(self, transaction):
        if self.operator == 'and':
            return self.left(transaction) and self.right(transaction)
        elif self.operator == 'or':
            return self.left(transaction) or self.right(transaction)
        else:
            return self.relation(transaction)

    def relation(self, transaction):
        left_side, right_side = self.calculate_sides(transaction)
        if left_side is None and right_side is None:
            return False
        if self.operator == '<':
            return left_side < right_side
        elif self.operator == '<=':
            return left_side <= right_side
        elif self.operator == '=':
            return left_side == right_side
        elif self.operator == '!=':
            return left_side != right_side
        elif self.operator == '>=':
            return left_side >= right_side
        elif self.operator == '>':
            return left_side > right_side
        elif self.operator == '^=':
            return left_side.startswith(right_side)
        elif self.operator == '*=':
            return right_side in left_side
        elif self.operator == '$=':
            return left_side.endswith(right_side)

    def calculate_sides(self, transaction):
        left_side = None
        right_side = None
        if self.left.type == 'keyword' and self.left.value == 'date':
            left_side = transaction.date
            right_side = parse_date(self.right.value)
        elif self.left.type == 'keyword' and self.left.value == 'money':
            left_side = transaction.money
            right_side = Money(self.right.value)
        elif self.left.type == 'keyword' and self.left.value == 'currency':
            left_side = ''.join(transaction.money.currencies())
            right_side = self.right.value
        elif self.left.type == 'tag':
            left_side = transaction.tags.get(self.left.value, '')
            right_side = self.right.value
        return left_side, right_side

    def __str__(self):
        return '({} {} {})'.format(self.left, self.operator, self.right)


class Unary:
    def __init__(self, token, right):
        self.type = 'unary'
        self.operator = token.value
        self.right = right

    def __call__(self, transaction):
        if self.operator == 'not':
            return not self.right(transaction)

    def __str__(self):
        return '({} {})'.format(self.operator, self.right)


class Atom:
    def __init__(self, token):
        self.type = token.type
        self.value = token.value.lower()

    def __call__(self, transaction):
        if self.type == 'tag':
            return self.value in (
                t.lower() for t in transaction.tags
            )

    def __str__(self):
        return self.value
