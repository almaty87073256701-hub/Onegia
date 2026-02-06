from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    chat_id: str
    db_url: str
    db_table: str
    db_date_column: str
    db_issued_column: str
    db_income_column: str
    db_product_column: str
    db_product_value: str
    timezone: str


REQUIRED_ENV_VARS = (
    "BOT_TOKEN",
    "CHAT_ID",
    "DB_URL",
    "DB_TABLE",
    "DB_DATE_COLUMN",
    "DB_ISSUED_COLUMN",
    "DB_INCOME_COLUMN",
    "DB_PRODUCT_COLUMN",
    "DB_PRODUCT_VALUE",
)


def load_settings() -> Settings:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Settings(
        bot_token=os.environ["BOT_TOKEN"],
        chat_id=os.environ["CHAT_ID"],
        db_url=os.environ["DB_URL"],
        db_table=os.environ["DB_TABLE"],
        db_date_column=os.environ["DB_DATE_COLUMN"],
        db_issued_column=os.environ["DB_ISSUED_COLUMN"],
        db_income_column=os.environ["DB_INCOME_COLUMN"],
        db_product_column=os.environ["DB_PRODUCT_COLUMN"],
        db_product_value=os.environ["DB_PRODUCT_VALUE"],
        timezone=os.getenv("BOT_TIMEZONE", "Asia/Almaty"),
    )
