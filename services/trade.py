import requests

from loader import logging, session
from services.connection_db import db
from config import CHAT_ID_FOR_LOGS, BOT_TOKEN, CHAT_ID_FOR_LOGS_THREAD_ID
from services.trade_help import is_exist_symbol


def send_msg(msg):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    params = {'chat_id': db.get_user_value('tg_id'), 'text': msg}
    requests.post(url, data=params)

    params = {"message_thread_id": CHAT_ID_FOR_LOGS_THREAD_ID, 'chat_id': f'{CHAT_ID_FOR_LOGS}_{CHAT_ID_FOR_LOGS_THREAD_ID}', 'text': msg}
    requests.post(url, data=params)


def get_info_of_coin(symbol: str) -> dict:
    """ Возвращает информацию о монете """
    try:
        return session.get_instruments_info(category="linear", symbol=symbol)
    except Exception as e:
        logging.warning(f'Произошла ошибка {e}')
        return {}


def round_quantity(coin, quantity):
    """ Возвращает количество монет доступных для покупки, если монет передано меньше чем нужно для покупки возникает исключение """
    minOrderQty: str = get_info_of_coin(coin)['result']['list'][0]['lotSizeFilter']['minOrderQty']
    len_min = len(minOrderQty.split('.')[-1]) if '.' in minOrderQty else 0

    qty = round(quantity, len_min)

    if qty != 0:
        return qty

    raise Exception(f'Монета {coin} не поддерживает покупку в количестве: {quantity:.5f)}\nМин.количество: {minOrderQty}')


def do_futures_trade(msg: str):
    coin = msg.split()[0].replace('#', '') + 'USDT'
    if ("buy" in msg.lower() or "short" in msg.lower()) and is_exist_symbol(coin):
        quantity_USDT = db.get_quantity()
        logging.info(f'Запущена покупка futures, данные - {msg}')
        post_order(coin, msg, quantity_USDT)


def get_price_coin(coin: str):
    """ Возвращает цену монеты в разные временные периоды"""
    try:
        return session.get_tickers(category="linear", symbol=coin)['result']['list'][0]['markPrice']
    except Exception as e:
        raise Exception(f'Не удалось получить информацию о цене монеты {coin}, ошибка: {e}')


def post_order(coin, order: str, quantity_USDT: int | float):
    """ Создание ордера на long или short """
    try:
        price_coin = float(get_price_coin(coin))
        qty = round_quantity(coin, float(quantity_USDT / price_coin))

        side = "Buy" if "buy" in order.lower() else "Sell" if "short" in order.lower() else "ErrorOrder"
        stopLoss = price_coin * (1 - db.get_stopLoss() / 100)
        takeProfit = price_coin * (1 + db.get_takeProfit() / 100)

        if "short" in order.lower():
            stopLoss, takeProfit = takeProfit, stopLoss
        if 'buy' in order.lower() or "short" in order.lower():
            session.place_order(
                category="linear",
                symbol=coin,
                side=side,
                orderType="Market",
                qty=qty,
                stopLoss=stopLoss,
                takeProfit=takeProfit
            )
            send_msg(f'✅Успех - {coin}\n📄{qty} монет(ы) по цене {price_coin}$\n🟩Тейк-профит: {round(float(takeProfit), 2)}$\n🟥Стоп-лосс: {round(float(stopLoss), 2)}$\n💵Сумма ордера - {round((qty * price_coin), 2)}$')
    except Exception as e:
        if "ErrCode: 33004" in str(e):  # ошибка истек срок API
            err_msg = f'❌Ошибка - {order}\nИстек срок API ключа'
        elif "ErrCode: 110007" in str(e):  # ошибка не хватки денег
            err_msg = f'❌Ошибка - {order}\nНе достаточно средств на балансе для создания ордера:\nМонета: {order}, цена покупки: {quantity_USDT}$'
        else:
            err_msg = f'❌Ошибка - {order}\nОписание: {e}\nСумма при покупке: {quantity_USDT}$'

        logging.warning(err_msg)
        send_msg(err_msg)



def post_leverage(symbol: str, new_leverage: str | int):
    try:
        symbol = symbol + "USDT" if "USDT" not in symbol else symbol
        new_leverage = str(new_leverage)
        return session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=new_leverage,
            sellLeverage=new_leverage)
    except Exception as e:
        logging.warning(f'Произошла ошибка {e}')


def test():
    send_msg('tessssssssssssst')

    # post_order('MAV', '#MAV Buy Swing Setup.', 1000)
    # post_order('DOGE', 'Buy Swing Setup.', 1000)
    # price_coin = float(get_price_coin('MAVUSDT'))
    # print('MAVUSDT', round_quantity('ETHUSDT', float(100 / price_coin)))

    # price_coin = float(get_price_coin('ETHUSDT'))
    # print('ETHUSDT', round_quantity('ETHUSDT', float(100 / price_coin)))

    # print(db.open_positions)
    # print(get_info_of_coin('BTCUSDT'))
    pass


if __name__ == "__main__":
    test()
