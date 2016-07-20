import datetime

from .query_parser import parse_query
from ..money import Money


def query(text):
    ast = parse_query(text)
    return _create_query(ast)


def _create_query(ast):
    if ast.type == 'binary':
        return _create_binary(ast.operator, ast.left, ast.right)
    if ast.type == 'unary':
        return _create_unary(ast.operator, ast.expression)
    return _create_atomic(ast.type, ast.value)


def _create_binary(operator, left, right):
    if operator in ('and', 'or'):
        return _create_logical(operator, left, right)
    else:
        return _create_operation(operator, left, right)


def _create_operation(operator, left, right):
    if left.type == 'keyword' and left.value == 'date':
        l = lambda t: t.date
        r = _parse_date(right.value)
    if left.type == 'keyword' and left.value == 'money':
        l = lambda t: t.money
        r = Money(right.value)
    if left.type == 'keyword' and left.value == 'currency':
        l = lambda t: ''.join(t.money.currencies())
        r = right.value
    if left.type == 'tag':
        l = lambda t: t.tags.get(left.value, '')
        r = right.value
    if operator == '<':
        return lambda t: l(t) < r
    if operator == '<=':
        return lambda t: l(t) <= r
    if operator == '=':
        return lambda t: l(t) == r
    if operator == '!=':
        return lambda t: l(t) != r
    if operator == '>=':
        return lambda t: l(t) >= r
    if operator == '>':
        return lambda t: l(t) > r
    if operator == '^=':
        return lambda t: l(t).startswith(r)
    if operator == '*=':
        return lambda t: r in l(t)
    if operator == '$=':
        return lambda t: l(t).endswith(r)


def _create_logical(operator, left, right):
    l = _create_query(left)
    r = _create_query(right)
    if operator == 'and':
        return lambda t: l(t) and r(t)
    if operator == 'or':
        return lambda t: l(t) or r(t)


def _create_unary(operator, right):
    r = _create_query(right)
    if operator == 'not':
        return lambda t: not r(t)


def _create_atomic(type, value):
    if type == 'tag':
        return lambda t: value.lower() in (t.lower() for t in t.tags)


def _parse_date(date_string):
    if date_string == 'today':
        today = datetime.date.today()
        return datetime.datetime(today.year, today.month, today.day)
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')
