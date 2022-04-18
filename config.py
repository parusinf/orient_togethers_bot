from secret_config import BOT_TOKEN

HELP_IMAGE_PATH = '/home/pa/data/devel/python/orient_togethers_bot/files/protrino-2022-04-16-m35.png'
EXAMPLE_PATH = '/home/pa/data/devel/python/orient_togethers_bot/files/Сплиты-Протвино-2022-04-16-М18-М35.txt'

# Допуск встреч на КП
TOGETHER_SECONDS = 30
TOGETHER_NUMBER = 4

# MongoDB
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# Webhook
WEBHOOK_HOST = 'https://api.parusinf.ru'
WEBHOOK_PATH = f'/bot{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Web server
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 5002

# Разработчик
DEVELOPER_NAME = 'Павел Никитин'
DEVELOPER_TELEGRAM = '@nikitinpa'
