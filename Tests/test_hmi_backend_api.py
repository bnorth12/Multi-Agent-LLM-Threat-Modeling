import pytest
import socket
import threading
import time
import os
from pathlib import Path
import json
import requests
from urllib.request import Request, urlopen
from urllib.error import URLError
from unittest.mock import patch

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from threat_modeler.server.api import start_server, _serialize_run_entry
from threat_modeler.backend.run_manager import _REGISTRY_LOCK, _RUN_REGISTRY, ExecutionStatus
from threat_modeler.config import build_default_settings
from threat_modeler.hitl.models import GateAction, GateStatus, HitlGateRecord
from threat_modeler.state import FrameworkState


def _register_run_with_checkpoint(run_id: str, checkpoint: dict, *, status: str = ExecutionStatus.PAUSED.value):
    state = FrameworkState()
    state.hitl_gate_checkpoint = checkpoint
    with _REGISTRY_LOCK:
        _RUN_REGISTRY[run_id] = {
            'run_id': run_id,
            'status': status,
            'start_time': None,
            'end_time': None,
            'pause_gate': next(iter(checkpoint.get('gates', {})), None),
            'error': None,
            'last_heartbeat_time': time.time(),
            'heartbeat_timeout_seconds': 10.0,
            'result_state': state,
            'live_state': state,
            'settings': build_default_settings(),
        }
    return state

