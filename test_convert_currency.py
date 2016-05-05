from finanse.convert_currency import convert_currency

zl100ineur = convert_currency(100, 'zł', '€')
print('100 zł = {} €'.format(zl100ineur))

eur100inzl = convert_currency(100, 'EUR', 'PLN')
print('100 € = {} zł'.format(eur100inzl))
print('ok')