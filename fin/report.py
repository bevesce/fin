# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

try:
    import matplotlib.pyplot as plt
    plt.style.use('ggplot')
except:
    pass

from .money import Money


def plot_split(
    path,
    left_transactions, right_transactions, in_currency,
    left_color='green', right_color='blue'
):
    left_amount = left_transactions.sum().amount(in_currency)
    right_amount = right_transactions.sum().amount(in_currency)
    total = left_amount + right_amount
    plt.figure(figsize=(20, 1))
    plt.xlim([0, total])
    plt.yticks([])
    plt.xticks([0, total / 2, total])
    plt.barh(
        left=0, height=1, width=left_amount, bottom=0,
        color=left_color
    )
    plt.barh(
        left=left_amount, height=1, width=right_amount, bottom=0,
        color=right_color
    )
    plt.savefig(path, bbox_inches='tight')


def plot_progress(
    path,
    transactions, goal_transactions, in_currency,
    value_color='blue', goal_color='green'
):
    value = transactions.sum().amount(in_currency)
    goal = goal_transactions.sum().amount(in_currency)
    plt.figure(figsize=(20, 1))
    plt.yticks([])
    plt.xticks([0, 1, value, goal])
    plt.bar(
        left=0, height=1, width=value, bottom=0,
        color=value_color
    )
    plt.bar(
        left=0, height=0.1, width=goal, bottom=0,
        color=goal_color
    )
    plt.savefig(path, bbox_inches='tight')


def plot_months(
    path,
    transactions, in_currency,
    line_color='black', average_line_color='blue',
    plus_marker_color=None, minus_marker_color=None
):
    groups = transactions.group('year-month').sum()
    months = list(_months_range(transactions))
    sums = [groups.get(m).amount(in_currency) for m in months]
    avgs = list(_calculate_moving_yearly_averages(sums))
    xticks = list(range(0, len(months)))

    fig, ax = plt.subplots(figsize=(20, 4))

    ax.set_xticks(xticks)
    ax.set_ylim(min(min(sums) - 10, 0), max(sums) + 10)
    ax.set_xticklabels(months, rotation=90)
    plt.plot(xticks, sums, color=line_color, linestyle='-')
    plt.plot(xticks, avgs, color=average_line_color, linestyle='-')

    on_plus, on_minus = _split_sums_based_on_sign(sums)
    if plus_marker_color:
        plt.plot(*on_plus, color=plus_marker_color, marker='o', linestyle='None')
    if minus_marker_color:
        plt.plot(*on_minus, color=minus_marker_color, marker='o', linestyle='None')

    plt.savefig(path, bbox_inches='tight')


def _months_range(data):
    dates = [t.date for t in data]
    end = datetime.now()
    start = min(dates) if len(dates) > 0 else end
    start_year = start.year
    start_month = start.month
    while start_year != end.year or start_month != end.month:
        yield '{}-{:02d}'.format(start_year, start_month)
        start_month += 1
        if start_month > 12:
            start_month = 1
            start_year += 1
    yield end.strftime('%Y-%m')


def _split_sums_based_on_sign(sums):
    xticks_on_plus = []
    sums_on_plus = []
    xticks_on_minus = []
    sums_on_minus = []
    for x, sum in enumerate(sums):
        if sum > 0:
            xticks_on_plus.append(x)
            sums_on_plus.append(sum)
        else:
            xticks_on_minus.append(x)
            sums_on_minus.append(sum)
    return (xticks_on_plus, sums_on_plus), (xticks_on_minus, sums_on_minus)



def _calculate_moving_yearly_averages(sums):
    for end in range(1, len(sums) + 1):
        start = max(end - 12, 0)
        size = end - start
        yield sum(sums[start:end]) / size


def plot_days(
    path, transactions, in_currency, line_color, least_squares_color=None,
    reference_value=None, reference_color=None
):
    if not transactions:
        return
    xticks = list(_index_dates([t.date for t in transactions]))
    xlabels = [t.date.strftime('%F') for t in transactions]
    values = [transactions.group('date').sum()[k].amount(in_currency) for k in xlabels]

    fig, ax = plt.subplots(figsize=(20, 4))
    ax.set_xticks(xticks)
    min_value = min(values) - 2
    max_value = max(values) + 2
    if reference_value:
        min_value = min(reference_value - 2, min_value)
        max_value = max(reference_value - 2, max_value)
    ax.set_ylim(min_value, max_value)
    ax.set_xticklabels(xlabels, rotation=90)

    plt.plot(xticks, values, color=line_color, linestyle='-')
    if (reference_value):
        plt.plot(xticks, [reference_value] * len(xticks), color=reference_color, linestyle='-')

    if least_squares_color:
        ls_line, _, _ = least_squares(xticks, values)
        if ls_line:
            plt.plot(xticks, ls_line, color=least_squares_color, linestyle='-')

    plt.savefig(path, bbox_inches='tight')



def _days_range(transactions):
    start_date = min(t.date for t in transactions)
    end_date = max(t.date for t in transactions)
    while start_date < end_date:
        yield start_date.strftime('%F')
        start_date += timedelta(days=1)


def _index_dates(dates):
    d = timedelta(days=1)
    start = dates[0]
    end = dates[-1]
    index = 0
    while start <= end:
        if start in dates:
            yield index
        start += d
        index += 1


def least_squares(xs, ys):
    S = len(xs)
    Sx = sum(xs)
    Sy = sum(ys)
    Sxx = sum(x ** 2 for x in xs)
    Syy = sum(y ** 2 for y in ys)
    Sxy = sum(x * y for x, y in zip(xs, ys))
    D = S * Sxx - (Sx) ** 2
    try:
        a = (S * Sxy - Sx * Sy) / D
        b = (Sxx * Sy - Sx * Sxy) / D
        return [a * x + b for x in xs], a, b
    except:
        return None, None, None

def monthly_average(transactions):
    months = transactions.group('year-month')
    return months.sum().sum() / len(list(_months_range(transactions)))
