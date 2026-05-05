# Model Configuration GUI and Backend Design Specification

Date: 2026-05-03
Version: 0.1 (Draft)
Status: Design for Next Sprint Implementation

## Overview

This document specifies the design of the model provider configuration system that enables analysts to select and configure model providers (local, cloud-hosted, commercial LLMs) through a GUI without requiring code changes.

Scope:
- GUI screens for provider selection and connection configuration
- Backend services for model connection management and validation
- Secure credential storage strategy
- Integration with existing LLM orchestration layer
- Testing and validation approach

## Related Requirements

- PRJ-008: Configurable Model Selection
- PRJ-009: Deployment Mode Flexibility
- PRJ-012: Role-Enforced Access Control
- INT-012: Provider Config Contract
- INT-015: Model Connection Contract (NEW)
- GUI-012: Model Provider Selection Screen (NEW)
- GUI-013: Model Connection Details Configuration (NEW)
- GUI-014: Model Connection Validation (NEW)

## Architecture

### Component 1: Model Provider Registry

**Purpose:** Maintain a list of available model providers and their configuration requirements.

**Responsibilities:**
- Define available providers:
   - Local or Fixture (offline test mode)
   - OpenAI
   - Anthropic
   - xAI or Grok
   - Azure OpenAI
   - Ollama
   - Custom or Intranet (OpenAI-compatible self-hosted endpoint)
- For each provider: required fields, optional fields, default values, authentication method
- Provide provider metadata to GUI for form generation

**Design Decisions:**
- Store provider definitions in a JSON config file: `src/threat_modeler/config/model_providers.json`
- Each provider entry includes:
  ```json
  {
    "provider_name": "openai",
    "display_name": "OpenAI GPT-4",
    "auth_method": "api_key",
    "required_fields": ["api_key", "model_name"],
    "optional_fields": ["org_id", "base_url"],
    "default_model": "gpt-4",
    "validation_endpoint": "/v1/models",
    "connection_timeout_seconds": 10
  }
  ```
- Registry is loaded at application startup and cached

### Component 2: Connection Configuration Service

**Purpose:** Manage, validate, and persist model connection configurations.

**Responsibilities:**
- Accept provider name and connection parameters from GUI
- Validate configuration format and required fields
- Test connectivity to configured model endpoint
- Securely store credentials
- Retrieve active configuration for pipeline execution
- Support multiple stored configurations (switch between providers/instances)

**Design Decisions:**
- Configuration persisted to `~/.threat_modeler/config/model_connections.json` (user home directory)
- Credentials encrypted using system keyring (Windows: Credential Manager, Linux: pass/secretservice, macOS: Keychain)
- API keys never logged or written to plaintext files
- Fallback to local ollama if no provider configured (default behavior)
- Configuration schema includes: provider_name, endpoint, auth_method, active_config_name, timestamp_configured

**Python Class Structure:**

```python
@dataclass
class ModelConnectionConfig:
    config_name: str  # e.g., "my-azure-gpt4", "local-ollama"
    provider_name: str  # e.g., "azure_openai", "openai"
    endpoint: str
    model_name: str
    auth_method: str  # "api_key", "oauth", "managed_identity"
    auth_credential_store: str  # "keyring", "env_var", "file"
    region_or_deployment: str = ""
    connection_validated_at: datetime = None
    validation_status: str = ""  # "valid", "invalid_auth", "invalid_endpoint", "timeout"

class ModelConnectionManager:
    def add_connection(config: ModelConnectionConfig) -> bool
    def get_connection(config_name: str) -> ModelConnectionConfig
    def set_active_connection(config_name: str) -> bool
    def get_active_connection() -> ModelConnectionConfig
    def delete_connection(config_name: str) -> bool
    def list_connections() -> list[ModelConnectionConfig]
    def validate_connection(config: ModelConnectionConfig) -> ConnectionValidationResult
```

### Component 3: GUI - Model Provider Selection Screen (GUI-012)

**Purpose:** Allow analysts to view, select, and activate a configured model provider.

**Responsibilities:**
- Display list of saved model provider configurations
- Show provider name, endpoint, model name, and validation status
- Support "Add New Configuration" button
- Support "Set as Active" action
- Show active configuration in highlighted state
- Provide "Test Connection" button
- Support "Delete Configuration" action (with confirmation)

