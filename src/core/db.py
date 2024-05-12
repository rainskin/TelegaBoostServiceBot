from datetime import datetime

import loader


class Users():

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
