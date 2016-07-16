# -*- coding: utf-8 -*-
import re
from collections import defaultdict

from .currency import convert as convert_currency
from .money_parser import parse, create_amounts


class Money:
    convert_currency = convert_currency

    def __init__(self, amounts=None):
        """
        amounts: {currency : amount of this currency}
            amount of given currency should be in hundredth parts
            for example in cents for euro or in groszes for złoty
        """
        if isinstance(amounts, str):
            self._amounts = parse(amounts)
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

    def convert(self, to_currency, date=None):
        total_amount = 0
        for from_currency, amount in self._amounts.items():
            total_amount += Money.convert_currency(amount, from_currency, to_currency, date)
        return Money({to_currency: int(total_amount)})

    @staticmethod
    def _format(amount, currency):
        return '{0},{1:02d} {2}'.format(
            amount // 100,
            amount % 100,
            currency
        )

    def currencies(self):
        return sorted(self._amounts.keys())


class GroupedMoney:
    def __init__(self, categories):
        if isinstance(categories, str):
            categories = self._parse(categories)
        self._categories = categories

    @staticmethod
    def _parse(text):
        result = {}
        for l in text.splitlines():
            if not l:
                continue
            l = l.strip(' -\t')
            title, amount_text = l.split('=')
            title = title.strip()
            amount = Money(amount_text)
            result[title] = amount
        return result

    def __add__(self, other):
        result = defaultdict(Money)
        for group, amount in self.items():
            result[group] += amount
        for group, amount in other.items():
            result[group] += amount
        return GroupedMoney(dict(result))

    def __sub__(self, other):
        result = defaultdict(Money)
        for group, amount in self.items():
            result[group] += amount
        for group, amount in other.items():
            result[group] -= amount
        return GroupedMoney(dict(result))

    def __eq__(self, other):
        if set(self.categories) != set(other.categories):
            return False
        for group in self.categories:
            if self[group] != other[group]:
                return False
        return True

    def __str__(self):
        return '\n'.join(
            '- {} = {}'.format(k, v) for k, v in self.items()
        )

    def __getitem__(self, group):
        return self._categories.get(group, Money())

    def __len__(self):
        return len(self._categories)

    def groups(self):
        return sorted(self._categories.keys())

    def amounts(self):
        return self._categories.values()

    def sum(self):
        return sum(self.amounts(), Money())

    def items(self):
        for group in self.categories():
            yield group, self[group]
