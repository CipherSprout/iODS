from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class IngestEnvelope(BaseModel):
    event_id: str
    source_system: str
    entity_type: str
    schema_version: str
    event_time: datetime
    payload: dict[str, Any]
    idempotency_key: str


class TransactionResponse(BaseModel):
    transaction_id: str
    account_id: str
    amount: Decimal
    currency: str
    status: str
    event_time: datetime
    source_system: str


class IngestResponse(BaseModel):
    status: str = Field(description="processed|duplicate|dlq")
    event_id: str
    transaction_id: str | None = None
    reason_code: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
