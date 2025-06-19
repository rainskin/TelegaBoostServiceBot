from datetime import datetime

import loader
from core.db import users


class Promo:

    def __init__(self):
        self.collection = loader.db['promo']
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'
        self.create_promo_if_not_exists()

    def create_promo_if_not_exists(self):
        if not self.collection.find_one({'promo_name': 'balance_for_new_users'}):
            self.add_balance_for_new_users(0, 0, True)

    def add_balance_for_new_users(self, amount_rub: float, total_users: int, completed: bool):
        current_date = datetime.now().strftime(self.default_datetime_format)
        doc = {
            'promo_name': 'balance_for_new_users',
            'starting': current_date,
            'amount': amount_rub,
            'total_users': total_users,
            'remains': total_users,
            'participants': [],
            'completed': completed
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

            self.collection.update_one({'promo_name': promo_name}, {'$push': {'participants': user_id},
                                                                    '$set': {'remains': remains}})

            users.add_balance(user_id, amount)
        if remains == 0:
            self.collection.update_one({'promo_name': promo_name}, {'$set': {'completed': True}})


promo: Promo = Promo()
