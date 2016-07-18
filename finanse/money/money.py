# -*- coding: utf-8 -*-
import re
from collections import defaultdict

from .currency import convert as convert_currency
from .money_parser import parse_money, create_amounts


class Money:
    def __init__(self, amounts=None):
        """
        amounts: {currency : amount of this currency}
            amount of given currency should be in hundredth parts
            for example in cents for euro or in groszes for złoty
        """
        if isinstance(amounts, str):
            self._amounts = parse_money(amounts)
        else:
            self._amounts = create_amounts(amounts)

    def __add__(self, other):
        amounts = create_amounts()
        for currency in self._amounts:
            amounts[currency] = amounts[currency] + self._amounts[currency]
        for currency in other._amounts:
            amounts[currency] = amounts[currency] + other._amounts[currency]
        return Money(amounts)

    def __sub__(self, other):
        amounts = create_amounts()
        for currency in self._amounts:
            amounts[currency] = amounts[currency] + self._amounts[currency]
        for currency in other._amounts:
            amounts[currency] = amounts[currency] - other._amounts[currency]
        return Money(amounts)

    def __truediv__(self, divider):
        amounts = create_amounts()
        for currency in self._amounts:
            amounts[currency] = int(self._amounts[currency] / divider)
        return Money(amounts)

    def __mul__(self, multiplayer):
        amounts = create_amounts()
        for currency in self._amounts:
            amounts[currency] = int(self._amounts[currency] * multiplayer)
        return Money(amounts)

    def __str__(self):
        return ' + '.join(
            self._formated_amount_of_given_currency(currency)
            for currency in self.currencies()
        )

    def _formated_amount_of_given_currency(self, currency):
        return self._format(
            self._amounts[currency], currency
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return self.get_amount_in_reference_currency(self) < self.get_amount_in_reference_currency(other)

    def __le__(self, other):
        return self.get_amount_in_reference_currency(self) <= self.get_amount_in_reference_currency(other)

    def __neg__(self):
        return Money() - self

    def convert(self, to_currency, date=None):
        total_amount = 0
        for from_currency, amount in self._amounts.items():
            total_amount += convert_currency(amount, from_currency, to_currency, date)
        return Money({to_currency: int(total_amount)})

    @staticmethod
    def _format(amount, currency):
        return '{0},{1:02d} {2}'.format(
            amount // 100,
            amount % 100,
            currency
        )

    @staticmethod
    def get_amount_in_reference_currency(money):
        return money.convert('EUR')._amounts['EUR']

    def currencies(self):
        return sorted(self._amounts.keys())

    def amount(self, currency):
        return self.convert(currency)._amounts[currency] / 100
