import logging
from pybit.unified_trading import HTTP

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN, BYBIT_API_KEY, BYBIT_API_SECRET, TESTNET_BYBIT

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


class States(StatesGroup):
    change_leverage = State()
    change_quantity = State()
    change_takeProfit = State()
    change_stopLoss = State()

    id_history_message = State()
    id_positions_message = State()


# --------------- Логирование -------------------------
__log_name = 'logs.log'
logging.basicConfig(
    filename=__log_name,
    filemode='w',
    format='[%(asctime)s.%(msecs)-3d] %(filename)s:%(lineno)d #%(levelname)s - %(message)s',  # -25s это отступы
    datefmt='%H:%M:%S %d/%m/%y',
    level=logging.INFO
)
dp.middleware.setup(LoggingMiddleware())

# --------------- bybit -------------------------
session = HTTP(
    testnet=TESTNET_BYBIT,
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
)