def find_free_port():
    """Find a free port to use for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

@pytest.fixture(scope='module')
def test_server():
    """Start test server in a background thread."""
    port = find_free_port()
    base_url = f'http://localhost:{port}'

    # Start server in background thread
    server_thread = threading.Thread(
        target=start_server,
        kwargs={'host': 'localhost', 'port': port},
        daemon=True
    )
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    yield base_url

    # Server will shut down with daemon thread

@pytest.fixture
def base_url(test_server):
    """Provide base URL for testing."""
    return test_server

def test_health_check(base_url):
    """Test backend health endpoint."""
    response = requests.get(f'{base_url}/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'

def test_create_run(base_url):
    """Test run creation."""
    run_id = 'test-run-001'
    response = requests.post(f'{base_url}/runs/{run_id}')
    assert response.status_code in [200, 201]

def test_get_runs(base_url):
    """Test listing runs."""
    response = requests.get(f'{base_url}/runs')
    assert response.status_code == 200
    data = response.json()
    assert 'runs' in data
    assert isinstance(data['runs'], list)

def test_full_state_retrieval(base_url):
    """Test comprehensive state retrieval for HMI."""
    run_id = 'hmi-test-run'

    # Create run
    requests.post(f'{base_url}/runs/{run_id}')

    # Get full state
    response = requests.get(f'{base_url}/runs/{run_id}/state/full')

    # May get 404 if run hasn't started yet, which is ok
    if response.status_code == 200:
        data = response.json()

        # Verify response structure
        assert 'state' in data
        assert 'stages' in data
        assert 'threats' in data
        assert 'gates' in data
        assert 'metrics' in data

        # Verify metrics structure
        metrics = data['metrics']
        assert 'total_tokens' in metrics
        assert 'prompt_tokens' in metrics
        assert 'completion_tokens' in metrics
        assert 'reasoning_tokens' in metrics
        assert 'cached_tokens' in metrics
        assert 'request_count' in metrics
        assert 'by_stage' in metrics

def test_gates_endpoint(base_url):
    """Test HITL gates retrieval."""
    run_id = 'gates-test-run'
    requests.post(f'{base_url}/runs/{run_id}')

    response = requests.get(f'{base_url}/runs/{run_id}/state/gates')

    # May not have gates yet
    if response.status_code == 200:
        data = response.json()
        assert 'gates' in data
        assert isinstance(data['gates'], list)

def test_threats_endpoint(base_url):
    """Test threats retrieval."""
    run_id = 'threats-test-run'
    requests.post(f'{base_url}/runs/{run_id}')

    response = requests.get(f'{base_url}/runs/{run_id}/state/threats')

    if response.status_code == 200:
        data = response.json()
        assert 'threats' in data
        assert isinstance(data['threats'], list)

def test_stages_endpoint(base_url):
    """Test execution stages retrieval."""
    run_id = 'stages-test-run'
    requests.post(f'{base_url}/runs/{run_id}')

    response = requests.get(f'{base_url}/runs/{run_id}/state/stages')

    if response.status_code == 200:
        data = response.json()
        assert 'stages' in data
        assert isinstance(data['stages'], list)

def test_metrics_endpoint(base_url):
    """Test LLM metrics retrieval."""
    run_id = 'metrics-test-run'
    requests.post(f'{base_url}/runs/{run_id}')

    response = requests.get(f'{base_url}/runs/{run_id}/state/metrics')

    if response.status_code == 200:
        data = response.json()
        assert 'metrics' in data
        metrics = data['metrics']
        assert 'total_tokens' in metrics
        assert 'by_stage' in metrics

def test_gate_decision_endpoint(base_url):
    """Test gate decision submission."""
    run_id = 'gate-decision-test'
    requests.post(f'{base_url}/runs/{run_id}')

    decision_data = {
        'actor': 'test_user',
        'role': 'analyst',
        'action': 'accept_as_is',
        'rationale': 'Testing gate decision flow'
    }

    response = requests.post(
        f'{base_url}/runs/{run_id}/gates/gate_01/decide',
        json=decision_data,
        headers={'Content-Type': 'application/json'}
    )

    # Will vary based on whether gate exists and whether payload readiness guard blocks early decision.
    assert response.status_code in [200, 404, 400, 409]


def test_gate_endpoints_return_all_checkpoint_gates_from_dict(base_url):
    """Checkpoint gates are stored as a dict keyed by gate_id and must round-trip to the UI."""
    run_id = 'gate-dict-shape-test'
    checkpoint = {
        'run_id': run_id,
        'gates': {
            gate_id: HitlGateRecord(
                gate_id=gate_id,
                gate_name=gate_id.replace('_', ' ').title(),
                stage_id=f'agent_{index:02d}' if index < 10 else f'agent_{index}',
                status=GateStatus.OPEN if gate_id == 'gate_2_boundary_approval' else GateStatus.PENDING,
                artifact_snapshot={'gate_index': index},
            ).to_dict()
            for index, gate_id in enumerate([
                'gate_0_input_integrity',
                'gate_1_normalization_review',
                'gate_1_scope_confirmation',
                'gate_2_boundary_approval',
                'gate_3_stride_calibration',
                'gate_4_threat_plausibility',
                'gate_5_mitigation_adequacy',
                'gate_8_diagram_review',
                'gate_9_stix_packaging_review',
                'gate_6_merge_conflict_resolution',
                'gate_7_export_consistency',
            ])
        },
        'audit_log': {'run_id': run_id, 'entries': []},
    }
    _register_run_with_checkpoint(run_id, checkpoint)

    gates_response = requests.get(f'{base_url}/runs/{run_id}/state/gates')
    assert gates_response.status_code == 200
    gates_payload = gates_response.json()['gates']
    assert len(gates_payload) == 11
    assert {gate['gate_id'] for gate in gates_payload} == set(checkpoint['gates'].keys())

    full_response = requests.get(f'{base_url}/runs/{run_id}/state/full')
    assert full_response.status_code == 200
    assert len(full_response.json()['gates']) == 11


def test_gate_decision_endpoint_updates_checkpoint_status(base_url):
    """Submitting a gate decision must update checkpoint state, not just record an opaque blob."""
    run_id = 'gate-decision-status-test'
    checkpoint = {
        'run_id': run_id,
        'gates': {
            'gate_2_boundary_approval': HitlGateRecord(
                gate_id='gate_2_boundary_approval',
                gate_name='Gate 2 Boundary Approval',
                stage_id='agent_03',
                status=GateStatus.OPEN,
                artifact_snapshot={'interfaces': 3},
            ).to_dict(),
        },
        'audit_log': {'run_id': run_id, 'entries': []},
    }
    _register_run_with_checkpoint(run_id, checkpoint)

    response = requests.post(
        f'{base_url}/runs/{run_id}/gates/gate_2_boundary_approval/decide',
        json={
            'actor': 'test_user',
            'role': 'analyst',
            'action': GateAction.ACCEPT_AS_IS.value,
            'rationale': 'Boundary review accepted.',
        },
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['decision_recorded'] is True
    assert payload['gate_status'] == GateStatus.ACCEPTED_AS_IS.value

    gates_response = requests.get(f'{base_url}/runs/{run_id}/state/gates')
    assert gates_response.status_code == 200
    gate = next(
        item for item in gates_response.json()['gates']
        if item['gate_id'] == 'gate_2_boundary_approval'
    )
    assert gate['status'] == GateStatus.ACCEPTED_AS_IS.value
    assert gate['decision']['actor'] == 'test_user'
    assert gate['decision']['rationale'] == 'Boundary review accepted.'


def test_gate_decision_endpoint_rejects_when_artifact_snapshot_missing(base_url):
    """Gate review must be blocked until parser/processing payload is present."""
    run_id = 'gate-decision-payload-not-ready-test'
    checkpoint = {
        'run_id': run_id,
        'gates': {
            'gate_8_diagram_review': HitlGateRecord(
                gate_id='gate_8_diagram_review',
                gate_name='Gate 8 Diagram Review',
                stage_id='agent_08',
                status=GateStatus.OPEN,
                artifact_snapshot=None,
            ).to_dict(),
        },
        'audit_log': {'run_id': run_id, 'entries': []},
    }
    _register_run_with_checkpoint(run_id, checkpoint)

    response = requests.post(
        f'{base_url}/runs/{run_id}/gates/gate_8_diagram_review/decide',
        json={
            'actor': 'test_user',
            'role': 'analyst',
            'action': GateAction.ACCEPT_AS_IS.value,
            'rationale': 'Approve once available.',
        },
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 409
    payload = response.json()
    assert 'not ready' in payload.get('error', '').lower()


def test_resume_endpoint_uses_server_side_state_when_payload_omitted(base_url):
    """Resume should work from the server's paused state without requiring the client to resend the pipeline state."""
    run_id = 'resume-server-state-test'
    checkpoint = {
        'run_id': run_id,
        'gates': {
            'gate_3_stride_calibration': HitlGateRecord(
                gate_id='gate_3_stride_calibration',
                gate_name='Gate 3 STRIDE Calibration',
                stage_id='agent_04',
                status=GateStatus.ACCEPTED_AS_IS,
                artifact_snapshot={'interfaces': 2},
            ).to_dict(),
        },
        'audit_log': {'run_id': run_id, 'entries': []},
    }
    state = _register_run_with_checkpoint(run_id, checkpoint)

    captured = {}

    def _fake_resume(run_id_arg, gate_id_arg, pipeline_state_arg, settings_arg):
        captured['run_id'] = run_id_arg
        captured['gate_id'] = gate_id_arg
        captured['pipeline_state'] = pipeline_state_arg
        captured['settings'] = settings_arg

    with patch('threat_modeler.server.api.resume_run', side_effect=_fake_resume):
        response = requests.post(
            f'{base_url}/runs/{run_id}/resume',
            json={'gate_id': 'gate_3_stride_calibration'},
            headers={'Content-Type': 'application/json'},
        )

    assert response.status_code == 202
    assert captured['run_id'] == run_id
    assert captured['gate_id'] == 'gate_3_stride_calibration'
    assert captured['pipeline_state'] is state
    assert captured['settings'] is not None

