from datetime import datetime

import loader
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus


class MainOrdersQueue:

    def __init__(self):
        self.collection = loader.db['unpaid_orders']
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    def save(self, order_item: OrderItem):
        order_item.creation_date = datetime.now().strftime(self.default_datetime_format)
        order_item.updated_at = order_item.creation_date
        print(order_item.dict())
        self.collection.update_one({'internal_order_id': order_item.internal_order_id}, {
            '$set': order_item.dict()
        }, upsert=True)

    def update(self, order_item: OrderItem):
        order_item.updated_at = datetime.now().strftime(self.default_datetime_format)
        self.collection.update_one({'internal_order_id': order_item.internal_order_id}, {
            '$set': order_item.dict()
        }, upsert=True)

    def get(self, internal_order_id: str) -> OrderItem | None:
        data: dict = self.collection.find_one({'internal_order_id': internal_order_id})
        if data:
            data.pop('_id')
            return OrderItem(**data)
        return None

    def delete(self, internal_order_id: str):
        if not self.deleted(internal_order_id):
            self.collection.update_one({'internal_order_id': internal_order_id}, {
                '$set': {
                    'deleted': True,
                    'updated_at': datetime.now().strftime(self.default_datetime_format)}})

    def deleted(self, internal_order_id: str) -> bool:
        return self.collection.find_one({'internal_order_id': internal_order_id}).get('deleted', False)

    def get_status(self, internal_order_id: str) -> OrderStatus:
        status = self.collection.find_one({'internal_order_id': internal_order_id}).get('order_status', 'unpaid')
        return OrderStatus(status)

    def get_paid_orders(self) -> list[OrderItem]:
        paid_orders = []
        cursor = self.collection.find({'order_status': OrderStatus.PAID.value})
        for data in cursor:
            data.pop('_id')
            paid_orders.append(OrderItem(**data))
        return paid_orders


orders_queue = MainOrdersQueue()
