import asyncio
import threading

from aiogram import executor
import os
from pathlib import Path

from loader import dp, logging
import handlers
from userbot import main_client



async def start(_):
    logging.info('Бот запущен')
    print('[+] Бот запущен')


def bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True, on_startup=start)


if __name__ == '__main__':
    name = 'ByBit_bot'
    if f'{name}.session' not in os.listdir(Path(__file__).parent):
        print('--------------------------------------------------------\n'
              '[!] Нет сессии, после ввода данных перезапустите бота!!!\n'
              '--------------------------------------------------------')
        main_client(name)

    try:
        thread = threading.Thread(target=bot_thread)
        thread.start()
        main_client(name)
    except Exception as error:
        logging.warning(error)
        print(error)
    finally:
        print('\n[+] Пока пока...')