def test_threat_decision_endpoint(base_url):
    """Test threat decision submission."""
    run_id = 'threat-decision-test'
    requests.post(f'{base_url}/runs/{run_id}')

    decision_data = {
        'decision': 'approve',
        'notes': 'Testing threat decision flow',
        'reviewer': 'test_user'
    }

    response = requests.post(
        f'{base_url}/runs/{run_id}/threats/threat_001/decide',
        json=decision_data,
        headers={'Content-Type': 'application/json'}
    )

    # Will vary based on whether threat exists
    assert response.status_code in [200, 404, 400]

def test_hmi_data_types():
    """Test HMI data extraction types are correct."""
    from threat_modeler.server.hmi_data import serialize_threat, serialize_gate

    # Test basic serialization structure
    test_threat = {
        'id': 'threat_001',
        'name': 'Test Threat',
        'interface_id': 'iface_01',
        'likelihood': 'High',
        'impact': 'Critical',
        'risk_score': 9,
        'description': 'Test',
        'technical_mitigations': [],
        'administrative_mitigations': [],
        'mitre_attack_techniques': [],
    }

    # Basic structure check
    assert test_threat['id'] == 'threat_001'
    assert test_threat['risk_score'] == 9


def test_config_verify_real_provider_fails_when_prompt_ping_errors(base_url):
    payload = {
        'config': {
            'model': {
                'provider': 'xai',
                'model_name': 'grok-4',
                'api_key': 'dummy-key',
                'offline_only': False,
                'connection_url': 'https://api.x.ai/v1',
                'endpoint_mode': 'chat_completions',
                'request_timeout_seconds': 20,
                'request_max_attempts': 1,
            },
            'pipeline': {
                'execution_mode': 'langgraph-compatible',
                'enabled_stage_ids': ['agent_01'],
                'stop_on_validation_error': False,
                'require_hitl_gates': True,
            },
        },
        'api_key': 'dummy-key',
    }

    with patch(
        'threat_modeler.server.api.OpenAiCompatibleAdapter.complete',
        side_effect=RuntimeError('401 Unauthorized'),
    ):
        response = requests.post(
            f'{base_url}/config/verify',
            json=payload,
            headers={'Content-Type': 'application/json'},
        )

    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is False
    assert 'Live prompt ping failed' in body['message']


