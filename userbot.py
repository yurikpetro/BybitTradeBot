from pyrogram import Client, filters, types
from pyrogram.handlers import MessageHandler

from loader import logging
from config import USERBOT_API_HASH, USERBOT_API_ID, CHAT_ID_FOR_PARSING, CHAT_ID_FOR_LOGS
from services.trade import do_futures_trade

msg_id = None


def main_client(name):
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    client = Client(name=name, api_id=USERBOT_API_ID, api_hash=USERBOT_API_HASH, lang_code="ru")

    async def message_photo(client: Client, message: types.Message):
        global msg_id
        logging.info(f'В группе появился прогноз msg_id={message.id} подпись - {message.caption}')

        async for msg in client.get_chat_history(chat_id=CHAT_ID_FOR_PARSING, limit=1, offset_id=-1):  # ищем в истории с конца
            try:
                if msg.photo and msg.id != msg_id:  # если есть фото
                    msg_id = msg.id

                    if msg.caption:
                        do_futures_trade(msg.caption)
                    else:
                        logging.info('Подпись отсутствует, запуск трейдинга не произошел')
                else:
                    logging.info(f'Такое сообщение уже переслано msg_id={msg.id} подпись - {msg.caption}')
            except Exception as e:
                logging.warning(f'Произошла ошибка {e}')


    client.add_handler(MessageHandler(message_photo, filters=filters.photo & filters.chat(chats=int(CHAT_ID_FOR_PARSING))))  # CHAT_ID_FOR_PARSING - передаём ID или Username чата
    print('[+] Юзербот запущен')
    try:
        client.run()
    except Exception as err:
        if 'database is locked' in str(err):
            print('[!] Ошибка, запущен фоновый клиент Pyrogram! Завершите все процессы данного клиента чтобы userbot начал работать!\n'
                  'Инструкция - https://docs.pyrogram.org/faq/sqlite3-operationalerror-database-is-locked')
            logging.warning('Ошибка, запущен фоновый клиент Pyrogram! Завершите все процессы данного клиента чтобы userbot начал работать!')
        else:
            print(f'[!] Возникала ошибка!\n'
                  f'{err}')
            logging.warning(err)


if __name__ == '__main__':
    main_client('ByBit_bot')
