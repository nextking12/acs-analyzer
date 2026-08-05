from datetime import date
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


class AnalysisSummary(BaseModel):
    analysis_date: date
    records_analyzed: int
    active_credentials: int
    inactive_credentials: int
    other_status_credentials: int
    total_findings: int
    findings_by_severity: dict[Severity, int]
    findings_by_rule: dict[str, int]
