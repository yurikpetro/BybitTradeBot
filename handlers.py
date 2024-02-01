from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ParseMode
from keyboards import *
from loader import dp, bot, States, logging
from services.connection_db import db
from services.trade_help import utils, is_exist_symbol
from services.trade import post_leverage
from config import CHAT_ID_FOR_LOGS, CHAT_ID_FOR_LOGS_THREAD_ID


__version__ = '1.5.1'

history_limit_on_message = positions_limit_on_message = 10  # количество сообщений истории которое будет отображаться (лимит отображения в одном сообщении)

# -----------------------------------------------------------------------
def admin_in_bd(tg_id) -> bool:
    if tg_id in db.get_admins():
        return True
    return False

# ------------------------------------------------------------------------
# РАБОТА С КОМАНДАМИ

@dp.message_handler(commands=['start'])
async def start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if '-' in str(message.chat.id):
        logging.warning(f'Попытка запуска бота в группе id={message.chat.id}, username=@{message.chat.username}')
        return

    if admin_in_bd(user_id):
        await state.update_data({
            'history_limit_on_message': history_limit_on_message,
            'positions_limit_on_message': positions_limit_on_message,
            'history_limit_step': history_limit_on_message,  # шаг увеличения, должен быть равен лимиту отображения, чтобы не возникало странностей
            'positions_limit_step': positions_limit_on_message,
        })

        await message.reply(text="BybitTradeBot приветствует вас!", reply_markup=del_kb)
        await bot.send_message(chat_id=user_id, text="Чтобы узнать больше обо мне отправь команду /help", reply_markup=inline_user_manager)
    else:
        await message.reply(text="Привет! Я BybitTradeBot! Я помогу автоматизировать твой трейдинг.\n"
                                 "У вас нет доступа к данному боту😪\n"
                                 "Если вам необходимо реализовать бота для Ваших нужд - обращайтесь к нам: @glithhch и @yurikpetro", reply_markup=del_kb)


@dp.message_handler(commands=['help'])
async def start_command(message: Message):
    await message.reply(text=f'''Версия бота - {__version__}
/start - вызывает главное меню бота

<b>Как рассчитывается 🟥StopLoss и 🟩TakeProfit?</b>
Значения устанавливаются в пределе от 1 до 100
<b>ТейкПрофит</b> устанавливается как Стоимость монеты + (Стоимость монеты * TP/100), 
<b>СтопЛосс</b> же как Стоимость монеты - (Стоимость монеты * SL/100)

Например, стоимость монеты: 500$, ТейкПрофит установлен как 20%, СтопЛосс как 25%, тогда:
🟩<b>ТейкПрофит:</b> 500$ + (500$ * 0,2) = 500$ + 100$ = <b>600$</b>
🟥<b>СтопЛосс:</b> 500$ - (500$ * 0.25) = 500$ - 125$ = <b>375$</b>
Подробная инструкция по боту - https://telegra.ph/Instrukciya-po-polzovaniyu-botom-01-05''', parse_mode=ParseMode.HTML)


@dp.message_handler(text=['Отменить действие 🚫'], state='*')
async def cancel_current_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await message.reply('Действие отменено', reply_markup=del_kb)
    await state.finish()

# -------------------------------------------------------------------------

@dp.message_handler(state=States.all_states)
async def states_manager(message: Message, state: FSMContext):
    """ Обработчик кнопок """
    current_state = await state.get_state()

    if current_state == "States:change_leverage":
        await change_leverage(message, state)
    elif current_state == "States:change_quantity":
        await change_quantity(message, state)
    elif current_state == "States:change_takeProfit":
        await change_takeProfit(message, state)
    elif current_state == "States:change_stopLoss":
        await change_stopLoss(message, state)


