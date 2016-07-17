from finanse import raport
from finanse import Transactions
from finanse import Transaction

t1 = Transactions("""2016-01-01 test1 10zł
2016-02-01 test1 20zł
2016-03-01 test1 50zł
2016-04-01 test1 50zł""")
t2 = Transactions("""2016-01-01 test2 10zł
2016-02-01 test2 50zł
2016-03-01 test2 20zł
2016-04-01 test2 30zł""")

raport.plot_split(
    'test/plots/split.png',
    t1, t2, 'zł',
    'red', 'green'
)


raport.plot_progress(
    'test/plots/progress.png',
    t1, t2, 'zł',
    'red', 'green'
)


raport.plot_months(
    'test/plots/months0.png',
    t1, 'zł',
    'black', 'blue',
    'green', 'red'
)


raport.plot_months(
    'test/plots/months1.png',
    t1 - t2, 'zł',
    'black', 'blue',
    'green', 'red'
)

print(raport.monthly_average(t1))
