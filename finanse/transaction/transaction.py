# -*- coding: utf-8 -*-
from .money import Money
from .money import GroupedMoney
from datetime import datetime
from collections import defaultdict

DATE_FORMAT = '%Y-%m-%d %H:%M'
COMMENT_IDICATOR = '#'


class Transaction:
    def __init__(self, date, tags=None, amount=None):
        if tags is None:
            date, tags, amount = self._parse(date)
        self.date = date
        self.tags = tuple(tags)
        self.amount = amount

    @staticmethod
    def _parse(text):
        split = text.lower().split(' ')
        try:
            date = datetime.strptime(
                split[0] + ' ' + split[1],
                DATE_FORMAT
            )
        except:
            print('error:', text)
            import sys
            sys.exit(0)
        try:
            amount = Money(split[-1])
            tags = split[2:-1]
        except:
            amount = Money(split[-2] + split[-1])
            tags = split[2:-2]
        return date, tags, amount

    def __eq__(self, other):
        return (
            self.date == other.date,
            self.tags == other.tags,
            self.amount == other.amount
        )

    def __str__(self):
        return '{} {} {}'.format(
            self.date.strftime(DATE_FORMAT),
            ' '.join(sorted(self.tags)),
            self.amount
        )


class Transactions:
    def __init__(self, transactions=None):
        if isinstance(transactions, str):
            self._transactions = self._parse(transactions)
        else:
            self._transactions = transactions or []

    @staticmethod
    def _parse(text):
        return [
            Transaction(t)
            for t in text.strip().split('\n')
            if t and not t.startswith(COMMENT_IDICATOR)
        ]

    def __len__(self):
        return len(self._transactions)

    def __getitem__(self, index):
        return self._transactions[index]

    def __eq__(self, other):
        return set(
            str(t) for t in self._transactions
        ) == set(
            str(t) for t in other._transactions
        )

    def __str__(self):
        return '\n'.join(str(t) for t in self)

    def __add__(self, other):
        return Transactions(self._transactions + other._transactions)

    def map(self, f):
        return Transactions([f(t) for t in self])

    def filter(self, f):
        return Transactions([t for t in self if f(t)])

    def sum(self):
        return sum((t.amount for t in self), Money())

    def group(self, key):
        groups = defaultdict(list)
        for transaction in self:
            groups[key(transaction)].append(transaction)
        return GroupedTransactions({
            k: Transactions(v)
            for k, v in groups.items()
        })


class GroupedTransactions:
    def __init__(self, groups):
        self._groups = groups

    def __len__(self):
        return len(self._groups)

    def __getitem__(self, key):
        return self._groups[key]

    def __str__(self):
        return '\n'.join(
            str(k) + '\n' + str(v)
            for k, v in self._groups.items()
        )

    def __eq__(self, other):
        if set(self._groups.keys()) != set(self._groups.keys()):
            return False
        for k in self._groups.keys():
            if self[k] != other[k]:
                return False
        return True


    def map(self, f):
        return GroupedTransactions({
            k: v.map(f) for k, v in self._groups.items()
        })

    def filter(self, f):
        return GroupedTransactions({
            k: v.filter(f) for k, v in self._groups.items()
        })

    def sum(self):
        return GroupedMoney({
            k: v.sum() for k, v in self._groups.items()
        })

    def groups(self):
        return self._groups.keys()


def parse_tags(text):
    class Tokenizer:
        def __init__(self, text):
            self._text = text
            self._tokens = ['']
            self._parenthesis_counter = 0

        def run(self):
            for c in self._text:
                if c == ' ' or c == '\t':
                    self._tokenize_whitespace(c)
                elif c == '(':
                    self._tokenize_left_parenthesis(c)
                elif c == ')':
                    self._tokenize_right_parenthesis(c)
                else:
                    self._tokenize_character(c)
            return [t for t in self._tokens if t]

        def add_token(self, token):
            self._tokens.append(token)

        def is_top_level(self):
            return self._parenthesis_counter == 0

        def _tokenize_whitespace(self, c):
            if self.is_top_level():
                self.add_token('')
            else:
                self._tokenize_character(c)

        def _tokenize_left_parenthesis(self, c):
            if self.is_top_level():
                self.add_token('(')
                self.add_token('')
            else:
                self._tokenize_character(c)
            self._parenthesis_counter += 1

        def _tokenize_right_parenthesis(self, c):
            self._parenthesis_counter -= 1
            if self.is_top_level():
                self.add_token(')')
                self.add_token('')
            else:
                self._tokenize_character(c)

        def _tokenize_character(self, c):
            self._tokens[-1] += c


    def parse(text):
        tokens = Tokenizer(text).run()
        tags = {}
        def pick():
            return tokens[0]

        def pop():
            return tokens.pop(0)

        def is_eof():
            return not tokens

        def is_word():
            return pick() != '(' and pick() != ')'

        def parse_tags():
            if not is_eof():
                parse_tag()
                parse_tags()

        def parse_tag():
            tag = pop_word()
            parameter = None
            if not is_eof() and pick() == '(':
                parameter = pop_parameter()
            tags[tag] = parameter

        def pop_word():
            if is_word():
                return pop()
            raise Exception(text)

        def pop_parameter():
            pop()
            word = pop_word()
            pop_close()
            return word

        def pop_close():
            if pick() == ')':
                return pop()
            raise Exception(text)

        parse_tags()
        return tags



    return parse(text)
    # return parse(Tokenizer(text).run())
    # tokens = tokenize(text)
    # if text:
        # return {t: None for t in text.split(' ')}
    # return {}
