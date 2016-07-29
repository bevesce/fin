# -*- coding: utf-8 -*-
# from ..money import Money
# from ..money import GroupedMoney
from datetime import datetime

from .transaction_parser import parse_transaction
from .transaction_parser import DATE_FORMAT


class Transaction:
    def __init__(self, date, tags=None, money=None):
        if isinstance(date, str):
            date, tags, money = parse_transaction(date)
        self.date = date
        self.tags = tags
        self.money = money

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return (
            self.date == other.date,
            self.tags == other.tags,
            self.money == other.money
        )

    def __neg__(self):
        return Transaction(self.date, self.tags, -self.money)

    def __str__(self):
        return '{} {} {}'.format(
            self.date.strftime(DATE_FORMAT),
            ' '.join(self._str_tag(t) for t in sorted(self.tags)),
            self.money
        )

    def _str_tag(self, tag):
        param = self.tags[tag]
        if param:
            return '{}({})'.format(tag, param)
        return tag

    def convert(self, currency):
        return Transaction(
            self.date,
            self.tags,
            self.money.convert(currency, self.date)
        )