async def change_leverage(message, state):
    msg_id = message.from_user.id
    coin, msg_leverage = message.text.split()
    coin = coin.upper() if "USDT" in coin.upper() else coin.upper() + "USDT"

    try:
        if is_exist_symbol(coin):
            if msg_leverage.isdigit():
                msg_leverage = int(msg_leverage)
                if 1 <= msg_leverage <= 100:
                    if msg_leverage == 10:
                        db.set_leverage_by_symbol(coin)
                    else:
                        db.set_leverage_by_symbol(coin, msg_leverage)

                    post_leverage(coin, msg_leverage)
                    await bot.send_message(msg_id, f'Кредитное плечо для монеты {coin} теперь равно {msg_leverage}x', reply_markup=del_kb)
                    await bot.send_message(chat_id=CHAT_ID_FOR_LOGS, message_thread_id=CHAT_ID_FOR_LOGS_THREAD_ID, text=f'Кредитное плечо изменено и теперь для монеты {coin} равно {msg_leverage}x')
                else:
                    await bot.send_message(msg_id, 'Число должно быть в диапазоне 1 - 100', reply_markup=del_kb)
            else:
                await bot.send_message(msg_id, 'Введите число!', reply_markup=del_kb)
        else:
            await message.reply("Такой монеты на ByBit не существует", reply_markup=del_kb)
            await bot.send_message(chat_id=CHAT_ID_FOR_LOGS, message_thread_id=CHAT_ID_FOR_LOGS_THREAD_ID, text=f'Ошибка изменения кредитного плеча для монеты {coin}, такой монеты на ByBit не существует')
    except Exception as e:
        if "ErrCode: 110043" in str(e):
            await bot.send_message(msg_id, f"Кредитное плечо для монеты {coin} уже равно {msg_leverage}", reply_markup=del_kb)
        else:
            logging.warning(f"При изменении плеча произошла ошибка {e}")
    await state.finish()



async def change_quantity(message, state):
    msg_id = message.from_user.id
    if str(message.text).isdigit():
        msg_int = int(message.text)
        if 0 <= msg_int:
            db.set_quantity(msg_int)
            await bot.send_message(msg_id, f'Сумма изменена на {msg_int}$', reply_markup=del_kb)
            await bot.send_message(chat_id=CHAT_ID_FOR_LOGS, message_thread_id=CHAT_ID_FOR_LOGS_THREAD_ID, text=f'Сумма для открытия новых позиций изменена, и теперь равна {msg_int}$')
        else:
            await bot.send_message(msg_id, 'Число должно быть больше 0', reply_markup=del_kb)
    else:
        await bot.send_message(msg_id, 'Введите число!', reply_markup=del_kb)
    await state.finish()


async def change_takeProfit(message, state):
    msg_id = message.from_user.id
    if str(message.text).isdigit():
        msg_int = int(message.text)
        if 0 <= msg_int:
            db.set_takeProfit(msg_int)
            await bot.send_message(msg_id, f'🟩TakeProfit теперь равен {msg_int}, это значит что TakeProfit будет открываться на {100 + msg_int}% от цены открытия позиции', reply_markup=del_kb)
            await bot.send_message(chat_id=CHAT_ID_FOR_LOGS, message_thread_id=CHAT_ID_FOR_LOGS_THREAD_ID, text=f'🟩Установлено новое значение TakeProfit, оно равно {100 + msg_int}%')
        else:
            await bot.send_message(msg_id, 'Число должно быть больше 0', reply_markup=del_kb)
    else:
        await bot.send_message(msg_id, 'Введите число!', reply_markup=del_kb)
    await state.finish()


async def change_stopLoss(message, state):
    msg_id = message.from_user.id
    if str(message.text).isdigit():
        msg_int = int(message.text)
        if 0 <= msg_int <= 100:
            db.set_stopLoss(msg_int)
            await bot.send_message(msg_id, f'🟥StopLoss теперь равен {msg_int}, это значит что StopLoss будет открываться на {100 - msg_int}% от цены открытия позиции', reply_markup=del_kb)
            await bot.send_message(chat_id=CHAT_ID_FOR_LOGS, message_thread_id=CHAT_ID_FOR_LOGS_THREAD_ID, text=f'🟥Установлено новое значение StopLoss, оно равно {100 - msg_int}%')

        else:
            await bot.send_message(msg_id, 'Число должно быть в диапазоне от 0 до 100', reply_markup=del_kb)
    else:
        await bot.send_message(msg_id, 'Введите число!', reply_markup=del_kb)
    await state.finish()
