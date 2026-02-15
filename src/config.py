from decouple import config

API_TOKEN = config('API_TOKEN', cast=str)
PG_URI = config('PG_URI', cast=str)