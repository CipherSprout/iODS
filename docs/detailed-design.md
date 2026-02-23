# iODS Detailed Design

## 1. Purpose
This document provides detailed design specifications for the iODS architecture, including component internals, APIs, data contracts, processing logic, and operational procedures.

## 2. Component Breakdown

### 2.1 Ingestion Service

#### Responsibilities
- Accept source data via streaming, CDC, and batch interfaces.
- Validate envelope-level metadata.
- Generate ingestion metadata and route records.

#### Internal Modules
- **Connector Adapters:** source-specific protocol handlers.
- **Envelope Validator:** checks required headers and schema version.
- **Dedup Filter:** validates idempotency key uniqueness within time window.
- **Dispatcher:** writes to raw store and publish queue.

#### Input Contract (Envelope)
| Field | Type | Required | Description |
|---|---|---:|---|
| event_id | string | Yes | Globally unique message ID |
| source_system | string | Yes | Source name identifier |
| entity_type | string | Yes | Domain entity type |
| schema_version | string | Yes | Payload schema version |
| event_time | datetime | Yes | Event creation timestamp |
| payload | object | Yes | Source-specific data |
| idempotency_key | string | Yes | Deduplication key |

#### Error Handling
- Invalid envelope -> reject and log reason.
- Duplicate idempotency key -> acknowledge/no-op and metric increment.
- Temporary downstream failure -> retry with exponential backoff.

### 2.2 Raw Data Writer

#### Responsibilities
- Persist immutable raw records.
- Partition data for efficient replay and discovery.

#### Storage Layout
`raw/{source_system}/{entity_type}/dt=YYYY-MM-DD/hour=HH/part-*.json`

#### Metadata Stored per Record
- ingestion_timestamp
- ingestion_partition
- source_offset_or_sequence
- checksum

### 2.3 Processing Engine

#### Pipeline Stages
1. **Deserialize & Validate** against schema registry.
2. **Normalize** field names, units, and enumerations.
3. **Enrich** via reference datasets.
4. **Business Validation** (domain constraints).
5. **Publish Curated Entity** or route to DLQ.

#### Pseudocode
```pseudo
for record in raw_stream:
  envelope = parse(record)
  if !schema_registry.validate(envelope):
    dlq.write(record, reason="schema_validation_failed")
    continue

  normalized = normalizer.apply(envelope.payload)
  enriched = enricher.apply(normalized)

  violations = rule_engine.evaluate(enriched)
  if violations.exists:
    dlq.write(record, reason="business_rule_failed", details=violations)
    continue

  canonical = mapper.to_canonical(enriched)
  curated_store.upsert(canonical)
```

### 2.4 Curated Store Writer

#### Canonical Entity Example: `transaction`
| Field | Type | Description |
|---|---|---|
| transaction_id | string | Canonical ID |
| source_transaction_id | string | Source-level identifier |
| account_id | string | Canonical account ID |
| amount | decimal(18,2) | Monetary amount |
| currency | string(3) | ISO currency |
| status | string | Normalized status |
| event_time | datetime | Domain event time |
| processed_time | datetime | Processing completion time |
| source_system | string | Origin source |
| lineage_event_id | string | Link to raw envelope |

#### Upsert Strategy
- Primary key: `transaction_id`.
- Conflict resolution: latest `event_time`, tie-breaker by ingestion timestamp.
- Optional SCD Type 2 for entities requiring history.

### 2.5 Serving API

#### Endpoint Set (v1)
- `GET /v1/transactions/{transaction_id}`
- `GET /v1/accounts/{account_id}/transactions?from=&to=&limit=`
- `GET /v1/health`

#### Transaction Lookup Response
```json
{
  "transaction_id": "tx_1001",
  "account_id": "acc_2001",
  "amount": 125.50,
  "currency": "USD",
  "status": "SETTLED",
  "event_time": "2026-01-10T12:30:00Z",
  "source_system": "core_banking"
}
```

#### API Non-Functional Constraints
- p95 < 300ms for single-record lookup.
- Hard timeout 2s.
- Rate limiting via token bucket per client/app.

### 2.6 Metadata, Lineage, and Schema Registry

#### Metadata Model
- dataset_name
- owner_team
- pii_classification
- retention_policy
- schema_versions[]
- sla_targets

#### Lineage Events
- `ingested`
- `validated`
- `normalized`
- `curated_written`
- `served`

## 3. Data Quality Framework

### 3.1 Rule Classes
- Completeness checks (required fields present).
- Validity checks (format/domain constraints).
- Consistency checks (cross-field relationships).
- Freshness checks (event delay thresholds).

### 3.2 Rule Execution Policy
- Blocker rules fail pipeline and route to DLQ.
- Warning rules pass with annotation and metric emission.

### 3.3 Quality Metrics
- Null rate by field.
- Rule failure rate by source.
- Late-event percentage.
- Duplicate event rate.

## 4. DLQ and Replay Design

### DLQ Record Schema
| Field | Type | Description |
|---|---|---|
| event_id | string | Original event ID |
| failed_stage | string | Stage of failure |
| reason_code | string | Machine-readable reason |
| reason_details | object | Additional diagnostics |
| failed_at | datetime | Failure timestamp |
| payload_snapshot | object | Original payload |

### Replay Workflow
1. Operator selects DLQ records by reason/source/date.
2. Corrective mapping or schema patch applied.
3. Replay job republishes records to processing input.
4. Replay outcome audited with trace IDs.

## 5. Observability Design

### Metrics
- ingestion_requests_total
- ingestion_failures_total
- processing_latency_seconds
- curated_upsert_failures_total
- api_request_duration_seconds

### Logging
- Structured logs with trace_id, event_id, component, severity.
- Redaction middleware for sensitive fields.

### Tracing
- Distributed trace propagated from ingestion through serving.

### Alerting
- Error-rate threshold breach.
- Pipeline lag beyond SLA.
- API latency above p95 target sustained for N minutes.

## 6. Security Detailed Design

### Authentication and Authorization
- OAuth2/JWT for client-facing APIs.
- mTLS + service identity for internal service-to-service calls.
- RBAC policies mapped to datasets and API scopes.

### Data Protection
- AES-256 at rest.
- TLS 1.2+ in transit.
- Column-level masking for sensitive fields in non-prod.

### Audit
- Immutable access logs.
- Periodic access review reports.

## 7. Operational Runbooks (Initial)

### Pipeline Backlog Spike
1. Confirm queue depth and consumer lag.
2. Scale processing workers.
3. Verify downstream store write throughput.
4. Trigger backlog alert incident if SLA breach likely.

### Elevated DLQ Rate
1. Identify failing source and reason code.
2. Compare with recent schema/deployment changes.
3. Roll back offending transform if required.
4. Replay corrected records.

## 8. Release and Change Management
- Version all external contracts (envelope + APIs).
- Backward-compatible changes preferred.
- Breaking changes require migration plan and dual-write/read phase.

## 9. Traceability Matrix
| Requirement | Architecture Section | Detailed Design Section |
|---|---|---|
| Scalable ingestion | 6.1, 8 | 2.1, 2.2 |
| Data quality enforcement | 6.3, 13 | 2.3, 3 |
| Low-latency serving | 6.5, 8 | 2.5 |
| Security/compliance | 9 | 6 |
| Operational resiliency | 11 | 4, 5, 7 |

## 10. Implementation Roadmap (Phased)
- **Phase 1:** Ingestion + raw storage + minimal curated model.
- **Phase 2:** Rule engine, DLQ, replay tools, and observability dashboards.
- **Phase 3:** API hardening, schema governance automation, and performance tuning.
