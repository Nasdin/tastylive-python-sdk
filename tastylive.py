import urllib.parse
import typing

class OrderLeg:
    def __init__(self, order_leg_data):
        self.id = order_leg_data['id']
        self.symbol = order_leg_data['symbol']
        self.action = order_leg_data['action']
        self.quantity = order_leg_data['quantity']
        self.asset_type = order_leg_data['asset_type']
        self.leg_price = order_leg_data['leg_price']
        self.leg_price_string = order_leg_data['leg_price_string']
        self.underlying_symbol = order_leg_data['underlying_symbol']
        self.expiration_date = order_leg_data['expiration_date']
        self.strike_price = order_leg_data['strike_price']
        self.call_or_put = order_leg_data['call_or_put']
        self.open_close = order_leg_data['open_close']

class Orders:
    def __init__(self, order_data):
        self.id = order_data['id']
        self.expiration = order_data['expiration']
        self.exp_date = order_data['exp_date']
        self.order_type = order_data['order_type']
        self.price = order_data['price']
        self.price_string = order_data['price_string']
        self.strategy = order_data['strategy']
        self.reason = order_data['reason']
        self.executed_at = order_data['executed_at']
        self.filled_at = order_data['filled_at']
        self.probability_of_profit = order_data['probability_of_profit']
        self.return_on_capital = order_data['return_on_capital']
        self.underlying_price = order_data['underlying_price']
        self.underlying_price_string = order_data['underlying_price_string']
        self.placed_at = order_data['placed_at']
        self.trader_id = order_data['trader_id']
        self.extrinsic_value = order_data['extrinsic_value']
        self.is_earnings_play = order_data['is_earnings_play']
        self.is_hedge = order_data['is_hedge']
        self.is_scalp_trade = order_data['is_scalp_trade']
        self.tos_iv_rank = order_data['tos_iv_rank']
        self.order_legs = [OrderLeg(leg) for leg in order_data['order_legs']]
        self.comments = order_data['comments']

class PublicOrders:
    def __init__(self, orders_data):
        self.public_orders = [Orders(order) for order in orders_data['public_orders']]


class Filter:
    def __init__(self, value, prefix):
        self.value = value
        self.prefix = prefix

    def get_query_param(self):
        return self.prefix + urllib.parse.quote_plus(self.value)


class StringFilter(Filter):
    SUPPORTED_VALUES = []

    def __init__(self, value, prefix):
        if not self.is_supported(value):
            raise ValueError(f'Unsupported value: {value}. Supported values are: {self.SUPPORTED_VALUES}')
        super().__init__(self.get_correct_case(value), prefix)

    @classmethod
    def is_supported(cls, value):
        return value.lower() in (v.lower() for v in cls.SUPPORTED_VALUES)

    @classmethod
    def get_correct_case(cls, value):
        matches = [v for v in cls.SUPPORTED_VALUES if v.lower() == value.lower()]
        return matches[0] if matches else None


class Trader(StringFilter):
    SUPPORTED_VALUES = [
        'Tom',
        'Bob The Trader IRA',
        'Liz & Jenny',
        'Tony MX',
        'Nick Battista',
        'Mike',
        'Jim Schultz',
        'Kristi',
        'Jessica',
        'Dr. Data',
        'Lindsay',
        'Jermal',
        'Shark-Jeev',
        'Errol',
        'Johnny',
        'Michael',
        'Josh',
        'Fauzia',
        'Katie',
        'Kai',
        'Tom C'
    ]

    def __init__(self, name):
        super().__init__(name, 'traders%5B%5D=')


class DateRange(Filter):
    def __init__(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date

    def get_query_param(self):
        from_date_str = urllib.parse.quote_plus(self.from_date.isoformat())
        to_date_str = urllib.parse.quote_plus(self.to_date.isoformat())
        return f'attrs%5Bdate_range%5D%5Bfrom%5D={from_date_str}&attrs%5Bdate_range%5D%5Bto%5D={to_date_str}'

class Strategy(StringFilter):
    SUPPORTED_VALUES = [
        'Option',
        'Vertical',
        'Strangle',
        'Future',
        'Iron Condor',
        'Butterfly',
        'Straddle',
        'Calendar',
        'Custom',
        'Covered Stock',
        'Jade Lizard',
        'Stock'
    ]

    def __init__(self, strategy):
        super().__init__(strategy, 'strategy=')


class Symbol(StringFilter):
    def __init__(self, symbol):
        super().__init__(symbol, 'underlying_symbols%5B%5D=')


class PublicOrdersAPI:
    BASE_URL = 'https://follow.tastylive.com/api/public_orders?'

    def __init__(self, *filters):
        self.query_params = [filter_.get_query_param() for filter_ in filters]

    def add_query_param(self, param):
        self.query_params.append(param)

    def construct_url(self):
        return self.BASE_URL + '&'.join(self.query_params)

    def get_public_orders(self):
        url = self.construct_url()
        # Here is where you would normally send a GET request to the URL.
        # But in this AI environment, we're just going to return the URL.
        return url
