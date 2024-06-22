from datetime import datetime
from typing import List, Dict

import loader


class Users:

    def __init__(self):
        self.collection = loader.users
        self.default_datetime_format = '%d-%m-%Y %H:%M'

    def register(self, _id: int, name: str, lang: str):
        if not self.is_new(_id):
            return

        date = datetime.now().strftime(self.default_datetime_format)

        doc = {
            'id': _id,
            'balance': 0,
            'name': name,
            'lang': lang,
            'registration_date': date,
            'platform': 'tg_bot'
        }

        self.collection.insert_one(doc)

    def is_new(self, _id: int):
        return not self.collection.find_one({'id': _id})

    def get_user_lang(self, user_id: int):
        doc = self.collection.find_one({'id': user_id})
        r = doc['lang']
        return r

    def switch_lang(self, user_id: int, lang: str):
        current_lang = self.get_user_lang(user_id)

        if current_lang == lang:
            return

        self.collection.update_one({'id': user_id}, {'$set': {'lang': lang}})

    def get_user_platform(self, user_id: int):
        return self.collection.find_one({'id': user_id})['platform']

    def add_balance(self, user_id: int, amount: float):
        self.collection.update_one({'id': user_id}, {'$inc': {'balance': amount}})

    def get_balance(self, user_id: int):
        balance: float = self.collection.find_one({'id': user_id})['balance']
        return round(balance, 2)

    def update_balance(self, user_id: int, amount: float):
        self.collection.update_one({'id': user_id}, {'$set': {'balance': amount}})


users = Users()


class Orders:

    def __init__(self):
        self.collection = loader.orders
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    def get_current_orders(self, user_id) -> dict | None:
        doc = self.collection.find_one({'user_id': user_id}, {'current_orders': 1})
        return doc.get('current_orders') if doc else None

    def get_orders_from_archive(self, user_id) -> dict | None:
        doc = self.collection.find_one({'user_id': user_id}, {'orders_archive': 1})
        return doc.get('orders_archive') if doc else None

    def new_order(self, user_id: id, platform: str, order_id: int, order_info: dict):
        order_id = str(order_id)
        if self.is_first_order(user_id):
            doc = {
                'user_id': user_id,
                'platform': platform,
                'current_orders': {order_id: order_info}
            }

            self.collection.insert_one(doc)

        else:
            self.collection.update_one(
                {'user_id': user_id},
                {'$set': {f'current_orders.{order_id}': order_info}},
                upsert=True
            )

    def get_not_accepted_orders(self, user_id: int):
        doc = self.collection.find_one({'user_id': user_id}, {'not_accepted_orders': 1})
        return doc.get('not_accepted_orders') if doc else None

    def add_not_accepted_order(self, user_id: int, order_id: str, order_info: dict):
        self.collection.update_one({'user_id': user_id}, {'$set': {
            f'not_accepted_orders.{order_id}': order_info}},
                                   upsert=True)

    def remove_not_accepted_order(self, user_id: int, order_id):
        self.collection.update_one({'user_id': user_id}, {'$unset': {f'not_accepted_orders.{order_id}': ''}})

    def cancel_order(self, user_id: int, order_id: str, not_accepted_orders=False):
        if not_accepted_orders:
            field_name = 'not_accepted_orders'
        else:
            field_name = 'current_orders'

        doc = self.collection.find_one({'user_id': user_id}, {field_name: 1})
        _order = doc.get('not_accepted_orders')
        _order_info: dict = _order[order_id]
        total_amount = _order_info.get('total_amount')

        self.collection.update_one({'user_id': user_id}, {
            '$unset': {f'{field_name}.{order_id}': ''}
        })
        users.add_balance(user_id, float(total_amount))

    def return_money_for_current_order(self, user_id: int, order_id: str, amount: float):
        # doc = self.collection.find_one({'user_id': user_id}, {'current_orders': 1})
        # _orders = doc.get('current_orders')
        # order_info = _orders.get(order_id)
        # is_money_returned = order_info.get('is_money_returned')
        # if not is_money_returned:
        #     amount = order_info.get('total_amount')
        #     users.add_balance(user_id, amount)
        #     self.collection.update_one({'user_id': user_id}, {
        #         '$set': {f'current_orders.{order_id}: is_money_returned': True}}, upsert=True)

        doc = self.collection.find_one_and_update(
            {'user_id': user_id, f'current_orders.{order_id}.is_money_returned': {'$ne': True}},
            {'$set': {f'current_orders.{order_id}.is_money_returned': True}},
            projection={'current_orders': 1},
            return_document=True
        )

        # Проверить, найден ли документ и обновлен ли он
        if doc:
            order_info = doc.get('current_orders', {}).get(order_id)
            if order_info:
                users.add_balance(user_id, amount)

    def is_first_order(self, user_id):
        r = not self.collection.find_one({'user_id': user_id})
        return r

    def is_order_exist(self, user_id: int, order_id: str, not_accepted_order=False, current_order=False):
        if not_accepted_order:
            doc = self.collection.find_one({'user_id': user_id}, {'not_accepted_orders': 1})
            _orders: dict = doc.get('not_accepted_orders')
            return order_id in _orders.keys()

        if current_order:
            doc = self.collection.find_one({'user_id': user_id}, {'current_orders': 1})
            _orders: dict = doc.get('current_orders')
            return order_id in _orders.keys()

    def get_order_info(self, user_id: int, order_id: str, current_orders=False):
        if current_orders:
            doc = self.collection.find_one({'user_id': user_id}, {'current_orders': 1})
            return doc['current_orders'][order_id]
        else:
            doc = self.collection.find_one({'user_id': user_id}, {'orders_archive': 1})
            return doc['orders_archive'][order_id]

    def move_orders_to_archive(self, user_id: int, order_id: str):
        pipeline = [
            {
                '$set': {
                    'orders_archive': {
                        '$mergeObjects': [
                            {'$ifNull': ['$orders_archive', {}]},
                            {order_id: f"$current_orders.{order_id}"}
                        ]
                    }
                }
            },
            {
                '$unset': [f'current_orders.{order_id}']
            }
        ]

        self.collection.update_one({'user_id': user_id}, pipeline)

    def save_last_order_info(self, user_id: int, data: dict):
        self.collection.update_one({'user_id': user_id}, {"$set": {'last_order_info': data}}, upsert=True)

    def get_last_order_info(self, user_id: int):
        doc = self.collection.find_one({'user_id': user_id}, {'last_order_info': 1})
        return doc.get('last_order_info') if doc else None

    def reset_last_order_info(self, user_id: int):
        self.collection.update_one({'user_id': user_id}, {"$unset": {'last_order_info': ''}})

    def get_last_internal_order(self, user_id: int):
        doc = self.collection.find_one({'user_id': user_id}, {'last_internal_order': 1})
        return doc.get('last_internal_order') if doc else None

    def update_last_internal_order(self, user_id: int, new_order_id: str):
        self.collection.update_one({'user_id': user_id}, {"$set": {'last_internal_order': new_order_id}}, upsert=True)


