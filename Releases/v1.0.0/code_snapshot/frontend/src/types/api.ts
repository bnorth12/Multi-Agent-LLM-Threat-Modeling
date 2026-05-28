export interface HealthResponse {
  status: 'ok' | string
}

export interface RuntimeSettings {
  model: {
    provider: string
    model_name: string
    api_key: string
    offline_only: boolean
    connection_url: string
    endpoint_mode: string
    request_timeout_seconds: number
    request_max_attempts: number
  }
  pipeline: {
    execution_mode: string
    enabled_stage_ids: string[]
    stop_on_validation_error: boolean
    require_hitl_gates: boolean
  }
}

export interface ConfigResponse {
  config: RuntimeSettings
}

export interface PromptSummary {
  prompt: string
  expected_output: string
  temperature: number
  is_modified: boolean
}

export interface PromptsResponse {
  prompts: Record<string, PromptSummary>
  prompt_store_path?: string
}

export interface PromptDetailResponse {
  agent_id: string
  prompt: string
  default_prompt: string
  expected_output: string
  temperature: number
  is_modified: boolean
  prompt_store_path?: string
  history: Array<{
    version: number
    text: string
    actor: string
    timestamp: string
  }>
}

export interface RunEntry {
  run_id: string
  run_name: string
  archived: boolean
  status: string
  pause_gate: string | null
  error: string | null
  last_heartbeat_time?: number | null
  heartbeat_timeout_seconds?: number | null
  heartbeat_age_seconds?: number | null
  start_time: string | null
  end_time: string | null
  settings: RuntimeSettings | null
  result_state: {
    next_stage_id: string | null
    hitl_paused_at_gate: string | null
    hitl_rejected_at_gate: string | null
  } | null
  live_state: {
    next_stage_id: string | null
    hitl_paused_at_gate: string | null
    hitl_rejected_at_gate: string | null
  } | null
}

export interface RunsResponse {
  runs: RunEntry[]
}

export interface RunResponse {
  run: RunEntry
}

export interface CreateRunResponse {
  run_id: string
  status_url: string
}

export interface ArtifactResponse {
  artifact: string
  content: unknown
}

export interface Stage {
  stage_id: string
  label: string
  status: string
}

export interface HitlDecision {
  gate_id: string
  actor: string
  role: string
  action: string
  rationale: string
}

export interface Gate {
  gate_id: string
  gate_name: string
  stage_id: string
  status: string
  artifact_snapshot?: Record<string, unknown> | null
  draft_artifact?: Record<string, unknown> | null
  is_resolved: boolean
  is_rejected: boolean
  decision: HitlDecision | null
}

export interface Mitigation {
  control_id: string
  title: string
  description: string
  residual_risk_after_control?: number
}

export interface Threat {
  id: string
  name: string
  description: string
  interface_id: string
  likelihood: string
  impact: string
  risk_score: number
  mitre_attack_techniques: string[]
  technical_mitigations: Mitigation[]
  administrative_mitigations: Mitigation[]
  decision?: ThreatDecision | null
}

export interface ThreatDecision {
  threat_id: string
  decision: string
  notes: string
  reviewer: string
}

export interface StageTokenUsage {
  request_count: number
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
}

export interface LLMMetrics {
  total_tokens: number
  request_count: number
  cached_tokens: number
  prompt_tokens: number
  completion_tokens: number
  reasoning_tokens: number
  by_stage: Record<string, StageTokenUsage>
}

export interface ThreatsResponse {
  threats: Threat[]
}

export interface GatesResponse {
  gates: Gate[]
}

export interface StagesResponse {
  stages: Stage[]
}

export interface MetricsResponse {
  metrics: LLMMetrics
}

export interface FullStateResponse {
  state: {
    next_stage_id: string | null
    hitl_paused_at_gate: string | null
    hitl_rejected_at_gate: string | null
  }
  threats: Threat[]
  gates: Gate[]
  stages: Stage[]
  metrics: LLMMetrics
  messages: string[]
}

export interface PromptStateResponse {
  last_prompt: unknown | null
  prompt_history: unknown[]
  prompts_by_stage: Record<string, unknown>
}

export interface ConnectionVerifyResponse {
  ok: boolean
  message: string
}
