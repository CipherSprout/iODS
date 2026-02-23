from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from iods.api.deps import require_api_key
from iods.api.schemas import HealthResponse, IngestEnvelope, IngestResponse, TransactionResponse
from iods.core.config import get_settings
from iods.db.models import Transaction
from iods.db.session import get_session
from iods.services.processing import process_ingestion

router = APIRouter(prefix="/v1")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)


@router.post("/ingest", response_model=IngestResponse, dependencies=[Depends(require_api_key)])
def ingest(envelope: IngestEnvelope, session: Session = Depends(get_session)) -> IngestResponse:
    return process_ingestion(envelope, session)


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    dependencies=[Depends(require_api_key)],
)
def get_transaction(transaction_id: str, session: Session = Depends(get_session)) -> TransactionResponse:
    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="transaction not found")

    return TransactionResponse(
        transaction_id=tx.transaction_id,
        account_id=tx.account_id,
        amount=tx.amount,
        currency=tx.currency,
        status=tx.status,
        event_time=tx.event_time,
        source_system=tx.source_system,
    )


@router.get(
    "/accounts/{account_id}/transactions",
    response_model=list[TransactionResponse],
    dependencies=[Depends(require_api_key)],
)
def get_account_transactions(
    account_id: str,
    from_time: datetime | None = Query(default=None, alias="from"),
    to_time: datetime | None = Query(default=None, alias="to"),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[TransactionResponse]:
    statement = select(Transaction).where(Transaction.account_id == account_id)

    if from_time is not None:
        statement = statement.where(Transaction.event_time >= from_time)
    if to_time is not None:
        statement = statement.where(Transaction.event_time <= to_time)

    statement = statement.order_by(Transaction.event_time.desc()).limit(limit)
    txs = session.exec(statement).all()

    return [
        TransactionResponse(
            transaction_id=tx.transaction_id,
            account_id=tx.account_id,
            amount=tx.amount,
            currency=tx.currency,
            status=tx.status,
            event_time=tx.event_time,
            source_system=tx.source_system,
        )
        for tx in txs
    ]
