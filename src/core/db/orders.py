from core.db import users

import loader

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
