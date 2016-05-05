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
from .query import by_month


def plot_split_graph(
        path,
        sum1, sum2, in_currency,
        color1, color2
    ):

    pamount = sum1.amount(in_currency)
    aamount = sum2.amount(in_currency)
    total = sum2 + sum1
    plt.figure(figsize=(10, 1))
    plt.yticks([])
    plt.xticks([0, (pamount + aamount) / 2, pamount + aamount])
    plt.bar(
        left=0, height=1, width=pamount, bottom=0,
        color=color1
    )
    plt.bar(
        left=pamount, height=1, width=aamount, bottom=0,
        color=color2
    )
    plt.savefig(
        path,
        bbox_inches='tight'
    )


def plot_monthly_graph(
        path,
        transactions, title,
        color, avg_color,
        plus_marker_color=None, minus_marker_color=None,
        sub_transactions=None
    ):

    filename = 'finanse_' + title + '.png'

    plus_marker_color = plus_marker_color or color
    minus_marker_color = minus_marker_color or color

    months = list(months_range(transactions))
    sums = transactions.group(by_month).sum()

    if sub_transactions:
        sums -= sub_transactions.group(by_month).sum()
    avgs = moving_averages(sums, list(reversed(months)))

    fig, ax = plt.subplots(figsize=(12, 4))
    x = [i for i in range(0, len(months))]
    sums = [sums[m].amount('zł') for m in months]
    avgs = [avgs[m].amount('zł') for m in months]
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=90)
    plt.plot(x, sums, color=color, linestyle='-')
    plt.plot(x, avgs, color=avg_color, linestyle='-')
    plt.ylabel('kwota [zł]')
    plt.xlabel('data')

    xs_green = []
    ys_green = []
    xs_red = []
    ys_red = []
    for i, v in enumerate(sums):
        if v >= 0:
            xs_green.append(i)
            ys_green.append(v)
        else:
            xs_red.append(i)
            ys_red.append(v)
    plt.plot(xs_green, ys_green, color=plus_marker_color, marker='o', linestyle='None')
    plt.plot(xs_red, ys_red, color=minus_marker_color, marker='o', linestyle='None')

    plt.savefig(
        path,
        bbox_inches='tight'
    )

    return filename


def plot_envelopes(
        path,
        envelopes, goals,
        envelopes_color, goal_color, over_goal_color
    ):
    filename = 'finanse_koperty.png'
    to_accumulate = goals - envelopes
    currency = '€'

    N = len(goals)
    plt.figure(figsize=(8, N))
    in_envelopes = [envelopes[c].amount(currency) for c in goals.categories()]
    diff = [to_accumulate[c].amount(currency) for c in goals.categories()]
    overflow = [0 if v > 0 else v for v in diff]
    in_to_accumulate = [0 if v < 0 else v for v in diff]
    ind = [i for i in range(N)] # the x locations for the groups
    width = 0.1 # the width of the bars: can also be len(x) sequence
    p1 = plt.bar(
        left=[0] * N, height=[1] * N, width=in_envelopes, bottom=ind,
        color=envelopes_color
    )
    p2 = plt.bar(
        left=in_envelopes, height=[1] * N, width=in_to_accumulate, bottom=ind,
        color=goal_color
    )
    p3 = plt.bar(
        left=in_envelopes, height=[1] * N, width=overflow, bottom=ind,
        color=over_goal_color
    )
    plt.yticks([i + 0.5 for i in ind], list(goals.categories()))
    plt.savefig(
        path,
        bbox_inches='tight'
    )
    return filename


def months_range(data):
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


def monthly_average(transactions, sub_transactions=None):
    grouped_by_month = transactions.group(by_month)
    sums = grouped_by_month.sum()
    if sub_transactions:
        sub_grouped_by_month = sub_transactions.group(by_month)
        sub_sums = sub_grouped_by_month.sum()
        sums -= sub_sums
    return sum(sums.amounts(), Money()) / len(sums)


def moving_averages(data, keys, size=12):
    averages = defaultdict(Money)
    values = [data[k] for k in keys]
    value = sum(values[:size], Money())
    for i in range(0, len(values)):
        k = keys[i]
        averages[k] = value / min(size, len(values) - i)
        value -= values[i]
        if i + size < len(values):
            value += values[i + size]
    return averages
