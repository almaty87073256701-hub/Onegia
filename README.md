# Brokerage Telegram Report Bot

Telegram-бот отправляет ежедневный отчёт по продажам Brokerage в группу в 09:00 (Asia/Almaty).

## Возможности

- Формирует отчёт за вчера, MTD и линейный прогноз на конец месяца.
- Отправляет сообщение в Telegram по фиксированному формату.
- Логирует запуск, значения и статус отправки.

## Требования

- Python 3.11+
- Доступ к БД только на чтение
- Драйвер для вашей БД (например, `psycopg` для PostgreSQL или `pymysql` для MySQL)

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Переменные окружения

```bash
export BOT_TOKEN="..."
export CHAT_ID="-5231217447"
export DB_URL="postgresql+psycopg://user:pass@host:5432/dbname"
export DB_TABLE="sales"
export DB_DATE_COLUMN="operation_date"
export DB_ISSUED_COLUMN="issued_amount"
export DB_INCOME_COLUMN="income_amount"
export DB_PRODUCT_COLUMN="product_type"
export DB_PRODUCT_VALUE="Brokerage"
export BOT_TIMEZONE="Asia/Almaty"
```

> `BOT_TIMEZONE` опционален. По умолчанию используется `Asia/Almaty`.

## Запуск

Одноразовый запуск (для проверки):

```bash
python -m brokerage_report_bot.main --once
```

Постоянный запуск по расписанию:

```bash
python -m brokerage_report_bot.main
```

## Формат сообщения

```
Отчёт на DD.MM.YYYY
(данные за DD.MM.YYYY, период DD–DD.MM)

Факт за DD.MM.YYYY
• Выдачи: X
• Доход: Y

Факт с начала месяца (DD–DD.MM)
• Выдачи: X_MTD
• Доход: Y_MTD

Прогноз до конца <месяц>
• Выдачи: X_FC
• Доход: Y_FC
```

## Примечания по БД

- Бот использует только чтение.
- В таблице должны быть поля даты операции, выдачи, дохода и признак продукта `Brokerage`.
- Если за день несколько записей — значения суммируются.
