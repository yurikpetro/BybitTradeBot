from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup


cancel = ReplyKeyboardMarkup(resize_keyboard=True).add('Отменить действие 🚫')
del_kb = ReplyKeyboardRemove()

# -------------------------------------------------------------------------------------------
# ОСНОВНАЯ КЛАВИАТУРА
inline_user_manager = InlineKeyboardMarkup(row_width=2)
inline_user_manager.add(*[
    InlineKeyboardButton("📖Открытые позиции", callback_data="show_positions"),
    InlineKeyboardButton("🗂История ордеров", callback_data="show_history"),
    InlineKeyboardButton("Изменить плечо", callback_data="change_leverage"),
    InlineKeyboardButton("🟥🟩Изменить SL/TP", callback_data="change_Lost_Profit"),
    InlineKeyboardButton("⚙️Показать конфигурацию", callback_data="settings_call"),
])
inline_user_manager.add(InlineKeyboardButton("Изменить сумму(USDT) для новых позиций", callback_data="change_quantity"))

# -------------------------------------------------------------------------------------------
# Кнопки вперед назад для перелистывания истории начало
__back_button_history = InlineKeyboardButton('️⬅️Назад', callback_data='back_history')
__next_button_history = InlineKeyboardButton('Вперед➡️', callback_data='next_history')

inline_back = InlineKeyboardMarkup().add(__back_button_history)
inline_next = InlineKeyboardMarkup().add(__next_button_history)

inline_next_back = InlineKeyboardMarkup(row_width=2)
inline_next_back.add(*[
    __back_button_history,
    __next_button_history,
])

# -------------------------------------------------------------------------------------------
# Кнопки вперед назад для перелистывания истории конец
__back_button_positions = InlineKeyboardButton('⬅️Назад', callback_data='back_positions')
__next_button_positions = InlineKeyboardButton('Вперед➡️', callback_data='next_positions')

inline_back_positions = InlineKeyboardMarkup().add(__back_button_positions)
inline_next_positions = InlineKeyboardMarkup().add(__next_button_positions)

inline_next_back_positions = InlineKeyboardMarkup(row_width=2)
inline_next_back_positions.add(*[
    __back_button_positions,
    __next_button_positions,
])

# -------------------------------------------------------------------------------------------
# ТЕЙК-ПРОФИТ И СТОП-ЛОСС
inline_mgr_less_profit = InlineKeyboardMarkup(row_width=1)
inline_mgr_less_profit.add(*[
    InlineKeyboardButton('🟥Установить stopLoss', callback_data='change_stopLoss'),
    InlineKeyboardButton('🟩Установить takeProfit', callback_data='change_takeProfit'),
])

# -------------------------------------------------------------------------------------------