**Layout:**
```
╔════════════════════════════════════════════════════════════╗
║ MODEL PROVIDER CONFIGURATION                              ║
╠════════════════════════════════════════════════════════════╣
║                                                             ║
║  Active Configuration: [my-azure-gpt4 ▼]                 ║
║                                                             ║
║  Saved Configurations:                                     ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ Name            │ Provider    │ Endpoint  │ Status  │ ║
║  ├─────────────────────────────────────────────────────┤ ║
║  │ my-azure-gpt4   │ Azure OpenAI │ ✓ Valid  │ Active  │ ║
║  │ local-ollama    │ Ollama      │ ✓ Valid  │         │ ║
║  │ claude-api      │ Anthropic   │ ✗ Invalid│         │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                             ║
║  [+ Add New Configuration]                                ║
║                                                             ║
║  Selected: my-azure-gpt4                                  ║
║  [ Test Connection ] [ Set Active ] [ Delete ]            ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝
```

### Component 4: GUI - Connection Configuration Form (GUI-013)

**Purpose:** Collect and validate model connection details without exposing credentials in plaintext.

**Responsibilities:**
- Present provider-specific form fields (generated from registry metadata)
- Mask/hide API key inputs
- Support configuration save/update operations
- Validate inputs before submission
- Show configuration name for saving (allows multiple configs per provider)
- Option to "Always use this endpoint" vs. one-time use
- Clear indication of required vs. optional fields

**Form Generation Logic:**
- For Local or Fixture: no API key required; offline mode enabled
- For OpenAI: API Key (required, masked), Model Name (required, dropdown), Organization ID (optional)
- For Anthropic: API Key (required, masked), Model Name (required)
- For xAI or Grok: API Key (required, masked), Model Name (required), Base URL default `https://api.x.ai/v1`
- For Azure OpenAI: Endpoint URL (required), API Key (required, masked), Deployment Name (required), API Version (required), Model Name (optional display)
- For Ollama: Base URL (required, default: `http://localhost:11434`), Model Name (required), API Key optional
- For Custom or Intranet: Endpoint URL (required), API Key (usually required), Model Name (required), Auth Method (dropdown)

Most enterprise self-hosted providers use commercial-compatible APIs with internal base URLs;
the Custom or Intranet provider exists specifically for this case.

**Layout Example (Azure OpenAI):**
```
╔════════════════════════════════════════════════════════════╗
║ ADD MODEL PROVIDER CONFIGURATION                          ║
╠════════════════════════════════════════════════════════════╣
║                                                             ║
║  Configuration Name:  [my-azure-gpt4           ]           ║
║  (used to identify this saved configuration)               ║
║                                                             ║
║  Provider:            [Azure OpenAI ▼]                    ║
║                                                             ║
║  Endpoint URL:        [https://myorg.openai.azure.com  ]  ║
║  Required           * (e.g., https://myorg.openai.azure.com)║
║                                                             ║
║  API Key:            [●●●●●●●●●●●●●●●    (Show/Hide) ]  ║
║  Required           * (stored securely in Credential Mgr)  ║
║                                                             ║
║  Deployment Name:    [my-gpt4-deployment    ]             ║
║  Required           *                                      ║
║                                                             ║
║  Model Name:         [gpt-4 ▼]                            ║
║  Optional                                                  ║
║                                                             ║
║  [ Save Configuration ]  [ Cancel ]                        ║
║                                                             ║
║  ⓘ Credentials are encrypted and stored securely.         ║
║    They will not appear in logs or config files.           ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝
```

### Component 5: GUI - Connection Validation Test (GUI-014)

**Purpose:** Verify model endpoint connectivity and credentials before pipeline execution.

**Responsibilities:**
- Accept configuration and initiate test connection
- Show progress/spinner during test
- Return human-readable success or error message
- Log connection test results (not credentials)
- Block pipeline execution if validation returns failure
- Support pre-run and standalone validation

**Test Process:**
1. Construct authentication headers based on auth_method and credentials
2. Call lightweight model list endpoint (e.g., GET /v1/models for OpenAI)
3. Verify HTTP 200 response
4. Parse response to confirm model availability
5. Record timestamp and status
6. Return result to GUI

**Error Message Examples:**
- ✓ Connection successful. Model 'gpt-4' is available.
- ✗ Connection failed: 401 Unauthorized. Check API key and endpoint.
- ✗ Connection timeout after 10 seconds. Check endpoint URL and network connectivity.
- ✗ Model 'gpt-5' not found. Available models: gpt-4, gpt-3.5-turbo. Check deployment name.

**Pre-Run Validation:**
- If stop_on_validation_error=True and connection invalid, display error modal and prevent "Start Run" button
- If stop_on_validation_error=False (offline mode), warn but allow continuation

### Component 6: Credential Storage Strategy

**Rationale:** API keys and authentication credentials must never be stored in plaintext config files or logged.

**Design:**
- Use system credential manager where available:
  - Windows: `python-keyring` with DPAPI backend (native Windows encryption)
  - Linux: `python-keyring` with pass or secretservice backend
  - macOS: `python-keyring` with Keychain backend
