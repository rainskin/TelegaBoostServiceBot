from datetime import datetime
import loader
from core.db import users
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from enums.transaction_type import TransactionType


class Promo:

    def __init__(self):
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    @property
    def collection(self):
        if loader.db is None:
            raise RuntimeError("Database not initialized. Call await loader.init_db() first.")
        return loader.db['promo']

    async def init(self):
        """Асинхронная инициализация промоакций"""
        exists = await self.collection.find_one({'promo_name': 'balance_for_new_users'})
        if not exists:
            await self.add_balance_for_new_users(0.0, 0, True)

    async def add_balance_for_new_users(self, amount_rub: float, total_users: int, completed: bool):
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
        await self.collection.insert_one(doc)

    async def is_completed(self, promo_name: str) -> bool:
        doc = await self.collection.find_one({'promo_name': promo_name})
        return doc.get('completed', False) if doc else True

    async def add_participant(self, promo_name: str, user_id: int):
        doc = await self.collection.find_one({'promo_name': promo_name})
        if not doc:
            return

        total_users = doc.get('total_users', 0)
        remains = doc.get('remains', 0)
        participants = doc.get('participants', [])

        # Проверка, не участвовал ли уже пользователь
        if user_id in participants:
            return

        if 0 < remains <= total_users:
            remains -= 1
            amount = doc.get('amount', 0.0)

            # Обновляем промо в БД
            await self.collection.update_one(
                {'promo_name': promo_name},
                {
                    '$push': {'participants': user_id},
                    '$set': {'remains': remains}
                }
            )

            # Логика начисления баланса
            user_balance = await users.get_balance(user_id)
            transaction_item = TransactionItem(
                user_id=user_id,
                transaction_type=TransactionType.PROMO,
                amount=amount,
                balance_after=round((user_balance + amount), 2),
            )

            # ВАЖНО: transactions.save и users.add_balance должны быть async
            await transactions.save(transaction_item)
            await users.add_balance(user_id, amount)

            # Если места закончились, помечаем как завершенную
            if remains == 0:
                await self.collection.update_one(
                    {'promo_name': promo_name},
                    {'$set': {'completed': True}}
                )


# Экземпляр
promo = Promo()
