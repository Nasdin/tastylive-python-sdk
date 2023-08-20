import urllib.parse
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
import requests

"Version 1"


@dataclass
class OrderLeg:
    id: int
    symbol: str
    action: str
    quantity: str
    asset_type: str
    leg_price: Optional[str]
    underlying_symbol: str
    expiration_date: str
    strike_price: str
    call_or_put: str
    open_close: str

    def __post_init__(self):
        self.quantity: Decimal = Decimal(self.quantity) if self.quantity else None
        self.leg_price = Decimal(self.leg_price) if self.leg_price else None
        self.expiration_date: datetime = datetime.strptime(self.expiration_date, "%Y-%m-%d") if self.expiration_date else None
        self.strike_price: Decimal = Decimal(self.strike_price) if self.strike_price else None

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

    def to_dict(self) -> dict:
        d = asdict(self)
        a = {k: v for k, v in d.items() if v is not None}
        a["expiration_date"] = datetime.strftime(self.expiration_date, '%Y-%m-%d %H:%M:%S') if self.expiration_date else ""
        a["is_open"] = self.is_open()
        a["is_close"] = self.is_close()
        a["is_call"] = self.is_call()
        a["is_put"] = self.is_put()

        return a


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
    order_legs: List[dict]
    comments: List[str]

    def __post_init__(self):
        self.price: Decimal = Decimal(self.price)
        self.executed_at: datetime = datetime.strptime(self.executed_at, '%Y-%m-%dT%H:%M:%SZ')
        self.filled_at: datetime = datetime.strptime(self.filled_at, '%Y-%m-%dT%H:%M:%SZ')
        self.probability_of_profit: Decimal = Decimal(self.probability_of_profit) if self.probability_of_profit else None
        self.return_on_capital: Decimal = Decimal(self.return_on_capital) if self.return_on_capital else None
        self.underlying_price: Decimal = Decimal(self.underlying_price) if self.underlying_price else None
        self.placed_at: datetime = datetime.strptime(self.placed_at, '%Y-%m-%dT%H:%M:%SZ')
        self.extrinsic_value: Decimal = Decimal(self.extrinsic_value) if self.extrinsic_value else None
        self.tos_iv_rank: Decimal = Decimal(self.tos_iv_rank) if self.tos_iv_rank else None
        self.order_legs: List[OrderLeg] = [OrderLeg(
            id=order_leg["id"],
            symbol=order_leg["symbol"],
            action=order_leg["action"],
            quantity=order_leg["quantity"],
            asset_type=order_leg["asset_type"],
            leg_price=order_leg["leg_price"],
            underlying_symbol=order_leg["underlying_symbol"],
            expiration_date=order_leg["expiration_date"],
            strike_price=order_leg["strike_price"],
            call_or_put=order_leg["call_or_put"],
            open_close=order_leg["open_close"]
        ) for order_leg in self.order_legs]

    def is_roll(self) -> bool:
        actions = [leg.action for leg in self.order_legs]
        return ("selltoopen" in actions and "buytoclose" in actions)

    def is_strike_price_change_roll(self) -> bool:
        if not self.is_roll():
            return False
        strike_prices = set(leg.strike_price for leg in self.order_legs)
        return len(strike_prices) > 1

    def is_expiration_date_change_roll(self) -> bool:
        if not self.is_roll():
            return False
        expiration_dates = set(leg.expiration_date for leg in self.order_legs)
        return len(expiration_dates) > 1

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
        current_time = datetime.now()
        return current_time - self.placed_at


class PublicOrders:
    def __init__(self, orders_data, filter_funcs=None):
        if filter_funcs is None:
            self.public_orders = [Orders(
                id=order["id"],
                expiration=order["expiration"],
                exp_date=order["exp_date"],
                order_type=order["order_type"],
                price=order["price"],
                price_string=order["price_string"],
                strategy=order["strategy"],
                reason=order["reason"],
                executed_at=order["executed_at"],
                filled_at=order["filled_at"],
                probability_of_profit=order["probability_of_profit"],
                return_on_capital=order["return_on_capital"],
                underlying_price=order["underlying_price"],
                underlying_price_string=order["underlying_price_string"],
                placed_at=order["placed_at"],
                trader_id=order["trader_id"],
                extrinsic_value=order["extrinsic_value"],
                is_earnings_play=order["is_earnings_play"],
                is_hedge=order["is_hedge"],
                is_scalp_trade=order["is_scalp_trade"],
                tos_iv_rank=order["tos_iv_rank"],
                order_legs=order["order_legs"],
                comments=order["comments"]
            )
                for order in orders_data['public_orders']]
        else:
            self.public_orders = [
                Orders(
                    id=order["id"],
                    expiration=order["expiration"],
                    exp_date=order["exp_date"],
                    order_type=order["order_type"],
                    price=order["price"],
                    price_string=order["price_string"],
                    strategy=order["strategy"],
                    reason=order["reason"],
                    executed_at=order["executed_at"],
                    filled_at=order["filled_at"],
                    probability_of_profit=order["probability_of_profit"],
                    return_on_capital=order["return_on_capital"],
                    underlying_price=order["underlying_price"],
                    underlying_price_string=order["underlying_price_string"],
                    placed_at=order["placed_at"],
                    trader_id=order["trader_id"],
                    extrinsic_value=order["extrinsic_value"],
                    is_earnings_play=order["is_earnings_play"],
                    is_hedge=order["is_hedge"],
                    is_scalp_trade=order["is_scalp_trade"],
                    tos_iv_rank=order["tos_iv_rank"],
                    order_legs=order["order_legs"],
                    comments=order["comments"]
                )
                for order in orders_data['public_orders']
                if all(filter_func(order) for filter_func in filter_funcs)
            ]

    def __repr__(self):
        return str(self.public_orders)


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
        super().__init__(from_date.isoformat(), 'attrs%5Bdate_range%5D%5Bfrom%5D=', to_date.isoformat(),
                         'attrs%5Bdate_range%5D%5Bto%5D=')


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


class Symbol(Filter):
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
