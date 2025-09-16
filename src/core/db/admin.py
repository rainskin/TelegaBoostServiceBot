from datetime import datetime

import loader
from core.db import orders
from core.db.models.order_item import OrderItem


class Admin:
    def __init__(self):
        self.collection = loader.db['admin']
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'
        self.init()

    def init(self):

        self.collection.update_one(
            {'orders_for_execution': True},
            {'$setOnInsert': {
                'orders': {},
            }},
            upsert=True
        )

        self.collection.update_one(
            {'recharge_xtr_commissions': True},
            {'$setOnInsert': {
                'recharge_xtr_commissions': True,
                'telegram_star_to_usd_equivalent': 0.0,
                'ton_to_usdt_spot_fee_percent': 0.0,
                'ton_network_fee_percent': 0.0,
                'p2p_premium_percent_from_db': 0.0,
                'info': 'This document contains settings for recharge XTR commissions.'
            }},
            upsert=True
        )

        self.collection.update_one(
            {'exchange_rates': True},
            {'$setOnInsert': {
                'usdt_to_rub_rate': 0.0,
                'updated_at': datetime.now().strftime(self.default_datetime_format),
                'update_interval_in_seconds': 3600,
                'info': 'This document contains exchange rates and update interval settings.'
            }},
            upsert=True
        )

        self.collection.update_one(
            {'shop_settings': True},
            {'$setOnInsert': {
                'base_commission': 0,  # int
                'commission_percentage': {},  # dict with service_id as key and commission percentage as value
                'balance_recharge_commission': 0,  # int
                'minimal_recharge_amount': 0,  # int
                'referral_deposit_reward_percent': 0,  # int
                'maintenance_mode': False,  # bool
                'info': 'This document contains shop settings including commissions and referral rewards.'
            }},
            upsert=True
        )

    def is_maintenance_mode(self) -> bool:
        doc = self.collection.find_one({'shop_settings': True})
        r = doc.get('maintenance_mode', False) if doc else False
        return r

    def get_exchange_rates(self) -> dict | None:
        doc = self.collection.find_one({'exchange_rates': True})
        if doc:
            return doc
        return None

    def update_exchange_rates(self, usdt_to_rub_rate: float):
        current_datetime = datetime.now().strftime(self.default_datetime_format)
        self.collection.update_one(
            {'exchange_rates': True},
            {'$set': {
                'usdt_to_rub_rate': usdt_to_rub_rate,
                'updated_at': current_datetime
            }}
        )

    def get_tg_stars_price_ranges_in_rub(self):
        doc = self.collection.find_one({'tg_star_per_rub': True}, {"price_ranges": 1})
        if not doc or "price_ranges" not in doc:
            return []

        # вернём список списков [[min_stars, price_per_star], ...]
        return [(r["min_stars"], r["price_per_star"]) for r in doc["price_ranges"]]

    def get_commission_percentage(self, service_id: str):
        doc: dict = self.collection.find_one({'shop_settings': True})
        base_commission = doc['base_commission']
        if service_id in doc['commission_percentage'].keys():
            percentage = doc['commission_percentage'][service_id]
        else:
            percentage = base_commission
        return percentage

    def get_minimal_recharge_amount(self):
        doc: dict = self.collection.find_one({'shop_settings': True})
        r = doc.get('minimal_recharge_amount')
        return r

    def get_balance_recharge_commission(self):
        doc: dict = self.collection.find_one({'shop_settings': True})
        r = doc.get('balance_recharge_commission')
        return r

    def get_recharge_xtr_commissions(self):
        return self.collection.find_one({'recharge_xtr_commissions': True})

    def get_orders_queue(self) -> dict | None:
        doc = self.collection.find_one({'order_queue': True})
        return doc.get('orders') if doc and doc.get('orders') else None

    def move_orders_to_execution_queue(self, _orders: dict):
        for order_id, order_info in _orders.items():
            self.collection.update_one(
                {'orders_for_execution': True},
                {'$set': {f'orders.{order_id}': order_info}},
                upsert=True
            )
            self.collection.update_one(
                {'order_queue': True},
                {'$unset': {f'orders.{order_id}': ''}}
            )


    def put_order_to_queue(self, order_item: OrderItem):

        order_item.updated_at = datetime.now().strftime(self.default_datetime_format)
        internal_order_id = order_item.internal_order_id
        self.collection.update_one({'order_queue': True}, {'$set': {
            f'orders.{internal_order_id}': order_item.dict()
        }}, upsert=True)

        orders.add_not_accepted_order(order_item)

    def get_orders_for_execution(self) -> dict | None:
        doc = self.collection.find_one({'orders_for_execution': True})
        _orders = doc['orders']
        return doc.get('orders') if doc else None

    def is_order_in_execution_queue(self, order_id: str):
        doc = self.collection.find_one({'orders_for_execution': True}, {'orders': 1})
        _orders: dict = doc.get('orders')
        return order_id in _orders.keys()

    def remove_order_from_main_queue(self, order_id: str):
        self.collection.update_one({'order_queue': True}, {'$unset': {f'orders.{order_id}': ""}})

    def remove_order_from_execution_queue(self, order_id: str):
        self.collection.update_one({'orders_for_execution': True}, {'$unset': {f'orders.{order_id}': ""}})

    def save_payment(self, payment_id: str, payment_info: dict):
        current_date = datetime.now().strftime(self.default_datetime_format)
        payment_info['date'] = current_date
        self.collection.update_one({'payments_queue': True}, {
            '$set': {f'payments.{payment_id}': payment_info}
        }, upsert=True)

    def update_payment_status(self, payment_id: str, status: str, telegram_payment_charge_id: str = None):
        update_fields = {f'payments.{payment_id}.status': status}
        if telegram_payment_charge_id is not None:
            update_fields[f'payments.{payment_id}.telegram_payment_charge_id'] = telegram_payment_charge_id

        self.collection.update_one(
            {'payments_queue': True},
            {'$set': update_fields}
        )

    def move_to_successful_payments(self, payment_id: str):
        doc = self.collection.find_one({'payments_queue': True}, {'payments': 1})
        payment_info = doc['payments'][payment_id]
        payment_info['status_update_date'] = datetime.now().strftime(self.default_datetime_format)
        self.collection.update_one(
            {'payments_queue': True},
            {
                '$set': {f'successful_payments.{payment_id}': payment_info},
                '$unset': {f'payments.{payment_id}': payment_id}
            }
        )

    def move_to_failed_payments(self, payment_id: str):
        doc = self.collection.find_one({'payments_queue': True}, {'payments': 1})
        payment_info = doc['payments'][payment_id]
        payment_info['status_update_date'] = datetime.now().strftime(self.default_datetime_format)
        self.collection.update_one(
            {'payments_queue': True},
            {
                '$set': {f'failed_payments.{payment_id}': payment_info},
                '$unset': {f'payments.{payment_id}': payment_id}
            }
        )

    def is_not_paid(self, payment_id: str):
        doc = self.collection.find_one({'payments_queue': True}, {'payments': 1})
        payments = doc.get('payments')
        payment = payments.get(payment_id)
        payment_status = payment.get('status')
        return payment_status != 'success' and payment_status != 'hold'

    def get_payment_info(self, payment_id: str):
        doc = self.collection.find_one({'payments_queue': True}, {'payments': 1})
        payment_info = doc['payments'][payment_id]

        return payment_info

    def get_referral_deposit_reward(self):
        doc = self.collection.find_one({'shop_settings': True})
        r = doc.get('referral_deposit_reward_percent')
        return r


admin: Admin = Admin()


def build_payment_info(
        user_id: int,
        amount_rub: float,
        currency: str,
        amount_original: float = None,
        payment_url: str = None,
        balance_recharge: bool = False,
        payment_status: str = None,
):
    payment_purpose = 'balance_recharge' if balance_recharge else None
    return {
        'user_id': user_id,
        'amount_rub': amount_rub,
        'amount_original': amount_original,
        'currency': currency,
        'payment_url': payment_url,
        'payment_purpose': payment_purpose,
        'status': payment_status,
    }
