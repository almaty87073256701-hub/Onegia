from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .db import DbConfig, DatabaseError, Totals, fetch_totals

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReportWindow:
    report_date: date
    data_date: date
    period_start: date
    period_end: date


@dataclass(frozen=True)
class ReportNumbers:
    daily: Totals
    mtd: Totals
    forecast_issued: int | None
    forecast_income: float | None
    days_passed: int
    days_in_month: int


def _get_days_in_month(value: date) -> int:
    next_month = (value.replace(day=28) + timedelta(days=4)).replace(day=1)
    return (next_month - timedelta(days=1)).day


def get_report_window(now: date) -> ReportWindow:
    report_date = now
    data_date = report_date - timedelta(days=1)

    if report_date.day == 1:
        data_date = report_date.replace(day=1) - timedelta(days=1)

    period_start = data_date.replace(day=1)
    period_end = data_date

    return ReportWindow(
        report_date=report_date,
        data_date=data_date,
        period_start=period_start,
        period_end=period_end,
    )


def compute_report_numbers(config: DbConfig, window: ReportWindow) -> ReportNumbers:
    daily = fetch_totals(config, window.data_date, window.data_date)
    mtd = fetch_totals(config, window.period_start, window.period_end)

    days_passed = (window.period_end - window.period_start).days + 1
    days_in_month = _get_days_in_month(window.period_end)

    forecast_issued: int | None
    forecast_income: float | None

    if days_passed <= 0 or mtd.issued is None or mtd.income is None:
        forecast_issued = None
        forecast_income = None
    else:
        avg_issued = mtd.issued / days_passed
        avg_income = mtd.income / days_passed
        forecast_issued = round(avg_issued * days_in_month)
        forecast_income = round(avg_income * days_in_month, 2)

    return ReportNumbers(
        daily=daily,
        mtd=mtd,
        forecast_issued=forecast_issued,
        forecast_income=forecast_income,
        days_passed=days_passed,
        days_in_month=days_in_month,
    )


def format_date(value: date) -> str:
    return value.strftime("%d.%m.%Y")


def format_period(start: date, end: date) -> str:
    return f"{start:%d}–{end:%d.%m}"


def format_issued(value: float | None) -> str:
    if value is None:
        return "нет данных"
    return f"{int(round(value)):,}".replace(",", " ")


def format_income(value: float | None) -> str:
    if value is None:
        return "нет данных"
    return f"{value:,.2f}".replace(",", " ")


def format_forecast_issued(value: int | None) -> str:
    if value is None:
        return "н/д"
    return f"{value:,}".replace(",", " ")


def format_forecast_income(value: float | None) -> str:
    if value is None:
        return "н/д"
    return f"{value:,.2f}".replace(",", " ")


MONTHS_RU = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)


def build_report_message(window: ReportWindow, numbers: ReportNumbers) -> str:
    report_date = format_date(window.report_date)
    data_date = format_date(window.data_date)
    period = format_period(window.period_start, window.period_end)
    month_label = MONTHS_RU[window.period_end.month - 1]

    message = (
        f"Отчёт на {report_date}\n"
        f"(данные за {data_date}, период {period})\n\n"
        f"Факт за {data_date}\n"
        f"• Выдачи: {format_issued(numbers.daily.issued)}\n"
        f"• Доход: {format_income(numbers.daily.income)}\n\n"
        f"Факт с начала месяца ({period})\n"
        f"• Выдачи: {format_issued(numbers.mtd.issued or 0)}\n"
        f"• Доход: {format_income(numbers.mtd.income or 0)}\n\n"
        f"Прогноз до конца {month_label}\n"
        f"• Выдачи: {format_forecast_issued(numbers.forecast_issued)}\n"
        f"• Доход: {format_forecast_income(numbers.forecast_income)}"
    )

    return message


def get_today_in_timezone(timezone: str) -> date:
    return datetime.now(ZoneInfo(timezone)).date()


def generate_report(config: DbConfig, timezone: str) -> str:
    today = get_today_in_timezone(timezone)
    window = get_report_window(today)

    try:
        numbers = compute_report_numbers(config, window)
    except DatabaseError:
        raise

    logger.info(
        "Report computed: day=%s, mtd=%s, forecast=(%s, %s)",
        numbers.daily,
        numbers.mtd,
        numbers.forecast_issued,
        numbers.forecast_income,
    )

    return build_report_message(window, numbers)
