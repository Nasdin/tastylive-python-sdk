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
url = api.get_public_orders()
print(url)
