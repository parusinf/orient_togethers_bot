import logging
from aiogram import Dispatcher
from aiogram.types import InputFile
from config.config import CERTIFICATE_PATH
from pathlib import Path
from aiogram.utils.executor import start_webhook
import config.config as config
from app.orientbot.bot import bot, dp


async def on_startup(_: Dispatcher):
    logging.info(f'Starting webhook connection')
    await bot.set_webhook(
       config.WEBHOOK_URL,
       certificate=InputFile(Path(CERTIFICATE_PATH)),
       drop_pending_updates=True)


async def on_shutdown(_: Dispatcher):
    await bot.set_webhook('')
    logging.info(f'Shutting down webhook connection')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=config.WEBHOOK_PATH,
        skip_updates=True,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
