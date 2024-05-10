import pymongo
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, MONGO_URL, MONGO_DB_NAME

dp = Dispatcher()
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(BOT_TOKEN, default=default)

db_client = pymongo.MongoClient(MONGO_URL)
db = db_client[MONGO_DB_NAME]

