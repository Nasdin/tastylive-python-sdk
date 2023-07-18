from datetime import datetime
from tastylive import PublicOrdersAPI

api = PublicOrdersAPI(
    Trader('Tom'),
    Trader('Bob The Trader IRA'),
    Trader('Liz & Jenny'),
    DateRange(datetime(2023, 7, 11), datetime(2023, 7, 18)),
    Strategy('Iron Condor'),
    Symbol('QQQ')
)

def filter_func1(order):
    return float(order['probability_of_profit']) > 0.5

def filter_func2(order):
    return order['is_hedge'] is False

public_orders = api.get_public_orders([filter_func1, filter_func2])

