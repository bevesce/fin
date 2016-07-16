# -*- coding: utf-8 -*-
from datetime import datetime


def tagged(*tags):
    return lambda t: all(tag in t.tags for tag in tags)


def in_this_month(transaction):
    return month(transaction.date) == month(datetime.now())


def not_tagged(tag):
    return lambda t: tag not in t.tags


def tagged_with_any(*tags):
    return lambda t: any(tag in t.tags for tag in tags)


def by_month(transaction):
    return month(transaction.date)


def by_year(transaction):
    return str(transaction.date.year)


def month(date):
    return date.strftime('%Y-%m')


def currency(c):
    return lambda t: c in t.amount.currencies()


def in_month(m):
    return lambda t: month(t.date) == m


def after(d):
    return lambda t: t.date >= datetime.strptime(d, '%Y-%m-%d')


def before(d):
    return lambda t: t.date <= datetime.strptime(d, '%Y-%m-%d')
