# -*- coding: utf-8 -*-
from collections import defaultdict
import requests


ratios = defaultdict(dict)
currencies_symbols = {
    '€': 'EUR', '$': 'USD', 'zł': 'PLN'
}
_url_template = "http://www.google.com/finance/converter?a={amount}&from={from_currency}&to={to_currency}"


def convert_currency(amount, from_currency, to_currency):
    if amount == 0:
        return 0
    from_currency = _normalize_currency_name(from_currency)
    to_currency = _normalize_currency_name(to_currency)
    if from_currency == to_currency:
        return amount
    if not _ratio_is_cached(from_currency, to_currency):
        _download_ratio(from_currency, to_currency)
    return amount * ratios[from_currency][to_currency]


def _normalize_currency_name(currency):
    return currencies_symbols.get(currency, currency).upper()


def _ratio_is_cached(from_currency, to_currency):
    return (
        from_currency in ratios and
        to_currency in ratios[from_currency]
    )


def _download_ratio(from_currency, to_currency):
    url = _make_url(from_currency, to_currency)
    result_html = requests.get(url).text
    ratio = _parse_result_html(result_html)
    ratios[from_currency][to_currency] = ratio


def _make_url(from_currency, to_currency):
    return _url_template.format(
        amount=1,
        from_currency=from_currency,
        to_currency=to_currency,
    )


def _parse_result_html(html):
    try:
        return float(
            str(html).split("<span class=bld>")[1].split(" ")[0]
        )
    except Exception:
        raise Exception('conversion error - cannot parse html')