- Fallback: Store in encrypted user config file with Fernet symmetric encryption (cryptography library)
- Config file stores only: provider_name, endpoint, model_name, credential_key_reference
- Credential key stored in system keyring or encrypted cache

**Python Implementation:**

```python
import keyring
from cryptography.fernet import Fernet

class CredentialManager:
    SERVICE_NAME = "threat-modeler"

    def store_credential(config_name: str, credential_key: str, credential_value: str):
        """Store credential in system keyring."""
        keyring.set_password(SERVICE_NAME, f"{config_name}:{credential_key}", credential_value)

    def retrieve_credential(config_name: str, credential_key: str) -> str:
        """Retrieve credential from system keyring."""
        return keyring.get_password(SERVICE_NAME, f"{config_name}:{credential_key}")

    def delete_credential(config_name: str, credential_key: str):
        """Delete credential from system keyring."""
        keyring.delete_password(SERVICE_NAME, f"{config_name}:{credential_key}")
```

## Integration Points

### 1. Runtime Settings Update

Extend `RuntimeSettings` dataclass to include:
- `active_model_config_name: str` (name of active configuration)
- `model_provider_override: ModelConnectionConfig` (optional, for programmatic override)

### 2. LLM Client Initialization

Update LLM client factory to:
1. Read active configuration from ModelConnectionManager
2. Build client with configured endpoint and credentials
3. Log configuration name but not credentials
4. Support fallback chain: explicit config → active config → environment variables → local ollama

### 3. Pipeline State

Update `FrameworkState` to include:
- `model_config_name: str` (records which config was used for this run)
- `model_connection_validation_status: str` (valid/invalid at run start)

### 4. HITL Gates

Extend HITL approval to allow model re-configuration before rerun:
- Gate question: "Re-use model provider or reconfigure?"
- If reconfigure: show provider selection screen before rerun
- Snapshot includes model configuration used

## Testing Strategy

### Unit Tests

1. **ModelConnectionManager Tests:**
   - Add/get/delete configurations
   - Set active configuration
   - Credential store/retrieve (mock keyring)
   - Validation of required fields
   - Duplicate configuration name handling

2. **Connection Validation Tests:**
   - Valid endpoint returns success
   - Invalid endpoint returns connectivity error
   - Invalid credentials return 401 error
   - Timeout handling (10-second default)
   - Model availability checks

3. **Configuration Parsing Tests:**
   - Provider registry loads correctly
   - Form field generation matches provider metadata
   - Required field validation before submission

### Integration Tests

1. **GUI Model Selection Flow:**
   - Add new configuration through GUI
   - Set as active configuration
   - Verify active config persists across app restart
   - Delete configuration and verify removal

2. **GUI Connection Test Flow:**
   - Enter valid connection details
   - Click "Test Connection" and verify success message
   - Modify endpoint to invalid URL
   - Click "Test Connection" and verify error message
   - Verify pipeline blocked if validation fails (when stop_on_validation_error=True)

3. **End-to-End Pipeline Flow:**
   - Configure model provider through GUI
   - Start pipeline run
   - Verify LLM client uses configured endpoint
   - Verify snapshot captures model config name
   - Import snapshot in new session
   - Verify model config is available (but credentials may need re-entry for security)

### Security Tests

1. Credentials never appear in logs (grep logs for API keys)
2. Credentials stored in encrypted keyring (verify keyring backend active)
3. Config file does not contain credentials (inspect JSON)
4. Credential references are unique per config (no cross-contamination)

## Future Enhancements (Post-Sprint)

1. **Model Provider Auto-Discovery:** Detect locally available Ollama models and cloud endpoints
2. **Connection Pooling:** Maintain connection pool for frequently used endpoints
3. **Multi-Provider Failover:** Define fallback provider chain if primary is unavailable
4. **Rate Limiting Configuration:** Per-provider rate limit settings (tokens/min, requests/min)
5. **Cost Tracking:** Log token usage per provider for cost analysis
6. **Provider-Specific Tuning:** Temperature, max_tokens, safety settings per provider
7. **Proxy Configuration:** HTTP/HTTPS proxy settings for restricted networks

## References

- PRJ-008: Configurable Model Selection (Requirements/01_Project_Requirements.md)
- INT-012 and INT-015: Provider configuration contracts (Requirements/02_Interface_Requirements.md)
- GUI-012, GUI-013, GUI-014: Model configuration GUI requirements (Requirements/10_GUI_Requirements.md)
- config.py: RuntimeSettings and ModelSelection dataclasses
- Python keyring documentation: https://keyring.readthedocs.io/
