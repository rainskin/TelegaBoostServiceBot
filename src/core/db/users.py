from datetime import datetime
from typing import List
import loader

class Users:

    def __init__(self):
        self.default_datetime_format = '%d-%m-%Y %H:%M'

    @property
    def collection(self):
        if loader.db_users is None:
            raise RuntimeError("Database not initialized. Call await loader.init_db() first.")
        return loader.db_users

    async def register(self, _id: int, username: str | None, name: str, lang: str):
        if not await self.is_new(_id):
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

        await self.collection.insert_one(doc)

    async def is_new(self, _id: int) -> bool:
        doc = await self.collection.find_one({'id': _id})
        return doc is None

    async def get_user_lang(self, user_id: int) -> str | None:
        doc = await self.collection.find_one({'id': user_id}, {'lang': 1})
        return doc.get('lang') if doc else None

    async def switch_lang(self, user_id: int, lang: str):
        current_lang = await self.get_user_lang(user_id)
        if current_lang == lang:
            return
        await self.collection.update_one({'id': user_id}, {'$set': {'lang': lang}})

    async def get_user_platform(self, user_id: int) -> str | None:
        doc = await self.collection.find_one({'id': user_id}, {'platform': 1})
        return doc.get('platform') if doc else None

    # async def add_balance(self, user_id: int, amount: float):
    #     await self.collection.update_one(
    #         {'id': user_id},
    #         {'$inc': {'balance': round(amount, 2)}}
    #     )

    async def add_balance(self, user_id: int, amount: float) -> float:
        """Добавляет баланс и возвращает итоговую сумму после операции"""
        doc = await self.collection.find_one_and_update(
            {'id': user_id},
            {'$inc': {'balance': round(float(amount), 2)}},
            return_document=True  # ВАЖНО: возвращает документ уже с новым балансом
        )
        if doc:
            return round(doc.get('balance', 0.0), 2)
        return 0.0

    async def get_balance(self, user_id: int) -> float:
        doc = await self.collection.find_one({'id': user_id}, {'balance': 1})
        if doc:
            balance = doc.get('balance', 0)
            return round(float(balance), 2)
        return 0.0


    async def update_balance(self, user_id: int, amount: float):
        await self.collection.update_one({'id': user_id}, {'$set': {'balance': amount}})

    async def get_all_active_users_ids(self) -> List[int]:
        # В Motor distinct возвращает корутину, которую нужно await
        return await self.collection.distinct('id', {'is_active': True})

    async def update_user(self, user_id: int, data: dict):
        await self.collection.update_one({'id': user_id}, {'$set': data}, upsert=True)

    async def get_all_users_ids(self) -> List[int]:
        return await self.collection.distinct('id')

    async def set_active_status(self, user_id: int, status: bool):
        await self.collection.update_one({'id': user_id}, {'$set': {'is_active': status}}, upsert=True)

    async def is_inactive_user(self, user_id: int) -> bool:
        doc = await self.collection.find_one({'id': user_id}, {'is_active': 1})
        if not doc:
            return True # Если юзера нет, считаем его неактивным
        return not doc.get('is_active', False)

    async def add_referral(self, user_id: int, referral_id: int):
        await self.collection.update_one(
            {'id': user_id},
            {'$push': {'referrals.referral_list': referral_id}},
            upsert=True
        )

    async def assign_inviter(self, user_id: int, inviter_id: int):
        await self.collection.update_one({'id': user_id}, {'$set': {'invited_by': inviter_id}}, upsert=True)

    async def get_inviter_id(self, user_id: int) -> int | None:
        doc = await self.collection.find_one({'id': user_id}, {'invited_by': 1})
        return doc.get('invited_by') if doc else None

    async def get_all_referrals(self, user_id: int) -> List[int]:
        doc = await self.collection.find_one({'id': user_id}, {'referrals.referral_list': 1})
        if doc and 'referrals' in doc:
            return doc['referrals'].get('referral_list', [])
        return []

    async def increment_referrals_reward(self, user_id: int, reward: float):
        await self.collection.update_one(
            {'id': user_id},
            {'$inc': {'referrals.total_reward': reward}},
            upsert=True
        )

    async def get_referrals_reward(self, user_id: int) -> float | None:
        doc = await self.collection.find_one({'id': user_id}, {'referrals.total_reward': 1})
        if doc and 'referrals' in doc:
            return doc['referrals'].get('total_reward')
        return None


users = Users()
