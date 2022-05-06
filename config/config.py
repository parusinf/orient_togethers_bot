import pathlib
from config.token import BOT_TOKEN

BASE_DIR = pathlib.Path(__file__).parent.parent
HELP_IMAGE_PATH = BASE_DIR/'files/protrino-2022-04-16-m35.png'
EXAMPLE_PATH = BASE_DIR/'files/Сплиты-Протвино-2022-04-16-М18-М35.txt'
CERTIFICATE_PATH = BASE_DIR/'cert/api-parusinf-ru.crt'

# Допуск встреч на КП
TOGETHER_SECONDS = 30
TOGETHER_NUMBER = 4

# Webhook
WEBHOOK_HOST = 'https://api.parusinf.ru'
WEBHOOK_PATH = f'/bot{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Web server
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 5003

# Разработчик
DEVELOPER_NAME = 'Павел Никитин'
DEVELOPER_TELEGRAM = '@nikitinpa'