orders = Orders()


class Promo:

    def __init__(self):
        self.collection = loader.db['promo']
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    def add_balance_for_new_users(self, amount_rub: float, total_users: int):
        current_date = datetime.now().strftime(self.default_datetime_format)
        doc = {
            'promo_name': 'balance_for_new_users',
            'starting': current_date,
            'amount': amount_rub,
            'total_users': total_users,
            'remains': total_users,
            'participants': [],
            'completed': False
        }

        self.collection.insert_one(doc)

    def is_completed(self, promo_name: str):
        return self.collection.find_one({'promo_name': promo_name})['completed']

    def add_participant(self, promo_name: str, user_id: int):
        doc = self.collection.find_one({'promo_name': promo_name})
        total_users = doc['total_users']
        remains = doc['remains']

        if 0 < remains <= total_users:
            remains -= 1
            amount = doc['amount']
            print(f'{amount}, {type(amount)}')

            self.collection.update_one({'promo_name': promo_name}, {'$push': {'participants': user_id},
                                                                    '$set': {'remains': remains}})

            users.add_balance(user_id, amount)
        if remains == 0:
            self.collection.update_one({'promo_name': promo_name}, {'$set': {'completed': True}})


promo = Promo()


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

    def confirm_payment(self, payment_id: str, successful_payment_status: str):
        doc = self.collection.find_one_and_update(
            {'payments_queue': True},
            {
                '$set': {f'payments.{payment_id}.status': successful_payment_status}
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


    def is_not_paid(self, payment_id: str, expected_status: str):
        doc = self.collection.find_one({'payments_queue': True}, {'payments': 1})
        payments = doc.get('payments')
        payment = payments.get(payment_id)
        payment_status = payment.get('status')
        return payment_status != expected_status

    def get_payment_info(self, payment_id: str):
        doc = self.collection.find_one({'payments_queue': True}, {'payments': 1})
        payment_info = doc['payments'][payment_id]

        return payment_info


admin = Admin()
