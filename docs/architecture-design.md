# iODS Architecture Design

## 1. Purpose
This document defines the target architecture for **iODS** (Intelligent Operational Data Store), a platform for ingesting, normalizing, storing, and serving operational data for analytics and downstream applications.

## 2. Goals and Non-Goals

### Goals
- Provide a scalable and resilient data ingestion and processing architecture.
- Offer low-latency query access to curated operational entities.
- Support near-real-time and batch workloads.
- Enable observability, governance, and secure access patterns.

### Non-Goals
- Building a BI/reporting UI in the first phase.
- Replacing source-of-truth transactional systems.
- Supporting arbitrary ad-hoc ETL pipelines without governance.

## 3. Architectural Drivers
- **Scalability:** Handle increasing data volumes and source integrations.
- **Availability:** Ensure critical data APIs remain available under failure scenarios.
- **Data Quality:** Detect malformed events and enforce schema contracts.
- **Extensibility:** Add new sources, transformations, and consumers with minimal coupling.
- **Security & Compliance:** Protect data-in-transit and at-rest; ensure least privilege.

## 4. Context and Scope

### 4.1 System Context
iODS sits between upstream producer systems and downstream consumers:
- **Upstream:** transactional applications, logs/events, partner feeds.
- **Core iODS:** ingestion, processing, storage, serving, governance.
- **Downstream:** API clients, analytics engines, data science pipelines.

### 4.2 In-Scope
- Data ingestion interfaces and contracts.
- Stream/batch processing and canonical modeling.
- Storage layers for raw, curated, and serving datasets.
- Internal service APIs and query endpoints.
- Observability and operational controls.

### 4.3 Out-of-Scope
- Consumer-specific dashboard definitions.
- Domain-specific business-rule proliferation outside managed transform modules.

## 5. High-Level Architecture

```text
[Source Systems]
   |  (events, CDC, files, APIs)
   v
[Ingestion Layer] ---> [Raw Storage]
   |                        |
   v                        v
[Processing & Validation] -> [Curated Storage]
   |                               |
   +-------------> [Serving Layer/API] ---> [Consumers]

Cross-cutting: Security, Metadata Catalog, Observability, CI/CD
```

## 6. Logical Components

### 6.1 Ingestion Layer
Responsibilities:
- Receive events/messages/files.
- Perform initial syntactic validation.
- Apply idempotency keys and dedup envelopes.
- Route to raw persistence and processing queues.

Interfaces:
- Streaming endpoint (topic-based).
- Batch file drop/API endpoint.
- CDC connector interface.

### 6.2 Raw Storage
Responsibilities:
- Immutable, append-only source payload persistence.
- Replay support for reprocessing.
- Retention controls and archival policies.

Characteristics:
- Partitioned by source and ingestion timestamp.
- Schema-on-read for forensic recovery.

### 6.3 Processing & Validation Layer
Responsibilities:
- Schema validation and drift detection.
- Data cleansing, normalization, enrichment.
- Business rule validation.
- Error classification and dead-letter routing.

Patterns:
- Stateless transforms for simple mapping.
- Stateful aggregations with windowing where needed.

### 6.4 Curated Storage
Responsibilities:
- Store canonical, query-optimized entities.
- Support historical versioning where required.
- Enforce schema evolution lifecycle.

Data model:
- Canonical entities (e.g., customer, account, transaction, event).
- Surrogate keys and source lineage references.

### 6.5 Serving Layer
Responsibilities:
- Expose low-latency APIs and query interfaces.
- Apply authorization and throttling policies.
- Materialize read models for common access patterns.

Interfaces:
- REST/GraphQL APIs.
- Internal SQL endpoint for controlled analytics use.

### 6.6 Metadata & Governance
Responsibilities:
- Track schema registry, lineage, ownership.
- Record quality checks and SLA metrics.
- Manage retention and compliance tags.

### 6.7 Observability & Operations
Responsibilities:
- Metrics, logs, traces, and alerting.
- Pipeline health dashboards.
- Automated rollback and replay procedures.

## 7. Data Flow (End-to-End)
1. Producer emits event or publishes batch payload.
2. Ingestion adapter validates envelope and writes to raw storage.
3. Processing jobs consume raw records and enforce schema contracts.
4. Valid records are transformed into canonical models and written to curated storage.
5. Serving layer updates/materializes read models and serves queries.
6. Invalid records are routed to dead-letter queues with diagnostics.
7. Observability pipeline emits processing latency, quality, and availability metrics.

## 8. Non-Functional Requirements
- **Availability:** 99.9% uptime target for serving APIs.
- **Durability:** No data loss for committed ingestion requests.
- **Latency:**
  - Near-real-time data visibility within 5 minutes.
  - API p95 response under 300 ms for common queries.
- **Scalability:** Horizontal scaling of ingestion and processing tiers.
- **Security:** TLS for all network paths; encryption at rest.
- **Auditability:** End-to-end lineage with immutable ingestion logs.

## 9. Security Architecture
- Authentication via centralized identity provider.
- Authorization via RBAC and scoped service principals.
- Secret management through managed vault integration.
- Data classification policies for sensitive fields.
- Tokenized or masked payloads for PII in non-prod environments.

## 10. Deployment Architecture
- Containerized microservices and jobs orchestrated in Kubernetes.
- Separate environments: dev, test, staging, prod.
- Blue/green or canary deployment for serving APIs.
- Infrastructure-as-code for reproducible environments.

## 11. Failure Handling and Resilience
- Retries with exponential backoff for transient connector failures.
- Circuit breakers for unstable dependencies.
- DLQ for unrecoverable records with replay tooling.
- Multi-AZ deployment for critical serving and metadata components.

## 12. Technology Decision Guidance (Vendor-Agnostic)
- Message bus for stream transport.
- Object storage for raw immutable zone.
- Distributed compute engine for transformation workloads.
- Analytical/operational database for curated and serving layers.
- API gateway and service mesh for edge and internal traffic controls.

## 13. Risks and Mitigations
- **Schema drift from producers:** enforce contract testing and registry checks.
- **Backpressure in ingestion:** autoscaling and queue depth monitoring.
- **Data quality degradation:** mandatory quality gates and quarantine workflows.
- **Operational complexity:** standard runbooks, SLOs, and playbooks.

## 14. Open Decisions
- Canonical event envelope versioning strategy.
- Historical data retention durations per entity class.
- Query federation versus pre-materialized views for analytics consumers.

## 15. Traceability
Detailed component-level behavior, APIs, and sequence flows are defined in:
- `docs/detailed-design.md`
