from datetime import datetime

import loader
from core.db import orders


class Admin:

    def __init__(self):
        self.collection = loader.db['admin']
        self.default_datetime_format = '%d-%m-%Y %H:%M'

    def get_commission_percentage(self, service_id: str):
        doc: dict = self.collection.find_one({'shop_settings': True})
        base_commission = doc['base_commission']
        if service_id in doc['commission_percentage'].keys():
            percentage = doc['commission_percentage'][service_id]
        else:
            percentage = base_commission
        return percentage

    def get_balance_recharge_commission(self):
        doc: dict = self.collection.find_one({'shop_settings': True})
        r = doc.get('balance_recharge_commission')
        return r

    def get_orders_queue(self) -> dict | None:
        doc = self.collection.find_one({'order_queue': True})
        _orders = doc.get('orders')
        if _orders:
            for order_id, order_info in _orders.items():
                self.collection.update_one({'orders_for_execution': True}, {
                    '$set': {f'orders.{order_id}': order_info},
                }, upsert=True)

                self.collection.update_one({'order_queue': True}, {
                    '$unset': {f'orders.{order_id}': ''},
                })

            return _orders

        else:
            return None

    def put_order_to_queue(self, user_id: int, internal_order_id: str, data: dict):
        date = datetime.now().strftime(self.default_datetime_format)
        quantity = data['quantity']
        service_id = data['service_id']
        url = data['url']
        amount_without_commission = data.get('amount_without_commission')
        profit = data['profit']
        total_amount = data['total_amount']
        hot_order = data['hot_order']
        canceling_is_available = data.get('canceling_is_available')

        order_info = {
            'date': date,
            'user_id': user_id,
            'service_id': service_id,
            'url': url,
            'quantity': quantity,
            'amount_without_commission': amount_without_commission,
            'total_amount': total_amount,
            'profit': profit,
            'hot_order': hot_order,
            'canceling_is_available': canceling_is_available
        }
        self.collection.update_one({'order_queue': True}, {'$set': {
            f'orders.{internal_order_id}': order_info
        }}, upsert=True)

        orders.add_not_accepted_order(user_id, internal_order_id, order_info)

    def get_orders_for_execution(self):
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

    def confirm_payment(self, payment_id: str, status: str):
        doc = self.collection.find_one_and_update(
            {'payments_queue': True},
            {
                '$set': {f'payments.{payment_id}.status': status}
            },
            return_document=True
        )
        payment_info = doc['payments'][payment_id]
        payment_info['execution_date'] = datetime.now().strftime(self.default_datetime_format)
        self.collection.update_one(
            {'payments_queue': True},
            {
                '$set': {f'successful_payments.{payment_id}': payment_info},
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

admin = Admin()