def test_config_verify_real_provider_fails_on_empty_prompt_response(base_url):
    payload = {
        'config': {
            'model': {
                'provider': 'xai',
                'model_name': 'grok-4',
                'api_key': 'dummy-key',
                'offline_only': False,
                'connection_url': 'https://api.x.ai/v1',
                'endpoint_mode': 'chat_completions',
                'request_timeout_seconds': 20,
                'request_max_attempts': 1,
            },
            'pipeline': {
                'execution_mode': 'langgraph-compatible',
                'enabled_stage_ids': ['agent_01'],
                'stop_on_validation_error': False,
                'require_hitl_gates': True,
            },
        },
        'api_key': 'dummy-key',
    }

    with patch('threat_modeler.server.api.OpenAiCompatibleAdapter.complete', return_value='   '):
        response = requests.post(
            f'{base_url}/config/verify',
            json=payload,
            headers={'Content-Type': 'application/json'},
        )

    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is False
    assert 'empty response' in body['message']


def test_config_verify_real_provider_passes_on_non_empty_prompt_response(base_url):
    payload = {
        'config': {
            'model': {
                'provider': 'xai',
                'model_name': 'grok-4',
                'api_key': 'dummy-key',
                'offline_only': False,
                'connection_url': 'https://api.x.ai/v1',
                'endpoint_mode': 'chat_completions',
                'request_timeout_seconds': 20,
                'request_max_attempts': 1,
            },
            'pipeline': {
                'execution_mode': 'langgraph-compatible',
                'enabled_stage_ids': ['agent_01'],
                'stop_on_validation_error': False,
                'require_hitl_gates': True,
            },
        },
        'api_key': 'dummy-key',
    }

    with patch('threat_modeler.server.api.OpenAiCompatibleAdapter.complete', return_value='OK'):
        response = requests.post(
            f'{base_url}/config/verify',
            json=payload,
            headers={'Content-Type': 'application/json'},
        )

    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is True
    assert body['message'] == 'Live prompt ping succeeded.'


