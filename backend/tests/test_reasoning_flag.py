import os
import sys
import pytest

# Ensure backend package and its modules are discoverable
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app import app  # noqa: E402

@pytest.fixture()
def client():
    app.config['TESTING'] = True
    return app.test_client()


def sample_payload():
    return {
        'question': 'Will I pass?',
        'location': 'London, UK',
        'useCurrentTime': True,
    }


def test_legacy_reasoning(client):
    resp = client.post('/api/calculate-chart', json=sample_payload())
    data = resp.get_json()
    assert 'rationale' in data and 'reasoning_v1' not in data


def test_reasoning_v1_via_query(client):
    resp = client.post('/api/calculate-chart?useReasoningV1=true', json=sample_payload())
    data = resp.get_json()
    assert 'reasoning_v1' in data and 'rationale' not in data


def test_reasoning_v1_via_header(client):
    resp = client.post('/api/calculate-chart', json=sample_payload(), headers={'X-Use-Reasoning-V1': 'true'})
    data = resp.get_json()
    assert 'reasoning_v1' in data and 'rationale' not in data
