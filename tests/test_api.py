from uuid import uuid4

from fastapi.testclient import TestClient

from iods.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get('/v1/health')

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_ingest_and_query_transaction() -> None:
    token = uuid4().hex
    tx_id = f'tx-{token}'
    account_id = f'acc-{token}'
    envelope = {
        'event_id': f'evt-{token}',
        'source_system': 'core_banking',
        'entity_type': 'transaction',
        'schema_version': '1.0',
        'event_time': '2026-01-10T12:30:00Z',
        'idempotency_key': f'idem-{token}',
        'payload': {
            'transaction_id': tx_id,
            'source_transaction_id': f'src-{tx_id}',
            'account_id': account_id,
            'amount': '125.50',
            'currency': 'usd',
            'status': 'settled',
        },
    }

    with TestClient(app) as client:
        ingest_resp = client.post('/v1/ingest', json=envelope)
        assert ingest_resp.status_code == 200
        assert ingest_resp.json()['status'] == 'processed'

        tx_resp = client.get(f'/v1/transactions/{tx_id}')
        assert tx_resp.status_code == 200
        body = tx_resp.json()
        assert body['transaction_id'] == tx_id
        assert body['currency'] == 'USD'

        account_resp = client.get(f'/v1/accounts/{account_id}/transactions')
        assert account_resp.status_code == 200
        assert len(account_resp.json()) >= 1


def test_invalid_payload_goes_to_dlq() -> None:
    token = uuid4().hex
    envelope = {
        'event_id': f'evt-{token}',
        'source_system': 'core_banking',
        'entity_type': 'transaction',
        'schema_version': '1.0',
        'event_time': '2026-01-10T12:30:00Z',
        'idempotency_key': f'idem-{token}',
        'payload': {
            'transaction_id': f'tx-{token}',
            'account_id': f'acc-{token}',
            'amount': '-1.00',
            'currency': 'USD',
            'status': 'SETTLED',
        },
    }

    with TestClient(app) as client:
        resp = client.post('/v1/ingest', json=envelope)

    assert resp.status_code == 200
    assert resp.json()['status'] == 'dlq'
    assert resp.json()['reason_code'] == 'negative_amount'