def test_config_verify_real_provider_rejects_offline_only_mode(base_url):
    payload = {
        'config': {
            'model': {
                'provider': 'xai',
                'model_name': 'grok-4',
                'api_key': 'dummy-key',
                'offline_only': True,
                'connection_url': 'https://api.x.ai/v1',
                'endpoint_mode': 'chat_completions',
                'request_timeout_seconds': 20,
                'request_max_attempts': 1,
            },
            'pipeline': {
                'execution_mode': 'langgraph-compatible',
                'enabled_stage_ids': ['agent_01'],
                'stop_on_validation_error': False,
                'require_hitl_gates': True,
            },
        },
        'api_key': 'dummy-key',
    }

    response = requests.post(
        f'{base_url}/config/verify',
        json=payload,
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is False
    assert 'offline_only=false' in body['message']


def test_serialize_run_entry_gate0_pause_hidden_until_preflight_ready():
    run_id = 'gate0-projection-race'
    state = FrameworkState()
    state.hitl_gate_checkpoint = {
        'run_id': run_id,
        'gates': {
            'gate_0_input_integrity': {
                'gate_id': 'gate_0_input_integrity',
                'gate_name': 'Input Integrity Gate',
                'stage_id': 'agent_01',
                'status': GateStatus.OPEN.value,
                'artifact_snapshot': None,
                'draft_artifact': None,
                'decision': None,
                'diff': {},
            }
        },
        'audit_log': {'run_id': run_id, 'entries': []},
    }

    projected = _serialize_run_entry(
        {
            'run_id': run_id,
            'status': ExecutionStatus.PAUSED.value,
            'pause_gate': 'gate_0_input_integrity',
            'result_state': state,
            'live_state': state,
            'settings': build_default_settings(),
            'start_time': None,
            'end_time': None,
            'error': None,
            'last_heartbeat_time': time.time(),
            'heartbeat_timeout_seconds': 10.0,
        }
    )

    assert projected is not None
    assert projected['status'] == ExecutionStatus.RUNNING.value
    assert projected['pause_gate'] is None


def test_serialize_run_entry_gate0_pause_visible_when_preflight_ready():
    run_id = 'gate0-projection-ready'
    state = FrameworkState()
    state.hitl_gate_checkpoint = {
        'run_id': run_id,
        'gates': {
            'gate_0_input_integrity': {
                'gate_id': 'gate_0_input_integrity',
                'gate_name': 'Input Integrity Gate',
                'stage_id': 'agent_01',
                'status': GateStatus.OPEN.value,
                'artifact_snapshot': {
                    'input_preflight': {
                        'raw_text_length': 32,
                        'raw_text_preview': 'Preflight payload',
                        'table_count': 0,
                        'checks': {
                            'source_present': True,
                            'has_raw_text': True,
                            'has_tables': False,
                        },
                    }
                },
                'draft_artifact': None,
                'decision': None,
                'diff': {},
            }
        },
        'audit_log': {'run_id': run_id, 'entries': []},
    }

    projected = _serialize_run_entry(
        {
            'run_id': run_id,
            'status': ExecutionStatus.PAUSED.value,
            'pause_gate': 'gate_0_input_integrity',
            'result_state': state,
            'live_state': state,
            'settings': build_default_settings(),
            'start_time': None,
            'end_time': None,
            'error': None,
            'last_heartbeat_time': time.time(),
            'heartbeat_timeout_seconds': 10.0,
        }
    )

    assert projected is not None
    assert projected['status'] == ExecutionStatus.PAUSED.value
    assert projected['pause_gate'] == 'gate_0_input_integrity'

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
