import json
import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from iods.api.schemas import IngestEnvelope, IngestResponse
from iods.db.models import DlqEvent, RawEvent, Transaction

logger = logging.getLogger(__name__)

ALLOWED_STATUSES = {"PENDING", "SETTLED", "FAILED", "REVERSED"}


class ProcessingError(ValueError):
    def __init__(self, reason_code: str, detail: str):
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(detail)



def _to_canonical_transaction(envelope: IngestEnvelope) -> Transaction:
    payload = envelope.payload
    required_fields = {"transaction_id", "account_id", "amount", "currency", "status"}
    missing = required_fields - payload.keys()
    if missing:
        raise ProcessingError("missing_required_field", f"missing fields: {sorted(missing)}")

    try:
        amount = Decimal(str(payload["amount"]))
    except (InvalidOperation, TypeError) as exc:
        raise ProcessingError("invalid_amount", "amount must be a valid decimal") from exc

    if amount < Decimal("0"):
        raise ProcessingError("negative_amount", "amount must be non-negative")

    currency = str(payload["currency"]).upper()
    if len(currency) != 3:
        raise ProcessingError("invalid_currency", "currency must be 3-letter ISO code")

    status = str(payload["status"]).upper()
    if status not in ALLOWED_STATUSES:
        raise ProcessingError("invalid_status", f"status must be one of {sorted(ALLOWED_STATUSES)}")

    event_time = envelope.event_time
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)

    return Transaction(
        transaction_id=str(payload["transaction_id"]),
        source_transaction_id=str(payload.get("source_transaction_id", payload["transaction_id"])),
        account_id=str(payload["account_id"]),
        amount=amount,
        currency=currency,
        status=status,
        event_time=event_time,
        processed_time=datetime.now(tz=timezone.utc),
        source_system=envelope.source_system,
        lineage_event_id=envelope.event_id,
    )



def process_ingestion(envelope: IngestEnvelope, session: Session) -> IngestResponse:
    raw = RawEvent(
        event_id=envelope.event_id,
        source_system=envelope.source_system,
        entity_type=envelope.entity_type,
        schema_version=envelope.schema_version,
        event_time=envelope.event_time,
        idempotency_key=envelope.idempotency_key,
        payload_json=json.dumps(envelope.payload),
    )

    session.add(raw)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.info("duplicate event id", extra={"event_id": envelope.event_id})
        return IngestResponse(status="duplicate", event_id=envelope.event_id)

    session.refresh(raw)

    try:
        canonical = _to_canonical_transaction(envelope)
    except ProcessingError as exc:
        dlq = DlqEvent(
            event_id=envelope.event_id,
            failed_stage="processing",
            reason_code=exc.reason_code,
            reason_details=exc.detail,
            payload_snapshot=raw.payload_json,
        )
        session.add(dlq)
        session.commit()
        return IngestResponse(status="dlq", event_id=envelope.event_id, reason_code=exc.reason_code)

    existing = session.exec(select(Transaction).where(Transaction.transaction_id == canonical.transaction_id)).first()
    if existing:
        if canonical.event_time > existing.event_time:
            existing.source_transaction_id = canonical.source_transaction_id
            existing.account_id = canonical.account_id
            existing.amount = canonical.amount
            existing.currency = canonical.currency
            existing.status = canonical.status
            existing.event_time = canonical.event_time
            existing.processed_time = canonical.processed_time
            existing.source_system = canonical.source_system
            existing.lineage_event_id = canonical.lineage_event_id
            session.add(existing)
            session.commit()
            return IngestResponse(
                status="processed",
                event_id=envelope.event_id,
                transaction_id=existing.transaction_id,
            )

        return IngestResponse(status="duplicate", event_id=envelope.event_id, transaction_id=existing.transaction_id)

    session.add(canonical)
    session.commit()

    return IngestResponse(status="processed", event_id=envelope.event_id, transaction_id=canonical.transaction_id)
