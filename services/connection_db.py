import json
from pathlib import Path
from services.trade_help import logging, TradeHelpers

path = Path(__file__).parent / 'DB.json'


def __create_db():
    structure = {
        'user': {
            'tg_id': 1234567,
            'quantity': 100,  # доллары
            'stopLoss': 20,
            'takeProfit': 10
        },
        'admins_id': [],  # список тех кто имеет доступ к админке
        'leverage_by_symbol': {}  # здесь будут храниться отдельно установленные количества к покупке, пример: 'BTCUSDT': 12
    }
    with open('DB.json', 'w', encoding='utf8') as f:
        json.dump(structure, f, indent=4, ensure_ascii=False)


class DBConnect(TradeHelpers):
    def __init__(self):
        super().__init__()
        with open(path, 'r', encoding='utf8') as f:
            self.db: dict = json.load(f)

    def __save(self):
        with open(path, 'w', encoding='utf8') as f:
            json.dump(self.db, f, indent=4, ensure_ascii=False)

    def get_admins(self) -> list[int]:
        return self.db['admins_id']

    def get_user_value(self, parameter):
        try:
            return self.db['user'][parameter]
        except Exception:
            logging.warning(f'Параметра {parameter} в бд - user нет!')
            return None

    def get_takeProfit(self) -> int:
        return self.db['user']['takeProfit']

    def set_takeProfit(self, new_takeProfit: str):
        try:
            self.db['user']['takeProfit'] = new_takeProfit
            self.__save()
        except Exception as err:
            logging.warning(err)

    def get_stopLoss(self) -> int:
        return self.db['user']['stopLoss']

    def set_stopLoss(self, new_stopLoss: str):
        try:
            self.db['user']['stopLoss'] = new_stopLoss
            self.__save()
        except Exception as err:
            logging.warning(err)

    def get_quantity(self) -> int:
        return self.db['user']['quantity']

    def set_quantity(self, new_quantity: str):
        try:
            self.db['user']['quantity'] = new_quantity
            self.__save()
        except Exception as err:
            logging.warning(err)

    def set_leverage_by_symbol(self, coin: str, new_leverage: int = None):
        """ Устанавливает значение монета:множитель, если множитель не передан то удаляет переданную монету из БД """
        if "USDT" not in coin:
            coin += "USDT"

        try:
            if new_leverage is None:
                del self.db['leverage_by_symbol'][coin]
            else:
                self.db['leverage_by_symbol'][coin] = new_leverage
            self.__save()
        except Exception as err:
            logging.warning(f"{err} - {coin, type(coin)} {new_leverage, type(new_leverage)}")

    def get_leverage_by_symbol(self):
        info_of_leverage_by_symbol = '<b>Кредитные плечи для каждой пары:</b>\n'
        try:
            leverage_by_symbol = ''
            for pair, leverage in self.db["leverage_by_symbol"].items():
                leverage_by_symbol += f"{pair}, плечо {leverage}x\n"

            return info_of_leverage_by_symbol + 'Нет измененных кредитных плеч, либо они все установленны в значение 10' \
                if leverage_by_symbol == '' else info_of_leverage_by_symbol + leverage_by_symbol
        except Exception as e:
            logging.warning(e)
            return "Нет открытых позиций/Ошибка получения данных"


db = DBConnect()


def test():
    db.set_leverage_by_symbol('BTC', 2)
    ...


if __name__ == '__main__':
    test()
