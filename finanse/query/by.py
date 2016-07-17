def by(text):
    if text == 'year':
        return lambda t: t.date.strftime('%Y')
    if text == 'month':
        return lambda t: t.date.strftime('%m')
    if text == 'day':
        return lambda t: t.date.strftime('%d')
    if text == 'weekday':
        return lambda t: t.date.strftime('%A')
    if text == 'year-month':
        return lambda t: t.date.strftime('%Y-%m')
    if text == 'year-month-day':
        return lambda t: t.date.strftime('%Y-%m-%d')
    if text == 'date':
        return lambda t: t.date.strftime('%Y-%m-%d')
    return lambda t: t.tags.get(text, '')
