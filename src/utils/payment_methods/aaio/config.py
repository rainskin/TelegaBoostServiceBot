import hashlib
from urllib.parse import urlencode
from core.env import env

MERCHANT_ID = env.get('AAIO_MERCHANT_ID')
SECRET_KEY1 = env.get('AAIO_SECRET_KEY1')
API_KEY = env.get('AAIO_API_KEY')



