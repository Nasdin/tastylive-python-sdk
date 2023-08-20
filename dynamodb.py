import boto3
import botocore.exceptions
from tastylive import Orders

def create_attribute_if_not_none(attribute_name, transformer, attribute_value):
    if attribute_value is not None:
        return {attribute_name: transformer(attribute_value)}


def insert_orders_into_boto3(orders: List[Orders]):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('tastylive')

    for order in orders:
        # Insert into the table where partition key is order_id and sort key is trader_id
        insertion_list = [
            create_attribute_if_not_none('order_id', int, order.id),
            create_attribute_if_not_none('trader_id', int, order.trader_id),
            create_attribute_if_not_none('expiration', str, order.expiration),
            create_attribute_if_not_none('exp_date', str, order.exp_date),
            create_attribute_if_not_none('order_type', str, order.order_type),
            create_attribute_if_not_none('price', Decimal, order.price),
            create_attribute_if_not_none('strategy', str, order.strategy),
            create_attribute_if_not_none('reason', str, order.reason),
            create_attribute_if_not_none('executed_at', lambda x: datetime.strftime(x, '%Y-%m-%d %H:%M:%S'),order.executed_at ),
            create_attribute_if_not_none('filled_at', lambda x: datetime.strftime(x, '%Y-%m-%d %H:%M:%S'), order.filled_at),
            create_attribute_if_not_none("probability_of_profit", Decimal, order.probability_of_profit),
            create_attribute_if_not_none("return_on_capital", Decimal, order.return_on_capital),
            create_attribute_if_not_none("underlying_price", Decimal, order.underlying_price),
            create_attribute_if_not_none('placed_at', lambda x: datetime.strftime(x, '%Y-%m-%d %H:%M:%S'), order.placed_at),
            create_attribute_if_not_none('extrinsic_value', str, order.extrinsic_value),
            create_attribute_if_not_none('is_earnings_play', str, order.is_earnings_play),
            create_attribute_if_not_none('is_hedge', str, order.is_hedge),
            create_attribute_if_not_none('is_scalp_trade', str, order.is_scalp_trade),
            create_attribute_if_not_none('tos_iv_rank', Decimal, order.tos_iv_rank),
            create_attribute_if_not_none("is_roll", bool, order.is_roll()),
            create_attribute_if_not_none("is_strike_price_change_roll", bool, order.is_strike_price_change_roll()),
            create_attribute_if_not_none("is_expiration_date_change_roll", bool, order.is_expiration_date_change_roll()),
            create_attribute_if_not_none("is_all_call", bool, order.is_all_call()),
            create_attribute_if_not_none("is_all_put", bool, order.is_all_put()),
            create_attribute_if_not_none("trade_age", int, order.trade_age().total_seconds() / (24 * 60 * 60)),

        ]
        item = {}
        for attribute in insertion_list:
            if attribute:
                item.update(attribute)

        item["comments"] = order.comments
        item["order_legs"] = [order_leg.to_dict() for order_leg in order.order_legs]
        item["executed_ts"] = Decimal(time.mktime(order.executed_at.timetuple()))
        print(item)
        try:
            table.put_item(Item=item,
                          ConditionExpression='attribute_not_exists(order_id)')
        except botocore.exceptions.ClientError as e:
            # Ignore the ConditionalCheckFailedException, bubble up
            # other exceptions.
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
