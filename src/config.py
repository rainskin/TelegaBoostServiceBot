from core.env import env

DEBUG = env.get_bool('DEBUG')
BOT_TOKEN = env.get('BOT_TOKEN') if not DEBUG else env.get('TEST_BOT_TOKEN')

BOT_URL = env.get('BOT_URL')

MONGO_URL = env.get('MONGO_URL')
MONGO_DB_NAME = env.get('MONGO_DB_NAME') if not DEBUG else env.get('TEST_MONGO_DB_NAME')

API_TOKEN = env.get('API_TOKEN')
BASE_URL = env.get('BASE_URL')

TG_STARS_API_KEY = env.get('TG_STARS_API_KEY')
TG_STARS_API_BASE_URL = env.get('TG_STARS_API_BASE_URL')

ADMIN_ID = env.get_int('ADMIN_ID')
SUPPORT_BOT_URL = env.get('SUPPORT_BOT_URL')

COINGECKO_API_KEY = env.get('COINGECKO_API_KEY')