# -*- coding: utf-8 -*-
import re
from collections import defaultdict

from .convert_currency import convert_currency
KNOWN_CURRENCIES = ('€', 'zł', '$')


class Money:
    convert_currency = convert_currency

    def __init__(self, amounts=None):
        """
        amounts: defaultdict { currency : amount of this currency }
            amount of given currency should be in hundredth parts
            for example in cents for euro or in groszes for złoty
        """
        if isinstance(amounts, str):
            self._amounts = self._parse(amounts)
        else:
            self._amounts = amounts or self._create_amounts()

    @classmethod
    def _parse(cls, text):
        try:
            amounts = cls._create_amounts()
            for amount_text in text.split('+'):
                amount_text = amount_text.strip()
                # numbers then optionally dot or comma (to separate) and then one or two numbers
                groups = re.match(r'(?:([\d]+)(?:[\.,](\d{1,2}))?)(\D+)', amount_text).groups()
                # euros and cents are examples - main currency and it's hundredth part
                euros, cents, currency = groups
                euros = int(euros) * 100
                if cents and len(cents) == 1:
                    cents += '0'
                cents = int(cents or 0)
                amount = euros + cents
                currency = currency.strip()
                if currency not in KNOWN_CURRENCIES:
                    print('unknown currency!:', currency, 'in:', text)
                amounts[currency] += amount
            return amounts
        except:
            raise Exception("can't parse money")

    @staticmethod
    def _create_amounts():
        return defaultdict(lambda: 0)

    def __add__(self, other):
        amounts = self._create_amounts()
        for currency in self._amounts:
            amounts[currency] = amounts[currency] + self._amounts[currency]
        for currency in other._amounts:
            amounts[currency] = amounts[currency] + other._amounts[currency]
        return Money(amounts)

    def __sub__(self, other):
        amounts = self._create_amounts()
        for currency in self._amounts:
            amounts[currency] = amounts[currency] + self._amounts[currency]
        for currency in other._amounts:
            amounts[currency] = amounts[currency] - other._amounts[currency]
        return Money(amounts)

    def __truediv__(self, divider):
        amounts = self._create_amounts()
        for currency in self._amounts:
            amounts[currency] = int(self._amounts[currency] / divider)
        return Money(amounts)

    def __mul__(self, multiplayer):
        amounts = self._create_amounts()
        for currency in self._amounts:
            amounts[currency] = int(self._amounts[currency] * multiplayer)
        return Money(amounts)

    def __str__(self):
        return self()

    def __repr__(self):
        return self()

    def __eq__(self, other):
        return self() == other()

    def __call__(self, currency=None):
        """Return text represenation of money"""
        if not self._amounts:
            return '0'
        if currency:
            return self._formated_amount_converted_to_one_currency(currency)
        return self._formated_amounts_in_many_currencies()

    def _formated_amount_converted_to_one_currency(self, currency):
        return self._format(
            self._calculate_total_amount_converted_to_one_currency(currency),
            currency
        )

    def _formated_amounts_in_many_currencies(self):
        return ' + '.join(
            self._formated_amount_of_given_currency(currency)
            for currency in self.currencies()
        )

    def _formated_amount_of_given_currency(self, currency):
        return self._format(
            self._amounts[currency],
            currency
        )

    @staticmethod
    def _format(amount, currency):
        MONEY_FORMAT = '{0},{1:02d} {2}'
        return MONEY_FORMAT.format(
            amount // 100,
            amount % 100,
            currency
        )

    def _calculate_total_amount_converted_to_one_currency(self, currency):
        amount = 0
        for from_currency, amount_in_currency in self._amounts.items():
            amount += int(Money.convert_currency(
                amount_in_currency, from_currency, currency
            ))
        return amount

    def amount(self, currency):
        return self._calculate_total_amount_converted_to_one_currency(currency) / 100

    def currencies(self):
        return sorted(self._amounts.keys())


class CategorizedMoney:
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
        for category, amount in self.items():
            result[category] += amount
        for category, amount in other.items():
            result[category] += amount
        return CategorizedMoney(dict(result))

    def __sub__(self, other):
        result = defaultdict(Money)
        for category, amount in self.items():
            result[category] += amount
        for category, amount in other.items():
            result[category] -= amount
        return CategorizedMoney(dict(result))

    def __eq__(self, other):
        if set(self.categories) != set(other.categories):
            return False
        for category in self.categories:
            if self[category] != other[category]:
                return False
        return True

    def __str__(self):
        return '\n'.join(
            '- {} = {}'.format(k, v) for k, v in self.items()
        )

    def __getitem__(self, category):
        return self._categories.get(category, Money())

    def __len__(self):
        return len(self._categories)

    def categories(self):
        return sorted(self._categories.keys())

    def amounts(self):
        return self._categories.values()

    def sum(self):
        return sum(self.amounts(), Money())

    def items(self):
        for category in self.categories():
            yield category, self[category]
