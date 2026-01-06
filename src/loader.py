import motor.motor_asyncio
import pymongo
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, MONGO_URL, MONGO_DB_NAME

motor_client = None
db = None
db_users = None
db_orders = None

async def init_db():
    global motor_client, db, db_users, db_orders

    # Создаем клиент ВНУТРИ цикла событий
    motor_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = motor_client[MONGO_DB_NAME]

    # Инициализируем ссылки на коллекции
    db_users = db['users']
    db_orders = db['orders']


dp: Dispatcher = Dispatcher()

default = DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True)
bot: Bot = Bot(BOT_TOKEN, default=default)

