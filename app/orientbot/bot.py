import os
import logging
from io import StringIO
from itertools import combinations
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType
from aiogram.types.input_file import InputFile
from aiogram.types import ParseMode
from app.orientbot.race import Race, calc_togethers_pair
from app.orientbot.tools import echo_error, temp_file_path
import config.config as config


# Команды бота
BOT_COMMANDS = '''ping - проверка отклика бота
help - как пользоваться этим ботом?'''

# Уровень логов
logging.basicConfig(level=logging.INFO)

# Aiogram Telegram Bot
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['help', 'start'])
async def cmd_help(message: types.Message):
    """
    Что может делать этот бот?
    """
    def format_command(command_line):
        command, desc = [x.strip() for x in command_line.split('-')]
        return md.text(md.link(f'/{command}', f'/{command}'), f' - {desc}')

    commands = [format_command(cl) for cl in BOT_COMMANDS.splitlines()]
    await message.reply(
        md.text(
            md.text(f'Поиск "паровозов" на соревнованиях по спортивному ориентированию'),
            md.text('\n1. Скопируйте таблицу результатов группы без заголовка с флажками `Показывать сплиты` и '
                    '`Отсечки нарастающим итогом` с сайта [https://orgeo.ru/](https://orgeo.ru/)'),
            md.text('2. Вставьте в текстовый файл с любым именем'),
            md.text('3. Сохраните файл и отправьте его боту'),
            md.text('\nБот вернёт список "паровозов" с перечислением порядковых номеров КП '
                    f'хотя бы с тремя встречами в пределах {config.TOGETHER_SECONDS} секунд, '
                    'либо сообщит об их отсутствии'),
            md.text(md.bold('\nАлгоритм поиска «паровозов»')),
            md.text('1. Для каждого спортсмена вычислить абсолютное время посещения всех КП с учётом абсолютного '
                    'времени старта и временных интервалов посещения КП из сплита с отсечками нарастающим итогом. '
                    'Удалить КП, которых нет в списке спортсмена, занявшего первое место.'),
            md.text('2. Для всех пар спортсменов вычислить список КП в которых они встретились в пределах '
                    f'{config.TOGETHER_SECONDS} секунд.'),
            md.text('3. Выбрать пары спортсменов, которые встретились более чем на трёх КП.'),
            md.text('4. Отсортировать пары в порядке убывания числа встреч на КП.'),
            md.text('5. В каждой паре «паровозит» тот, кто в большем числе встреч на КП отмечался позже. КП, на '
                    'которых тот, кто «паровозит» отмечался раньше того, за кем он «паровозит», пометить знаком «-». '
                    'При одинаковом числе КП с «-» и без «-» считать, что «паровозит» тот, кто занял место хуже '
                    'в своей группе.'),
            md.text('6. Если тот, кто «паровозит», ранее не был добавлен в результирующий список с большим числом '
                    'встреч на КП, то добавить пару спортсменов и список порядковых номеров КП со встречами '
                    'в результирующий список.'),
            md.text(md.bold('\nКоманды бота')),
            *commands,
            md.text(md.bold('\nРазработчик')),
            md.text(f'{config.DEVELOPER_NAME} {config.DEVELOPER_TELEGRAM}'),
            md.text(md.bold('\nИсходные коды бота')),
            md.text('[https://github.com/parusinf/orientbot]'
                    '(https://github.com/parusinf/orientbot)'),
            sep='\n',
        ),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN,
    )
    photo = InputFile(config.HELP_IMAGE_PATH)
    await bot.send_photo(chat_id=message.chat.id, photo=photo, caption='Как выделять таблицу результатов')
    example = InputFile(config.EXAMPLE_PATH)
    await bot.send_document(chat_id=message.chat.id, document=example, caption='Пример файла с таблицей результатов')


@dp.message_handler(commands='ping')
async def cmd_ping(message: types.Message):
    """
    Проверка отклика бота
    """
    await message.reply('pong')


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def process_results(message: types.Message):
    if message.document:
        file_name = message.document['file_name']
        file_path = temp_file_path(file_name)
        try:
            # Загрузка файла от пользователя во временную директорию
            await message.document.download(destination_file=file_path)
            # Чтение файла
            with open(file_path, 'r') as file:
                lines = file.read().splitlines()
            # Удаление файла из временной директории
            os.remove(file_path)
            # Разбор забегов
            races = [Race(lines[i:i+5]) for i in range(0, len(lines), 5)]
            # Вычисление КП со встречами во всех парах забегов
            togethers_pairs = [calc_togethers_pair(pair[0], pair[1]) for pair in combinations(races, 2)]
            # Фильтрация списка пар забегов: должно быть хотя бы {TOGETHER_NUMBER} КП со встречами
            togethers_pairs_filtered = list(filter(lambda x: len(x[0]) >= config.TOGETHER_NUMBER, togethers_pairs))
            # Сортировка пар забегов в порядке убывания числа КП со встречами
            togethers_pairs_filtered.sort(key=lambda x: len(x[0]), reverse=True)
            # Формирование списка пар со встречами на КП
            buffer = StringIO()
            count = 0
            togethers_pairs_added = []
            for togethers, pair in togethers_pairs_filtered:
                # Поиск в уже найденных "паровозах" для избежания дублирования
                is_duplicate = False
                for togethers_added, pair_added in togethers_pairs_added:
                    abs_togethers = [abs(t) for t in togethers]
                    abs_togethers_added = [abs(t) for t in togethers_added]
                    if pair_added[1] == pair[1] and set(abs_togethers).issubset(abs_togethers_added):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    # Вывод "паровоза"
                    count += 1
                    buffer.write(f'{count}. {pair[1].family} ({pair[1].place}) → '
                                 f'{pair[0].family} ({pair[0].place}): {togethers}\n')
                    togethers_pairs_added.append((togethers, pair))
            # Отправка списка "паровозов" пользователю
            result = buffer.getvalue() or '"Паровозов" в этой группе нет'
            await message.reply(result)
        except Exception as error:
            await echo_error(message, error)
