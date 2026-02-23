from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column
from sqlalchemy.types import Numeric
from sqlmodel import Field, SQLModel


class RawEvent(SQLModel, table=True):
    __tablename__ = "raw_events"

    id: int | None = Field(default=None, primary_key=True)
    event_id: str = Field(index=True, unique=True)
    source_system: str = Field(index=True)
    entity_type: str = Field(index=True)
    schema_version: str
    event_time: datetime
    idempotency_key: str = Field(index=True)
    payload_json: str
    ingested_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    transaction_id: str = Field(primary_key=True)
    source_transaction_id: str
    account_id: str = Field(index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(18, 2), nullable=False))
    currency: str = Field(min_length=3, max_length=3)
    status: str = Field(index=True)
    event_time: datetime = Field(index=True)
    processed_time: datetime = Field(default_factory=datetime.utcnow)
    source_system: str
    lineage_event_id: str = Field(index=True)


class DlqEvent(SQLModel, table=True):
    __tablename__ = "dlq_events"

    id: int | None = Field(default=None, primary_key=True)
    event_id: str = Field(index=True)
    failed_stage: str
    reason_code: str = Field(index=True)
    reason_details: str
    payload_snapshot: str
    failed_at: datetime = Field(default_factory=datetime.utcnow)
