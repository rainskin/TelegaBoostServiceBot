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

    def get_user_lang(self, _id: int):
        return self.collection.find_one({'id': _id})['lang']

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
        return balance

    def update_balance(self, user_id: int, amount: float):
        self.collection.update_one({'id': user_id}, {'$set': {'balance': amount}})


users = Users()


class Orders:

    def __init__(self):
        self.collection = loader.orders
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    def get_current_orders(self, user_id) -> dict | None:
        doc = self.collection.find_one({'id': user_id}, {'current_orders': 1})
        return doc.get('current_orders') if doc else None

    def new_order(self, user_id: id, platform: str, order_id: int, order_info: dict):
        order_id = str(order_id)
        if self.is_first_order(user_id):
            doc = {
                'id': user_id,
                'platform': platform,
                'current_orders': {order_id: order_info}
            }

            self.collection.insert_one(doc)

        else:
            self.collection.update_one(
                {'id': user_id},
                {'$set': {f'current_orders.{order_id}': order_info}},
                upsert=True
            )

    def cancel_order(self, order_id: int):
        pass

    def is_first_order(self, user_id):
        r = not self.collection.find_one({'id': user_id})
        print(f'is first order {r}')
        return r

    def move_completed_orders_to_archive(self, user_id: int, current_orders: Dict[str, dict]):

        for order_id, order_info in current_orders.items():
            status = order_info['status']
            if status != 'In progress' and status != 'Canceled':
                self.collection.update_one({'id': user_id},
                                           {'$set': {f'orders_archive.{order_id}': order_info}}, upsert=True)

                self.collection.update_one(
                    {"id": user_id}, {"$unset": {f"current_orders.{order_id}": ""}})


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
