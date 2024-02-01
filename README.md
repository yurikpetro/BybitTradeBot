<h1 style="text-align:center;">BybitTradeBot</h1>

> **Бот для автоматизации выставления ордеров long и short на платформе bybit, основной функционал реализовывался для работы с группой @RoseSignalsPremium.   
> Бот умеет менять плечи, сумму для закупок, показывать историю транзакций и многое другое**

> **Авторы: [KittyByte](https://github.com/KittyByte) и [yurikpetro](https://github.com/yurikpetro)**

## Возможности

- установка плеча(множитель), сумму для закупки, Stop-loss и Take-profit
- показывать историю(мах лимит указывается в TradeHelper.limit_history) и открытые позиции
- отображение текущих настроек

## Стек технологий

- Python3
- [Aiogram2](https://docs.aiogram.dev/)
- [Pyrogram](https://docs.pyrogram.org/)
- Threading
- [Pybit](https://pypi.org/project/pybit/)

## Инструкция по развертыванию бота

1. Зарегистрируйте бота в Telegram с помощью [@BotFather](https://t.me/BotFather) и получите API-токен бота.
2. Перейдите на [Telegram Core API](https://core.telegram.org/api/obtaining_api_id) и зарегистрируйте свое приложение для получения API ID и API Hash.
3. Создайте аккаунт в ByBit переходите к разделу API, создаете "API ключи, созданные системой" даете разрешения(почти все), также получаете API_KEY и API_SECRET
4. Установите необходимые зависимости:
   ```sh
   pip install -r requirements.txt
   ```
5. Настройте config, замените параметры соответствующими вам значениями.
   ```
   Данные из аккаунта ByBit
   TESTNET_BYBIT - ставя значение True вы работаете с тестовой сетью где используются не настоящие деньги, False - настроящие
   BYBIT_API_KEY - получаем на шаге №3
   BYBIT_API_SECRET - получаем на шаге №3

   конфигурация бота
   BOT_TOKEN - токен вашего бота, токен можно получить в шаге №1
   CHAT_ID_FOR_LOGS и CHAT_ID_FOR_LOGS_THREAD_ID - id группы и id топика для логов, если вы их не ведете ставьте в значение 0 
   
   Параметры для работы с userbot'ом. Эти данные можно получить в шаге №2
   USERBOT_API_ID - на шаге №2
   USERBOT_API_HASH - на шаге №2

   CHAT_ID_FOR_PARSING - id/username чата от куда парсится фото с информацией о покупке
   ```

6. Перейдите в trade.py - do_futures_trade и измените его под ваши нужды, в нем находится логика при котором запускается выставление ордера
7. Измените DB.json в поле "tg_id" укажите id главного пользователя, в "admins_id" тех кто также будут иметь доступ к боту
8. Запустите бота.
9. Теперь ваш бот готов для автоматизации выставления ордеров!

---
### Команды доступные у бота:
  - /start - перезапуск бота
  - /help - информацию по работе
---

## Пример работы бота: 
<p align="center">
  <img src="imgs\example1.png" alt="example1.png" width="350">
  <img src="imgs\example2.png" alt="example2.png" width="350">
</p>

<div style="text-align:center;"><h1> Удачи с Вашим BybitTradeBot!</h1></div>
