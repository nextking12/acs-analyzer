from enum import StrEnum

from pydantic import BaseModel


class Severity(StrEnum):
    HIGH = "High"
    MEDIUM = "Medium"


class Finding(BaseModel):
    rule_id: str
    rule_name: str
    severity: Severity
    source_row: int
    cardholder_name: str | None
    badge_number: str | None
    description: str
    recommended_action: str
    source_data: dict[str, str | None]
