from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from random import randint

import requests

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    chat_id: str


class TelegramError(RuntimeError):
    pass


def send_message(config: TelegramConfig, message: str, retries: int = 3) -> None:
    url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
    payload = {
        "chat_id": config.chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=20)
            if response.ok:
                logger.info("Message sent successfully")
                return
            logger.warning(
                "Telegram API responded with status %s: %s",
                response.status_code,
                response.text,
            )
        except requests.RequestException:
            logger.exception("Failed to send message to Telegram")

        if attempt < retries:
            sleep_for = randint(60, 120)
            logger.info("Retrying Telegram send in %s seconds", sleep_for)
            time.sleep(sleep_for)

    raise TelegramError("Failed to send message after retries")
