import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Alert,
  Typography,
} from '@mui/material'
import { apiClient } from '../api/client'

const LLM_REQUEST_TIMEOUT_SECONDS = 900
const LLM_REQUEST_MAX_ATTEMPTS = 2

const PROVIDERS = [
  { id: 'fixture', label: 'Local/Fixture (Offline)' },
  { id: 'xai', label: 'xAI Grok' },
  { id: 'openai', label: 'OpenAI' },
  { id: 'anthropic', label: 'Anthropic Claude' },
  { id: 'azure', label: 'Azure OpenAI' },
  { id: 'ollama', label: 'Ollama (Local)' },
  { id: 'custom', label: 'Custom/Intranet' },
]

const STAGES = [
  { id: 'agent_01', label: 'Input Normalizer' },
  { id: 'agent_02', label: 'Context Builder' },
  { id: 'agent_03', label: 'Trust Boundary Validator' },
  { id: 'agent_04', label: 'STRIDE Scorer' },
  { id: 'agent_05', label: 'Threat Generator' },
  { id: 'agent_06', label: 'STIX Packager' },
  { id: 'agent_07', label: 'Mitigation Generator' },
  { id: 'agent_08', label: 'Diagram Generator' },
  { id: 'agent_09', label: 'Report Writer' },
]

interface PipelineConfigProps {
  open: boolean
  onConfirm: (config: PipelineConfigData) => void
  onBack: () => void
  onCancel: () => void
}

export interface PipelineConfigData {
  provider: string
  modelName: string
  apiKey: string
  connectionUrl: string
  enabledStages: string[]
  requireHitlGates: boolean
}

const PROVIDER_MODELS: Record<string, string[]> = {
  fixture: ['fixture-placeholder'],
  openai: ['gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-4o-mini', 'o4-mini', 'o3'],
  anthropic: ['claude-sonnet-4-20250514', 'claude-opus-4-20250514', 'claude-3-5-haiku-20241022'],
  xai: [
    'grok-4',
    'grok-4.3',
    'grok-4.20-multi-agent-0309',
    'grok-4.20-0309-reasoning',
    'grok-4.20-0309-non-reasoning',
    'grok-4-1-fast-reasoning',
    'grok-4-1-fast-non-reasoning',
  ],
  azure: ['gpt-4.1', 'gpt-4o', 'o4-mini'],
  ollama: ['llama3.1:8b', 'llama3.1:70b', 'qwen2.5:14b', 'mistral:latest'],
  custom: ['<Custom model>'],
}

const PROVIDER_CONNECTION_URLS: Record<string, string> = {
  fixture: '',
  openai: 'https://api.openai.com/v1',
  anthropic: 'https://api.anthropic.com/v1',
  xai: 'https://api.x.ai/v1',
  azure: 'https://{resource-name}.openai.azure.com/openai/deployments/{deployment}',
  ollama: 'http://127.0.0.1:11434/v1',
  custom: '',
}