# -------------------------------------------------------------------------

async def update_message(chat_id, text, id_message, reply_markup=None):
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=id_message, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as err:
        logging.warning(f'Не удалось отредактировать сообщение chat_id={chat_id} message_id={id_message}\n{err}')
        await bot.send_message(chat_id=CHAT_ID_FOR_LOGS, message_thread_id=CHAT_ID_FOR_LOGS_THREAD_ID, text=f'update_message | Не удалось отредактировать сообщение message_id={id_message}')


@dp.callback_query_handler()
async def buttons_manager(call: CallbackQuery, state: FSMContext):
    call_id = call.from_user.id
    call_data = call.data
    full_history = [f'{num}. {part}\n' for num, part in enumerate(db.history, 1)]  # тут формируется полный список для отображения
    full_positions = [f'{num}. {part}\n' for num, part in enumerate(db.open_positions, 1)]

    state_data = await state.get_data()
    history_limit_step = state_data.get('history_limit_step')
    positions_limit_step = state_data.get('positions_limit_step')

    messages_and_states = {
        'change_quantity': ('Введите сумму в USDT, которая будет использоваться для открытия новых позиций', States.change_quantity),
        'change_leverage': ('Введите название монеты и новое значение её кредитного плеча, пример: BTC 50', States.change_leverage),
        'change_stopLoss': ('Введите новое значение для stopLoss в диапазоне 0 - 100', States.change_stopLoss),
        'change_takeProfit': ('Введите новое значение для takeProfit в диапазоне 0 - 100', States.change_takeProfit),
    }

    # ------------------------------------------------------------------------------
    # ОБРАБОТЧИКИ КНОПОК ИСТОРИИ
    if call_data == 'show_history':
        db.update_history()
        full_history = [f'{num}. {part}\n' for num, part in enumerate(db.history, 1)]

        history_limit_step = history_limit_on_message  # сброс шага
        history = "".join(full_history[:history_limit_on_message])

        msg = await bot.send_message(call_id, text=f"🗂<b>История ордеров:</b>\n\n{history}",
                                     reply_markup=inline_next if history_limit_step <= len(full_history) else None,
                                     parse_mode=ParseMode.HTML)
        await state.update_data(id_history_message=msg.message_id)
        await bot.answer_callback_query(call.id)

    elif call_data == 'next_history':
        if len(full_history) >= history_limit_step + history_limit_on_message or len(full_history) - history_limit_step > 0:
            history_limit_step += history_limit_on_message
            await state.update_data(history_limit_step=history_limit_step)
        else:
            await bot.answer_callback_query(call.id)
            return

        history = "".join(full_history[history_limit_step-history_limit_on_message:history_limit_step])

        await update_message(call_id, text=f"🗂<b>История ордеров:</b>\n\n{history}", id_message=state_data.get('id_history_message'),
                             reply_markup=inline_back if history_limit_step >= len(full_history) else inline_next_back)
        await bot.answer_callback_query(call.id)

    elif call_data == 'back_history':
        if history_limit_step - history_limit_on_message >= history_limit_on_message:
            history_limit_step -= history_limit_on_message
            await state.update_data(history_limit_step=history_limit_step)
        else:
            await bot.answer_callback_query(call.id)
            return

        history = "".join(full_history[history_limit_step-history_limit_on_message:history_limit_step])

        await update_message(call_id, text=f"🗂<b>История ордеров:</b>\n\n{history}", id_message=state_data.get('id_history_message'),
                             reply_markup=inline_next if history_limit_step <= history_limit_on_message else inline_next_back, )
        await bot.answer_callback_query(call.id)

    # ------------------------------------------------------------------------------
    # ОБРАБОТЧИКИ КНОПОК ПОЗИЦИЙ
    elif call_data == 'show_positions':
        db.update_open_positions()
        full_positions = [f'{num}. {part}\n' for num, part in enumerate(db.open_positions, 1)]

        positions_limit_step = positions_limit_on_message  # сброс шага
        positions = "".join(full_positions[:positions_limit_on_message])

        msg = await bot.send_message(call_id, text=f"📖<b>Открытые позиции:</b>\n\n{positions}", reply_markup=inline_next_positions if positions_limit_step <= len(full_positions) else None, parse_mode=ParseMode.HTML)

        await state.update_data(id_positions_message=msg.message_id)
        await bot.answer_callback_query(call.id)

    elif call_data == 'next_positions':
        if len(full_positions) >= positions_limit_step + positions_limit_on_message or len(full_positions) - positions_limit_step > 0:
            positions_limit_step += positions_limit_on_message
            await state.update_data(positions_limit_step=positions_limit_step)
        else:
            await bot.answer_callback_query(call.id)
            return

        positions = "".join(full_positions[positions_limit_step - positions_limit_on_message:positions_limit_step])

        await update_message(call_id, text=f"📖<b>Открытые позиции:</b>\n\n{positions}", id_message=state_data.get('id_positions_message'),
                             reply_markup=inline_back_positions if positions_limit_step >= len(full_positions) else inline_next_back_positions)
        await bot.answer_callback_query(call.id)

    elif call_data == 'back_positions':
        if positions_limit_step - positions_limit_on_message >= positions_limit_on_message:
            positions_limit_step -= positions_limit_on_message
            await state.update_data(positions_limit_step)
        else:
            await bot.answer_callback_query(call.id)
            return

        positions = "".join(full_positions[positions_limit_step-positions_limit_on_message:positions_limit_step])

        await update_message(call_id, text=f"📖<b>Открытые позиции:</b>\n\n{positions}", id_message=state_data.get('id_positions_message'),
                             reply_markup=inline_next_positions if positions_limit_step <= positions_limit_on_message else inline_next_back_positions)
        await bot.answer_callback_query(call.id)

    # ------------------------------------------------------------------------------
    # ОБРАБОТЧИКИ ТЕЙК-ПРОФИТ И СТОП-ЛОСС
    elif call_data == 'change_Lost_Profit':
        await bot.send_message(chat_id=call_id, text='Что именно вы хотите сменить?', reply_markup=inline_mgr_less_profit)

    # ------------------------------------------------------------------------------
    # ОБРАБОТЧИКИ КНОПОК НАСТРОЕК
    elif call_data == 'settings_call':
        utils.update_utils()
        await bot.send_message(chat_id=call_id, text=f'⚙️<b>Настройки конфигурации:</b>'
                                                     f'\n  💵Сумма USDT для новых позиций - {db.get_quantity()}$\n'
                                                     f'  🟩Тейк-профит - {100 + db.get_takeProfit()}%\n'
                                                     f'  🟥Стоп-лосс - {100 - db.get_stopLoss()}%\n'
                                                     f'  📊Активы: {utils.wallet_balance[0]}$, Баланс маржи: {utils.wallet_balance[1]}$\n'
                                                     f'  ⏳Дата истечения токена - {utils.expired_date[0]} ({utils.expired_date[1]} days)\n\n'
                                                     f'{db.get_leverage_by_symbol()}', reply_markup=del_kb, parse_mode=ParseMode.HTML)
        await bot.answer_callback_query(call.id)

    # ------------------------------------------------------------------------------
    # ОБРАБОТКА КНОПОК ЗАПУСКА СОСТОЯНИЙ
    elif call_data in messages_and_states:
        message, state = messages_and_states[call_data]
        await bot.send_message(chat_id=call_id, text=message, reply_markup=cancel)
        await state.set()
        await bot.answer_callback_query(call.id)

    # ------------------------------------------------------------------------------
