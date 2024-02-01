from loader import session, logging
from datetime import datetime


def get_open_positions():
    try:
        return session.get_positions(category="linear", settleCoin="USDT")
    except Exception as e:
        raise Exception(f'Не удалось получить актуальные открытые позиции, ошибка: {e}')


def get_history_transfer(limit_history):
    try:
        return session.get_order_history(category="linear", limit=limit_history)
    except Exception as e:
        raise Exception(f'Не удалось получить историю открытых позиций, ошибка: {e}')


# ---------------------------------------------------------------------------------------
# ДЕТАЛИЗИЯ ДЛЯ КОНФИГА
def get_wallet_balance() -> tuple[float, float]:
    """ Возвращается (float, float) -> (Сумма активов, Баланс маржи) """
    # Возвращаемые данные можно увидеть тут - https://testnet.bybit.com/user/assets/home/tradingaccount
    try:
        total_available_balance = session.get_wallet_balance(accountType='UNIFIED')['result']['list'][0]['totalAvailableBalance']  # общая сумма, которую можно использовать в качестве маржи на вашем аккаунте, включая баланс кошелька и нереализованный P&L по бессрочным контрактам.
        # Если баланс маржи опускается ниже уровня поддерживающей маржи, будет запущен процесс ликвидации. Обратите внимание, что представленное здесь значение является сконвертированным, а не фактическим балансом USD на вашем аккаунте.
        total_equity = session.get_wallet_balance(accountType='UNIFIED')['result']['list'][0]['totalEquity']  # Общий капитал рассчитывается путём сложения стоимости каждой монеты на вашем аккаунте в пересчёте на фиатную валюту.
        return round(float(total_equity), 2), round(float(total_available_balance), 2)
    except Exception as err:
        logging.warning(err)
        return 0, 0


def expired_date():
    try:
        expiredAt = session.get_api_key_information()['result']['expiredAt'].replace('Z', '').replace('T', ' ')  # дата когда api надо менять
        formatted_expiredAt = datetime.strptime(expiredAt, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")

        original_date = datetime.strptime(expiredAt, "%Y-%m-%d %H:%M:%S")
        date_difference = (original_date - datetime.now()).days

        return formatted_expiredAt, date_difference
    except Exception as err:
        logging.warning(err)
        return 0, 0
# ---------------------------------------------------------------------------------------

def is_exist_symbol(symbol: str) -> bool:
    """ Возвращает bool, существует ли монета """
    try:
        session.get_instruments_info(category="linear", symbol=symbol)
        return True
    except Exception:
        return False


class TradeHelpers:
    def __init__(self):
        self.limit_history = 40

        self.history = self._get_history()
        self.open_positions = self._get_open_positions()

    def _get_history(self) -> list:
        try:
            history = []
            info = get_history_transfer(self.limit_history)['result']['list']
            for i in info:
                coin = f"#{i['symbol']}"
                price = i['price']
                position = "🟢Long" if i['side'] == 'Buy' else "🔴Short"
                stopLoss = f" Стоп-лосс: {i['stopLoss']}$, " if i['stopLoss'] != '' else ''
                takeProfit = f"Тейк-профит: {i['takeProfit']}$," if i['takeProfit'] != '' else ''
                cumExecValue = i['cumExecValue']
                updatedTime = f"Дата: {datetime.fromtimestamp(int(i['updatedTime']) / 1000).strftime('%H:%M %d/%m/%Y')}" if i['updatedTime'] != '' else ''
                orderStatus = "Статус: " + ("✅" if i['orderStatus'] == 'Filled' else "Создан➕" if i['orderStatus'] == 'Created' else 'Отменен🚫' if i['orderStatus'] == 'Cancelled' else i['orderStatus'])
                if i['stopOrderType'] != "":
                    stopOrderType = f'🟩{i["stopOrderType"]}' if i["stopOrderType"] == "TakeProfit" else f'🟥{i["stopOrderType"]}' if i["stopOrderType"] == "StopLoss" else i["stopOrderType"]
                    triggerPrice = i["triggerPrice"]
                    history.append(f"{stopOrderType} для {coin} по цене {triggerPrice}, {updatedTime}")
                else:
                    history.append(f'{position} {coin}, Цена: {price}$, Объем: {cumExecValue}$,{stopLoss}{takeProfit} {orderStatus} {updatedTime}')
            return history
        except Exception as e:
            logging.warning(e)
            return ["История ордеров пуста/Ошибка получения данных"]

    def _get_open_positions(self) -> list:
        try:
            positions = []
            info = get_open_positions()['result']['list']
            for i in info:
                coin = f"#{i['symbol']}"
                leverage = f"Маржа։ {i['leverage']}x"
                avgPrice = "Цена: " + (f"{round(float(i['avgPrice']), 2)}$" if float(i['avgPrice']) > 1 else f"{(float(i['avgPrice']))}$")
                liqPrice = f"Цена ликвидации: {round(float(i['liqPrice']), 2)}$" if i['liqPrice'] != '' else ''
                cumRealisedPnl = f"PnL: {round(float(i['cumRealisedPnl']), 2)}%"
                position = "🟢Long" if i['side'] == 'Buy' else "🔴Short"
                stopLoss = f"Стоп-лосс: {i['stopLoss']}$" if i['stopLoss'] != '' else ''
                takeProfit = f"Тейк-профит: {i['takeProfit']}$" if i['takeProfit'] != '' else ''
                positionValue = f"Объем: {round(float(i['positionValue']), 2)}$"

                positions.append(', '.join(
                    filter(None, [f"{position} {coin}", cumRealisedPnl, avgPrice, positionValue, leverage, liqPrice, stopLoss, takeProfit])
                ))
            return positions
        except Exception as e:
            logging.warning(e)
            return ["Нет открытых позиций/Ошибка получения данных"]

    def update_history(self):
        self.history = self._get_history()

    def update_open_positions(self):
        self.open_positions = self._get_open_positions()


class Utils:
    def __init__(self):
        self.expired_date = expired_date()
        self.wallet_balance = get_wallet_balance()

    def update_utils(self):
        """ Обновление всех статусов """
        self.expired_date = expired_date()
        self.wallet_balance = get_wallet_balance()


utils = Utils()
