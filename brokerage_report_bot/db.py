from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class DbConfig:
    url: str
    table: str
    date_column: str
    issued_column: str
    income_column: str
    product_column: str
    product_value: str


@dataclass(frozen=True)
class Totals:
    issued: float | None
    income: float | None


class DatabaseError(RuntimeError):
    pass


def _validate_identifier(name: str, label: str) -> str:
    if not IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid {label} identifier: {name}")
    return name


def _build_query(config: DbConfig) -> str:
    table = _validate_identifier(config.table, "table")
    date_col = _validate_identifier(config.date_column, "date column")
    issued_col = _validate_identifier(config.issued_column, "issued column")
    income_col = _validate_identifier(config.income_column, "income column")
    product_col = _validate_identifier(config.product_column, "product column")

    return (
        "SELECT SUM(" + issued_col + ") AS issued, "
        "SUM(" + income_col + ") AS income "
        "FROM " + table + " "
        "WHERE " + date_col + " >= :start_date AND " + date_col + " <= :end_date "
        "AND " + product_col + " = :product_value"
    )


def fetch_totals(config: DbConfig, start_date: date, end_date: date) -> Totals:
    query = _build_query(config)
    logger.debug("Executing query for %s - %s", start_date, end_date)

    try:
        engine = create_engine(config.url)
        with engine.connect() as connection:
            result = connection.execute(
                text(query),
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "product_value": config.product_value,
                },
            ).mappings().first()
    except Exception as exc:  # noqa: BLE001 - custom error surface
        logger.exception("Database query failed")
        raise DatabaseError("Database query failed") from exc

    if not result:
        return Totals(issued=None, income=None)

    return Totals(
        issued=result.get("issued"),
        income=result.get("income"),
    )
