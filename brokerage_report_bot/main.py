from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import load_settings
from .db import DbConfig, DatabaseError
from .report import generate_report
from .telegram import TelegramConfig, TelegramError, send_message


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def run_report() -> None:
    settings = load_settings()

    db_config = DbConfig(
        url=settings.db_url,
        table=settings.db_table,
        date_column=settings.db_date_column,
        issued_column=settings.db_issued_column,
        income_column=settings.db_income_column,
        product_column=settings.db_product_column,
        product_value=settings.db_product_value,
    )

    telegram_config = TelegramConfig(
        bot_token=settings.bot_token,
        chat_id=settings.chat_id,
    )

    try:
        message = generate_report(db_config, settings.timezone)
    except DatabaseError:
        logging.error("Report not sent due to database error")
        return

    try:
        send_message(telegram_config, message)
    except TelegramError:
        logging.error("Report not sent due to Telegram error")


def schedule_reports(timezone: str) -> None:
    scheduler = BackgroundScheduler(timezone=ZoneInfo(timezone))
    trigger = CronTrigger(hour=9, minute=0, timezone=ZoneInfo(timezone))
    scheduler.add_job(run_report, trigger)
    scheduler.start()

    logging.info("Scheduler started for 09:00 %s", timezone)

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brokerage report bot")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run report immediately and exit",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    configure_logging()
    args = parse_args(argv or sys.argv[1:])
    settings = load_settings()

    if args.once:
        logging.info("Running report once at %s", datetime.now())
        run_report()
        return

    schedule_reports(settings.timezone)


if __name__ == "__main__":
    main()
