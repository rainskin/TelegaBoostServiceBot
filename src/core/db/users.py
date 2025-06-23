from datetime import datetime
from typing import List

import loader


class Users:

    def __init__(self):
        self.collection = loader.db_users
        self.default_datetime_format = '%d-%m-%Y %H:%M'

    def register(self, _id: int, username: str | None, name: str, lang: str):
        if not self.is_new(_id):
            return

        date = datetime.now().strftime(self.default_datetime_format)

        doc = {
            'id': _id,
            'balance': 0,
            'username': username,
            'name': name,
            'lang': lang,
            'registration_date': date,
            'platform': 'tg_bot',
            'is_active': True,
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

    def get_all_active_users_ids(self):
        return self.collection.distinct('id', {'is_active': True})

    def update_user(self, user_id: int, data: dict):
        self.collection.update_one({'id': user_id}, {'$set': data}, upsert=True)

    def get_all_users_ids(self):
        return self.collection.distinct('id')

    def set_active_status(self, user_id: int, status: bool):
        self.collection.update_one({'id': user_id}, {'$set': {'is_active': status}}, upsert=True)

    def is_inactive_user(self, user_id: int):
        doc = self.collection.find_one({'id': user_id}, {'is_active': 1})
        return not doc.get('is_active')

    def add_referral(self, user_id: int, referral_id: int):
        self.collection.update_one({'id': user_id}, {'$push': {f'referrals.referral_list': referral_id}}, upsert=True)

    def assign_inviter(self, user_id: int, inviter_id: int):
        self.collection.update_one({'id': user_id}, {'$set': {'invited_by': inviter_id}}, upsert=True)

    def get_inviter_id(self, user_id):
        doc = self.collection.find_one({'id': user_id})
        r = doc.get('invited_by')
        return r

    def get_all_referrals(self, user_id: int) -> List[int]:
        doc = self.collection.find_one({'id': user_id}, {f'referrals': 1})
        if doc and 'referrals' in doc:
            return doc['referrals'].get('referral_list')
        return []

    def increment_referrals_reward(self, user_id, reward: float):
        self.collection.update_one({'id': user_id}, {'$inc': {'referrals.total_reward': reward}}, upsert=True)

    def get_referrals_reward(self, user_id):
        doc = self.collection.find_one({'id': user_id}, {f'referrals': 1})
        if doc and 'referrals' in doc:
            return doc['referrals'].get('total_reward')
        return None


users = Users()
