# -*- coding: utf-8 -*-
from collections import defaultdict
try:
    from urllib import request
    from urllib import error
except ImportError:
    pass
try:
    import requests
except:
    pass
import datetime
import pickle
import json
import atexit


currencies_aliases = {
    '€': 'EUR', '$': 'USD', 'zł': 'PLN'
}


cache = {}
cache_path = None


def setup_cache(path):
    global cache_path
    cache_path = path
    if not cache_path:
        return
    try:
        _load_cache()
    except Exception:
        pass


def _load_cache():
    global cache
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.loads(f.read())


def _save_cache():
    if not cache_path:
        return
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(cache))


atexit.register(_save_cache)


def convert(amount, from_currency, to_currency, date=None):
    rates = _get_rates(from_currency, date)
    from_currency = currencies_aliases.get(from_currency, from_currency)
    to_currency = currencies_aliases.get(to_currency, to_currency)
    if from_currency == to_currency:
        return amount
    try:
        return amount * rates[to_currency]
    except KeyError:
        raise Exception("Currency '{}' is not supported by fixer.io".format(to_currency))


def _get_rates(base, date=None):
    base = currencies_aliases.get(base, base)
    date = date or datetime.date.today()
    date_key = date.strftime('%F')
    try:
        return cache[date_key][base]
    except KeyError:
        rates = _get_fixer_rates(base, date)
        cache.setdefault(date_key, {})[base] = rates
        return rates



def _get_fixer_rates(base, date):
    url = _prepare_fixer_url(base, date)
    try:

        response = requests.get(url)
        response_data = response.json
    except Exception:
        try:
            response = request.urlopen(url)
            response_data = json.loads(response.read().decode('utf-8'))
        except error.HTTPError as e:
            _raise_coldnt_download_rates_exception(base, date, e)
    return response_data['rates']


def _prepare_fixer_url(base, date):
    date = date.strftime('%F') if date else 'latest'
    return 'http://api.fixer.io/{date}?base={base}'.format(
        date=date, base=base
    )


def _raise_coldnt_download_rates_exception(base, date, exception):
    raise Exception(
        "Couldn't download conversion rates for base: '{}' at date: '{}', because: [{}] {}".format(
            base, date, exception.code, json.loads(exception.read().decode('utf-8'))['error']
        )
    )
