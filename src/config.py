from decouple import config

API_TOKEN = config('API_TOKEN', cast=str)
PG_URI = config('PG_URI', cast=str)
ADMIN_USERNAME = config('ADMIN_USERNAME', cast=str)
ADMINS = [int(id) for id in config("ADMINS_IDS", cast=str).split(",")]
BOT_USERNAME = config('BOT_USERNAME', cast=str)
SOFT_WIN_LINK = config('SOFT_WIN_LINK', cast=str)
SOFT_LINUX_LINK = config('SOFT_LINUX_LINK', cast=str)
SOFT_MAC_LINK = config('SOFT_MAC_LINK', cast=str)
VIRUS_TOTAL_LINK = config('VIRUS_TOTAL_LINK', cast=str)