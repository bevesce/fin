# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

try:
    from mpltools import style
    style.use('ggplot')
except:
    pass

try:
    import matplotlib.pyplot as plt
except:
    pass

from .money import Money


def plot_split(
    path,
    left_transactions, right_transactions, in_currency,
    left_color, right_color
):
    left_amount = left_transactions.sum().amount(in_currency)
    right_amount = right_transactions.sum().amount(in_currency)
    total = left_amount + right_amount
    plt.figure(figsize=(10, 1))
    plt.yticks([])
    plt.xticks([0, total / 2, total])
    plt.bar(
        left=0, height=1, width=left_amount, bottom=0,
        color=left_color
    )
    plt.bar(
        left=left_amount, height=1, width=right_amount, bottom=0,
        color=right_color
    )
    plt.savefig(path, bbox_inches='tight')


def plot_progress(
    path,
    values, goals, in_currency,
    value_color, goal_color
):
    value = values.sum().amount(in_currency)
    goal = goals.sum().amount(in_currency)
    plt.figure(figsize=(10, 1))
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
    line_color, average_line_color,
    plus_marker_color=None, minus_marker_color=None
):
    groups = transactions.group('year-month').sum()
    months = list(_months_range(transactions))
    sums = [groups.get(m).amount(in_currency) for m in months]
    avgs = list(_calculate_moving_yearly_averages(sums))
    xticks = list(range(0, len(months)))

    fig, ax = plt.subplots(figsize=(12, 4))

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
    start = min(dates)
    end = datetime.now()
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


def monthly_average(transactions):
    months = transactions.group('year-month')
    return months.sum().sum() / len(list(_months_range(transactions)))
