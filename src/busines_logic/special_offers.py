from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.localisation.texts import buttons


class SpecialOffer:
    callback_template = 'special_offer_'

    def __init__(self, name_and_info: dict, uniq_tag: str):
        self.lang = 'en'
        self.name_and_info = name_and_info
        self.name = self.name_and_info['name'][self.lang]
        self.info = self.name_and_info['info'][self.lang]
        self.tag = uniq_tag
        self.price = 0
        self.currency = 'RUB'
        self.amount_without_commission = 0
        self.profit = 0
        self.services_and_amount: dict = {}
        self.canceling_is_available = False

    def get_keyboard(self):
        builder = InlineKeyboardBuilder()
        builder.button(text=self.name, callback_data=f'{self.callback_template}{self.tag}')

        return builder

    def translate_name_and_info(self, lang):
        self.name = self.name_and_info['name'][lang]
        self.info = self.name_and_info['info'][lang]


offer_viewers_and_subscribers = SpecialOffer(buttons.views_and_subscribers_special_offer, 'views_and_subscribers')
offer_viewers_and_subscribers.services_and_amount = [()]
offer_viewers_and_subscribers.price = 450.00
a = offer_viewers_and_subscribers.price

twenty_boosts_30_days = SpecialOffer(buttons.twenty_boosts_30_days, 'fifteen_boosts')
twenty_boosts_30_days.price = 450
# twenty_boosts_30_days.services_and_amount = {'66': 20, }
twenty_boosts_30_days.services_and_amount = {'67': 1, }
twenty_boosts_30_days.amount_without_commission = 10
twenty_boosts_30_days.profit = twenty_boosts_30_days.price - twenty_boosts_30_days.amount_without_commission


special_offers_list = [
    twenty_boosts_30_days,
]


def get_special_offers_keyboard(lang: str):
    builder = InlineKeyboardBuilder()

    for offer in special_offers_list:
        offer.translate_name_and_info(lang)
        builder.attach(offer.get_keyboard())

    return builder


def get_offer_by_tag(tag: str) -> SpecialOffer:
    for offer in special_offers_list:
        if offer.tag == tag:
            return offer