export function PipelineConfig({ open, onConfirm, onBack, onCancel }: PipelineConfigProps) {
  const [provider, setProvider] = React.useState('fixture')
  const [modelName, setModelName] = React.useState('fixture-placeholder')
  const [apiKey, setApiKey] = React.useState('')
  const [connectionUrl, setConnectionUrl] = React.useState('')
  const [enabledStages, setEnabledStages] = React.useState<string[]>(STAGES.map((stage) => stage.id))
  const [requireHitlGates, setRequireHitlGates] = React.useState(true)
  const [verified, setVerified] = React.useState(provider === 'fixture')
  const [verifyMessage, setVerifyMessage] = React.useState<string | null>(null)
  const [verifyError, setVerifyError] = React.useState<string | null>(null)
  const [verifying, setVerifying] = React.useState(false)

  const requiresApiKey = provider !== 'fixture' && provider !== 'ollama'
  const providerModels = PROVIDER_MODELS[provider] ?? []
  const isCustomProvider = provider === 'custom'

  React.useEffect(() => {
    setVerified(provider === 'fixture')
    setVerifyMessage(provider === 'fixture' ? 'Fixture mode selected, verification is not required.' : null)
    setVerifyError(null)
  }, [provider, modelName, apiKey, connectionUrl])

  React.useEffect(() => {
    const nextModels = PROVIDER_MODELS[provider] ?? []
    const defaultModel = nextModels[0] ?? ''

    if (!isCustomProvider) {
      setModelName(defaultModel)
    } else if (modelName === '<Custom model>') {
      setModelName('')
    }

    setConnectionUrl(PROVIDER_CONNECTION_URLS[provider] ?? '')
  }, [provider, isCustomProvider, modelName])

  const handleStageToggle = (stage: string) => {
    setEnabledStages((prev) =>
      prev.includes(stage) ? prev.filter((s) => s !== stage) : [...prev, stage]
    )
  }

  const handleConfirm = () => {
    const errors: string[] = []
    if (!modelName.trim()) errors.push('Model name is required')
    if (requiresApiKey && !apiKey.trim()) errors.push('API key is required for this provider')
    if (!connectionUrl.trim() && provider !== 'fixture') errors.push('Connection URL is required for this provider')
    if (enabledStages.length === 0) errors.push('At least one stage must be enabled')
    if (provider !== 'fixture' && !verified) {
      errors.push('Verify LLM connection before applying settings')
    }

    if (errors.length > 0) {
      alert(errors.join('\n'))
      return
    }

    onConfirm({
      provider,
      modelName,
      apiKey,
      connectionUrl,
      enabledStages,
      requireHitlGates,
    })
  }

  const handleVerifyConnection = async () => {
    setVerifyError(null)
    setVerifyMessage(null)
    setVerifying(true)
    try {
      const runtimeSettings = {
        model: {
          provider,
          model_name: modelName,
          api_key: apiKey,
          offline_only: provider === 'fixture',
          connection_url: connectionUrl,
          endpoint_mode: 'chat_completions',
          request_timeout_seconds: LLM_REQUEST_TIMEOUT_SECONDS,
          request_max_attempts: LLM_REQUEST_MAX_ATTEMPTS,
        },
        pipeline: {
          execution_mode: 'langgraph-compatible',
          enabled_stage_ids: enabledStages,
          stop_on_validation_error: false,
          require_hitl_gates: requireHitlGates,
        },
      }
      const response = await apiClient.verifyConfigConnection(runtimeSettings, apiKey)
      setVerified(response.ok)
      setVerifyMessage(response.message)
      if (!response.ok) {
        setVerifyError(response.message)
      }
    } catch (err) {
      setVerified(false)
      setVerifyError(err instanceof Error ? err.message : 'Connection verification failed')
    } finally {
      setVerifying(false)
    }
  }

  return (
    <Dialog open={open} maxWidth="sm" fullWidth>
      <DialogTitle>Pipeline Configuration</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControl fullWidth>
            <InputLabel>LLM Provider</InputLabel>
            <Select value={provider} label="LLM Provider" onChange={(e) => setProvider(e.target.value)}>
              {PROVIDERS.map((p) => (
                <MenuItem key={p.id} value={p.id}>
                  {p.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {isCustomProvider ? (
            <TextField
              label="Model Name"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              fullWidth
              placeholder="custom-model"
            />
          ) : (
            <FormControl fullWidth>
              <InputLabel>Model Name</InputLabel>
              <Select value={modelName} label="Model Name" onChange={(e) => setModelName(e.target.value)}>
                {providerModels.map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          <TextField
            label="Connection URL"
            value={connectionUrl}
            onChange={(e) => setConnectionUrl(e.target.value)}
            fullWidth
            disabled={!isCustomProvider}
            placeholder="https://api.example.com/v1"
            helperText={isCustomProvider ? 'Editable for Custom/Intranet provider only' : 'Managed by selected provider'}
          />

          {requiresApiKey && (
            <TextField
              label="API Key"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              fullWidth
              helperText="Stored in session only, not persisted"
            />
          )}

          <Box>
            <Typography sx={{ display: 'block', mb: 1, fontWeight: 600 }}>Enabled Stages</Typography>
            <FormGroup>
              {STAGES.map((stage) => (
                <FormControlLabel
                  key={stage.id}
                  control={
                    <Checkbox
                      checked={enabledStages.includes(stage.id)}
                      onChange={() => handleStageToggle(stage.id)}
                    />
                  }
                  label={`${stage.id} - ${stage.label}`}
                />
              ))}
            </FormGroup>
          </Box>

          <FormControlLabel
            control={<Checkbox checked={requireHitlGates} onChange={(e) => setRequireHitlGates(e.target.checked)} />}
            label="Require HITL Gates (pause at decision points)"
          />

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Button variant="outlined" onClick={handleVerifyConnection} disabled={verifying}>
              {verifying ? 'Verifying...' : 'Verify LLM Connection'}
            </Button>
            {verified && <Alert severity="success" sx={{ py: 0 }}>Verified</Alert>}
          </Box>

          {verifyMessage && !verifyError && <Alert severity="info">{verifyMessage}</Alert>}
          {verifyError && <Alert severity="error">{verifyError}</Alert>}

          {provider === 'fixture' && (
            <Alert severity="info">
              Fixture mode uses deterministic pre-recorded outputs. Perfect for testing and demos.
            </Alert>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button onClick={onBack}>Back</Button>
        <Button onClick={handleConfirm} variant="contained">
          Apply Settings
        </Button>
      </DialogActions>
    </Dialog>
  )
}
