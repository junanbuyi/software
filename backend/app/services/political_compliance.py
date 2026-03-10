from __future__ import annotations

from typing import Iterable

from app.models.dataset import Dataset
from app.models.dataset_record import DatasetRecord


POLITICAL_SENSITIVE_TERMS = (
    "台独",
    "港独",
    "藏独",
    "疆独",
    "分裂国家",
    "颠覆国家政权",
    "法轮功",
    "暴恐",
    "恐怖袭击",
)


def _contains_sensitive_term(text: str) -> str | None:
    normalized = text.strip().lower()
    if not normalized:
        return None
    for term in POLITICAL_SENSITIVE_TERMS:
        if term.lower() in normalized:
            return term
    return None


def check_dataset_political_compliance(
    dataset: Dataset,
    records: Iterable[DatasetRecord],
) -> tuple[bool, str]:
    """
    Returns:
        (is_compliant, reason)
    """
    text_fields = [
        ("dataset.name", dataset.name or ""),
        ("dataset.description", dataset.description or ""),
    ]

    for record in records:
        weather_text = record.weather_type or ""
        if weather_text:
            text_fields.append((f"record[{record.id}].weather_type", weather_text))

    for field_name, field_value in text_fields:
        hit = _contains_sensitive_term(field_value)
        if hit:
            return False, f"{field_name} contains sensitive term: {hit}"

    return True, ""
