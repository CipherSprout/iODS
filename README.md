# iODS (Intelligent Operational Data Store)

Production-ready baseline implementation of an ODS service with:

- Event ingestion endpoint with envelope validation.
- Raw immutable event storage.
- Canonical transaction processing with validation rules.
- DLQ handling for failed business-rule processing.
- Query APIs for transaction and account transaction history.
- Health endpoint, configurable API-key auth, and structured logging.

## Repository Layout

- `src/iods/main.py` - FastAPI application entrypoint.
- `src/iods/api/` - API routes, schemas, and dependencies.
- `src/iods/services/processing.py` - ingestion and transformation pipeline logic.
- `src/iods/db/` - SQLModel models and DB session management.
- `docs/architecture-design.md` - architecture design.
- `docs/detailed-design.md` - detailed design.

## Quick Start

### 1) Install dependencies

```bash
pip install -e .[dev]
```

### 2) Run service

```bash
uvicorn iods.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3) Example ingest request

```bash
curl -X POST "http://localhost:8000/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt-1001",
    "source_system": "core_banking",
    "entity_type": "transaction",
    "schema_version": "1.0",
    "event_time": "2026-01-10T12:30:00Z",
    "idempotency_key": "idem-1001",
    "payload": {
      "transaction_id": "tx-1001",
      "source_transaction_id": "src-tx-1001",
      "account_id": "acc-2001",
      "amount": "125.50",
      "currency": "USD",
      "status": "SETTLED"
    }
  }'
```

### 4) Query transaction

```bash
curl "http://localhost:8000/v1/transactions/tx-1001"
```

## Configuration

Environment variables:

- `ENV` (default: `dev`)
- `LOG_LEVEL` (default: `INFO`)
- `DATABASE_URL` (default: `sqlite:///./iods.db`)
- `IODS_API_KEY` (default: empty; when set, clients must send `X-API-Key`)

See `.env.example`.

## Quality Gates

```bash
ruff check .
pytest -q
```

## Container

```bash
docker compose up --build
```

## Design References

- [Architecture Design](docs/architecture-design.md)
- [Detailed Design](docs/detailed-design.md)
