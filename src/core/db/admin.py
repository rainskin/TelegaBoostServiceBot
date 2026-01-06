from datetime import datetime
import loader
from core.db import orders
from core.db.models.order_item import OrderItem


class Admin:
    def __init__(self):
        # Мы не присваиваем self.collection здесь через loader.db['admin'],
        # так как loader.db может быть None на момент импорта.
        # Лучше обращаться к нему внутри методов или через свойство.
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    @property
    def collection(self):
        if loader.db is None:
            raise RuntimeError("Database not initialized. Call await loader.init_db() first.")
        return loader.db['admin']

    async def init(self):
        """Инициализация начальных документов в БД"""
        await self.collection.update_one(
            {'orders_for_execution': True},
            {'$setOnInsert': {'orders': {}}},
            upsert=True
        )

        await self.collection.update_one(
            {'recharge_xtr_commissions': True},
            {'$setOnInsert': {
                'recharge_xtr_commissions': True,
                'telegram_star_to_usd_equivalent': 0.0,
                'ton_to_usdt_spot_fee_percent': 0.0,
                'ton_network_fee_percent': 0.0,
                'p2p_premium_percent_from_db': 0.0,
                'info': 'Settings for recharge XTR commissions.'
            }},
            upsert=True
        )

        await self.collection.update_one(
            {'exchange_rates': True},
            {'$setOnInsert': {
                'usdt_to_rub_rate': 0.0,
                'updated_at': datetime.now().strftime(self.default_datetime_format),
                'update_interval_in_seconds': 3600,
                'info': 'Exchange rates settings.'
            }},
            upsert=True
        )

        await self.collection.update_one(
            {'shop_settings': True},
            {'$setOnInsert': {
                'base_commission': 0,
                'commission_percentage': {},
                'balance_recharge_commission': 0,
                'minimal_recharge_amount': 0,
                'referral_deposit_reward_percent': 0,
                'maintenance_mode': False,
                'info': 'Shop settings document.'
            }},
            upsert=True
        )

    async def is_maintenance_mode(self) -> bool:
        doc = await self.collection.find_one({'shop_settings': True})
        return doc.get('maintenance_mode', False) if doc else False

    async def get_exchange_rates(self) -> dict | None:
        return await self.collection.find_one({'exchange_rates': True})

    async def update_exchange_rates(self, usdt_to_rub_rate: float):
        current_datetime = datetime.now().strftime(self.default_datetime_format)
        await self.collection.update_one(
            {'exchange_rates': True},
            {'$set': {
                'usdt_to_rub_rate': usdt_to_rub_rate,
                'updated_at': current_datetime
            }}
        )

    async def get_tg_stars_price_ranges_in_rub(self):
        doc = await self.collection.find_one({'tg_star_per_rub': True}, {"price_ranges": 1})
        if not doc or "price_ranges" not in doc:
            return []
        return [(r["min_stars"], r["price_per_star"]) for r in doc["price_ranges"]]

    async def get_commission_percentage(self, service_id: str):
        doc = await self.collection.find_one({'shop_settings': True})
        if not doc: return 0
        base_commission = doc.get('base_commission', 0)
        commissions = doc.get('commission_percentage', {})
        return commissions.get(service_id, base_commission)

    async def get_minimal_recharge_amount(self):
        doc = await self.collection.find_one({'shop_settings': True})
        return doc.get('minimal_recharge_amount') if doc else 0

    async def get_balance_recharge_commission(self):
        doc = await self.collection.find_one({'shop_settings': True})
        return doc.get('balance_recharge_commission') if doc else 0

    async def get_recharge_xtr_commissions(self):
        return await self.collection.find_one({'recharge_xtr_commissions': True})

    async def get_orders_queue(self) -> dict | None:
        doc = await self.collection.find_one({'order_queue': True})
        return doc.get('orders') if doc else None

    async def move_orders_to_execution_queue(self, _orders: dict):
        for order_id, order_info in _orders.items():
            await self.collection.update_one(
                {'orders_for_execution': True},
                {'$set': {f'orders.{order_id}': order_info}},
                upsert=True
            )
            await self.collection.update_one(
                {'order_queue': True},
                {'$unset': {f'orders.{order_id}': ''}}
            )

    async def put_order_to_queue(self, order_item: OrderItem):
        order_item.updated_at = datetime.now().strftime(self.default_datetime_format)
        internal_order_id = order_item.internal_order_id
        await self.collection.update_one({'order_queue': True}, {'$set': {
            f'orders.{internal_order_id}': order_item.dict()
        }}, upsert=True)

        await orders.add_not_accepted_order(order_item)

    async def get_orders_for_execution(self) -> dict | None:
        doc = await self.collection.find_one({'orders_for_execution': True})
        return doc.get('orders') if doc else None

    # check check check
    async def is_order_in_execution_queue(self, order_id: str):
        doc = await self.collection.find_one({'orders_for_execution': True}, {'orders': 1})
        if not doc: return False
        _orders = doc.get('orders', {})
        return order_id in _orders

    async def remove_order_from_main_queue(self, order_id: str):
        await self.collection.update_one({'order_queue': True}, {'$unset': {f'orders.{order_id}': ""}})

    async def remove_order_from_execution_queue(self, order_id: str):
        await self.collection.update_one({'orders_for_execution': True}, {'$unset': {f'orders.{order_id}': ""}})

    async def save_payment(self, payment_id: str, payment_info: dict):
        current_date = datetime.now().strftime(self.default_datetime_format)
        payment_info['date'] = current_date
        await self.collection.update_one({'payments_queue': True}, {
            '$set': {f'payments.{payment_id}': payment_info}
        }, upsert=True)

    async def update_payment_status(self, payment_id: str, status: str, telegram_payment_charge_id: str = None):
        update_fields = {f'payments.{payment_id}.status': status}
        if telegram_payment_charge_id is not None:
            update_fields[f'payments.{payment_id}.telegram_payment_charge_id'] = telegram_payment_charge_id
        await self.collection.update_one({'payments_queue': True}, {'$set': update_fields})

    async def move_to_successful_payments(self, payment_id: str):
        doc = await self.collection.find_one({'payments_queue': True}, {'payments': 1})
        if not doc or payment_id not in doc.get('payments', {}): return
        payment_info = doc['payments'][payment_id]
        payment_info['status_update_date'] = datetime.now().strftime(self.default_datetime_format)
        await self.collection.update_one(
            {'payments_queue': True},
            {
                '$set': {f'successful_payments.{payment_id}': payment_info},
                '$unset': {f'payments.{payment_id}': ""}
            }
        )

    async def move_to_failed_payments(self, payment_id: str):
        doc = await self.collection.find_one({'payments_queue': True}, {'payments': 1})
        if not doc or payment_id not in doc.get('payments', {}): return
        payment_info = doc['payments'][payment_id]
        payment_info['status_update_date'] = datetime.now().strftime(self.default_datetime_format)
        await self.collection.update_one(
            {'payments_queue': True},
            {
                '$set': {f'failed_payments.{payment_id}': payment_info},
                '$unset': {f'payments.{payment_id}': ""}
            }
        )

    async def is_not_paid(self, payment_id: str):
        doc = await self.collection.find_one({'payments_queue': True}, {'payments': 1})
        if not doc:
            return True

        payment = doc.get('payments', {}).get(payment_id)

        if not payment:
            return True

        status = payment.get('status')
        return status not in ['success', 'hold']

    async def get_payment_info(self, payment_id: str):
        doc = await self.collection.find_one({'payments_queue': True}, {'payments': 1})
        return doc.get('payments', {}).get(payment_id) if doc else None

    async def get_referral_deposit_reward(self):
        doc = await self.collection.find_one({'shop_settings': True})
        return doc.get('referral_deposit_reward_percent', 0) if doc else 0


# Экземпляр класса
admin = Admin()
from typing import Optional, Any


def build_payment_info(
        user_id: int,
        amount_rub: float,
        currency: str,
        amount_original: Optional[float] = None,
        payment_url: Optional[str] = None,
        balance_recharge: bool = False,
        payment_status: Optional[str] = None,
) -> dict[str, Any]:
    """
    Формирует словарь с информацией о платеже для сохранения в MongoDB.
    Это синхронная функция, так как она только подготавливает данные.
    """

    payment_purpose = 'balance_recharge' if balance_recharge else None

    return {
        'user_id': user_id,
        'amount_rub': round(amount_rub, 2),  # Округляем для красоты в БД
        'amount_original': round(amount_original, 2) if amount_original else None,
        'currency': currency,
        'payment_url': payment_url,
        'payment_purpose': payment_purpose,
        'status': payment_status,
    }
