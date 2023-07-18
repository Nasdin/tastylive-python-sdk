import urllib.parse
import typing
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional


@dataclass_json
@dataclass
class OrderLeg:
    id: int
    symbol: str
    action: str
    quantity: str
    asset_type: str
    leg_price: Optional[str]
    leg_price_string: Optional[str]
    underlying_symbol: str
    expiration_date: str
    strike_price: str
    call_or_put: str
    open_close: str

    def __post_init__(self):
        self.quantity = float(self.quantity)
        self.leg_price = float(self.leg_price) if self.leg_price else None
        self.expiration_date = datetime.strptime(self.expiration_date, "%Y-%m-%d")
        self.strike_price = float(self.strike_price)

    def is_open(self) -> bool:
        return self.open_close == 'O'

    def is_close(self) -> bool:
        return self.open_close == 'C'

    def has_days_to_expiration_less_than_or_equal_to(self, days: int) -> bool:
        today = datetime.now().date()
        expiration = self.expiration_date.date()
        days_to_expiration = (expiration - today).days
        return days_to_expiration <= days

    def has_days_to_expiration_greater_than_or_equal_to(self, days: int) -> bool:
        today = datetime.now().date()
        expiration = self.expiration_date.date()
        days_to_expiration = (expiration - today).days
        return days_to_expiration >= days

    def is_call(self) -> bool:
        return self.call_or_put == 'C'

    def is_put(self) -> bool:
        return self.call_or_put == 'P'

    def trade_age(self) -> timedelta:
        placed_at = datetime.fromisoformat(self.placed_at)
        current_time = datetime.now()
        return current_time - placed_at

@dataclass_json
@dataclass
class Orders:
    id: int
    expiration: str
    exp_date: Optional[str]
    order_type: str
    price: str
    price_string: str
    strategy: str
    reason: Optional[str]
    executed_at: str
    filled_at: str
    probability_of_profit: str
    return_on_capital: Optional[str]
    underlying_price: str
    underlying_price_string: str
    placed_at: str
    trader_id: int
    extrinsic_value: Optional[str]
    is_earnings_play: Optional[str]
    is_hedge: bool
    is_scalp_trade: Optional[str]
    tos_iv_rank: str
    order_legs: List[OrderLeg]
    comments: List[str]

    def __post_init__(self):
        self.price = float(self.price)
        self.executed_at = datetime.fromisoformat(self.executed_at)
        self.filled_at = datetime.fromisoformat(self.filled_at)
        self.probability_of_profit = float(self.probability_of_profit)
        self.return_on_capital = float(self.return_on_capital) if self.return_on_capital else None
        self.underlying_price = float(self.underlying_price)
        self.placed_at = datetime.fromisoformat(self.placed_at)
        self.extrinsic_value = float(self.extrinsic_value) if self.extrinsic_value else None
        self.tos_iv_rank = float(self.tos_iv_rank)

    def has_days_to_expiration_less_than_or_equal_to(self, days: int) -> bool:
        return all(
            leg.has_days_to_expiration_less_than_or_equal_to(days)
            for leg in self.order_legs
        )

    def has_days_to_expiration_greater_than_or_equal_to(self, days: int) -> bool:
        return all(
            leg.has_days_to_expiration_greater_than_or_equal_to(days)
            for leg in self.order_legs
        )

    def is_all_call(self) -> bool:
        return all(leg.is_call() for leg in self.order_legs)

    def is_all_put(self) -> bool:
        return all(leg.is_put() for leg in self.order_legs)

    def trade_age(self) -> timedelta:
        placed_at = datetime.fromisoformat(self.placed_at)
        current_time = datetime.now()
        return current_time - placed_at

class PublicOrders:
    def __init__(self, orders_data, filter_funcs=None):
        if filter_funcs is None:
            self.public_orders = [Orders.from_dict(order) for order in orders_data['public_orders']]
        else:
            self.public_orders = [
                Orders.from_dict(order)
                for order in orders_data['public_orders']
                if all(filter_func(order) for filter_func in filter_funcs)
            ]


class Filter:
    def __init__(self, value, prefix, value2=None, prefix2=None):
        self.value = value
        self.prefix = prefix
        self.value2 = value2
        self.prefix2 = prefix2

    def get_query_param(self):
        param = self.prefix + urllib.parse.quote_plus(self.value)
        if self.value2 is not None:
            param += '&' + self.prefix2 + urllib.parse.quote_plus(self.value2)
        return param


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
        super().__init__(from_date.isoformat(), 'attrs%5Bdate_range%5D%5Bfrom%5D=', to_date.isoformat(), 'attrs%5Bdate_range%5D%5Bto%5D=')


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

    def get_public_orders(self, filter_funcs=None):
        url = self.construct_url()
        response = requests.get(url)
        response.raise_for_status()
        return PublicOrders(response.json(), filter_funcs)
