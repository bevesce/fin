import re
from collections import defaultdict

from ..exceptions import MoneyParseError


def parse_money(text):
    def parse_base_unit(base_unit):
        return int(base_unit) * 100

    def parse_subunit(subunit):
        if not subunit:
            return 0
        if len(subunit) == 1:
            subunit += '0'
        return int(subunit)

    def parse_currency(currency):
        return currency.strip()

    def parse_sign(sign):
        if sign:
            return -1
        return 1

    def raise_money_parse(name):
        raise MoneyParseError(
            "can't parse '{}' as {}".format(text, name)
        )

    amounts = create_amounts()
    for amount_text in text.split('+'):
        amount_text = amount_text.strip()
        # digits -> optionally dot or comma (to separate) ->
        # optionally one or two digits -> currency name (not digits)
        match = re.match(r'^(-{0,1})(?:([\d]+)(?:[\.,](\d{1,2}))?)(\D+)$', amount_text)
        if not match:
            raise_money_parse('money')
        # base_unit and subunit - main currency and it's hundredth part
        sign, base_unit, subunit, currency = match.groups()
        amounts[parse_currency(currency)] += parse_sign(sign) * parse_base_unit(base_unit) + parse_subunit(subunit)
    return amounts



def create_amounts(amounts=None):
    if amounts:
        return defaultdict(lambda: 0, amounts)
    return defaultdict(lambda: 0)
