import pymongo
import motor.motor_asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, MONGO_URL, MONGO_DB_NAME

dp = Dispatcher()
default = DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True)
bot = Bot(BOT_TOKEN, default=default)

db_client = pymongo.MongoClient(MONGO_URL)
db = db_client[MONGO_DB_NAME]
users = db['users']
orders = db['orders']

storage_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

