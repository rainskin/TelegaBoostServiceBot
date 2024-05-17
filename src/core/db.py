from datetime import datetime

import loader


class Users:

    def __init__(self):
        self.collection = loader.users
        self.default_datetime_format = '%d-%m-%Y %H:%M'

    async def register(self, _id: int, name: str, lang: str):
        if not self.is_new(_id):
            return

        date = datetime.now().strftime(self.default_datetime_format)

        doc = {
            'id': _id,
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

    def switch_lang(self, _id: int, lang: str):
        current_lang = self.get_user_lang(_id)

        if current_lang == lang:
            return

        self.collection.update_one({'id': _id}, {'$set': {'lang': lang}})


users = Users()


class Orders:

    def __init__(self):
        self.collection = loader.orders
        self.default_datetime_format = '%d-%m-%Y %H:%M:%S'

    def get_current_orders(self, user_id) -> list | None:
        doc = self.collection.find_one({'id': user_id}, {'current_orders': 1})
        return doc.get('current_orders') if doc else None

    def new_order(self, user_id: id, platform: str, order_id: int, order_info: dict):

        if self.is_first_order(user_id):
            doc = {
                'id': user_id,
                'platform': platform,
                'order_info': order_info,
                'current_orders': [order_id]
            }

            self.collection.insert_one(doc)

        else:
            self.collection.update_one(
                {'id': user_id},
                {'$push': {'current_orders': order_id}},
                upsert=True)

    def cancel_order(self, order_id: int):
        pass

    def is_first_order(self, user_id):
        r = not self.collection.find_one({'id': user_id})
        print(f'is first order {r}')
        return r


orders = Orders()
