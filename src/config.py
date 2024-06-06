from core.env import env

BOT_TOKEN = env.get('BOT_TOKEN')

MONGO_URL = env.get('MONGO_URL')
MONGO_DB_NAME = env.get('MONGO_DB_NAME')

API_TOKEN = env.get('API_TOKEN')
BASE_URL = env.get('BASE_URL')

ADMIN_ID = env.get_int('ADMIN_ID')
SUPPORT_BOT_URL = env.get('SUPPORT_BOT_URL')