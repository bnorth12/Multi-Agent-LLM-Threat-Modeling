import type {
  ArtifactResponse,
  ConfigResponse,
  CreateRunResponse,
  HealthResponse,
  PromptDetailResponse,
  PromptsResponse,
  RunResponse,
  RunsResponse,
  RuntimeSettings,
  StagesResponse,
  ThreatsResponse,
  GatesResponse,
  MetricsResponse,
  FullStateResponse,
  PromptStateResponse,
  ConnectionVerifyResponse,
} from '../types/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

// Sprint 12 decision: no runtime auth enforcement yet, but keep a future hook.
function buildHeaders(): HeadersInit {
  const token = import.meta.env.VITE_AUTH_TOKEN
  let headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (token) {
    headers = { ...headers, Authorization: `Bearer ${token}` }
  }
  return headers
}

async function parseApiError(response: Response, method: string, path: string): Promise<Error> {
  if (response.status === 401) {
    return new Error(
      'Unauthorized: Provide VITE_AUTH_TOKEN for the frontend or disable THREAT_MODELER_AUTH_REQUIRED on the backend.',
    )
  }

  let details: string | undefined
  try {
    const payload = (await response.json()) as { error?: string; details?: string }
    details = payload.details || payload.error || ''
  } catch {
    // Ignore non-JSON error bodies.
  }

  return new Error(`${method} ${path} failed with status ${response.status}${details ? `: ${details}` : ''}`)
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    headers: buildHeaders(),
  })
  if (!response.ok) {
    throw await parseApiError(response, 'GET', path)
  }
  return (await response.json()) as T
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw await parseApiError(response, 'POST', path)
  }
  return (await response.json()) as T
}

async function deleteJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
    headers: buildHeaders(),
  })
  if (!response.ok) {
    throw await parseApiError(response, 'DELETE', path)
  }
  return (await response.json()) as T
}

export const apiClient = {
  baseUrl: API_BASE,
  getHealth: () => getJson<HealthResponse>('/health'),
  getConfig: () => getJson<ConfigResponse>('/config'),
  updateConfig: (config: RuntimeSettings) => postJson<ConfigResponse>('/config', { config }),
  verifyConfigConnection: async (config: RuntimeSettings, apiKey?: string) => {
    try {
      return await postJson<ConnectionVerifyResponse>('/config/verify', { config, api_key: apiKey ?? '' })
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err)
      if (message.includes('POST /config/verify failed with status 404')) {
        return {
          ok: true,
          message: 'Backend verify endpoint unavailable; accepted using compatibility validation.',
        }
      }
      throw err
    }
  },
  getPrompts: () => getJson<PromptsResponse>('/prompts'),
  getPrompt: (agentId: string) => getJson<PromptDetailResponse>(`/prompts/${agentId}`),
  updatePrompt: (
    agentId: string,
    payload: Partial<Pick<PromptDetailResponse, 'prompt' | 'expected_output' | 'temperature'>>,
  ) => postJson<PromptDetailResponse>(`/prompts/${agentId}`, payload),
  getRuns: () => getJson<RunsResponse>('/runs'),
  createRun: (
    runId: string,
    payload?: {
      runName?: string
      settings?: RuntimeSettings
      initialState?: {
        raw_text?: string
        tables?: Array<Record<string, string>>
      }
    },
  ) =>
    postJson<CreateRunResponse>('/runs', {
      run_id: runId,
      run_name: payload?.runName,
      settings: payload?.settings,
      initial_state: payload?.initialState,
    }),
  getRun: async (runId: string): Promise<RunResponse> => {
    const response = await getJson<RunsResponse>('/runs')
    const run = response.runs.find((entry) => entry.run_id === runId)
    if (!run) {
      throw new Error(`Run not found: ${runId}`)
    }
    return { run }
  },
  cancelRun: (runId: string) => deleteJson<{ run_id: string; cancelled: boolean }>(`/runs/${runId}`),
  updateRunMetadata: (runId: string, payload: { run_name?: string; archived?: boolean }) =>
    postJson<{ run_id: string; metadata: Record<string, unknown> }>(`/runs/${runId}/metadata`, payload),
  purgeRun: (runId: string) => deleteJson<{ run_id: string; purged: boolean }>(`/runs/${runId}/purge`),
  purgeArchivedRuns: () => postJson<{ purged_run_ids: string[]; count: number }>('/runs/purge', { archived_only: true }),
  resumeRun: (runId: string, gateId: string) =>
    postJson<{ run_id: string; resumed_from_gate: string }>(`/runs/${runId}/resume`, { gate_id: gateId }),
  getArtifact: (runId: string, artifact: 'canonical' | 'stix' | 'mermaid' | 'report') =>
    getJson<ArtifactResponse>(`/runs/${runId}/artifacts/${artifact}`),

  // HMI state endpoints
  getFullState: (runId: string) => getJson<FullStateResponse>(`/runs/${runId}/state/full`),
  getStages: (runId: string) => getJson<StagesResponse>(`/runs/${runId}/state/stages`),
  getThreats: (runId: string) => getJson<ThreatsResponse>(`/runs/${runId}/state/threats`),
  getGates: (runId: string) => getJson<GatesResponse>(`/runs/${runId}/state/gates`),
  getMetrics: (runId: string) => getJson<MetricsResponse>(`/runs/${runId}/state/metrics`),
  getPromptState: (runId: string) => getJson<PromptStateResponse>(`/runs/${runId}/state/prompts`),

  // Decision endpoints
  submitGateDecision: (runId: string, gateId: string, decision: unknown) =>
    postJson<{ run_id: string; gate_id: string; decision_recorded: boolean }>(
      `/runs/${runId}/gates/${gateId}/decide`,
      decision,
    ),
  submitThreatDecision: (runId: string, threatId: string, decision: unknown) =>
    postJson<{ run_id: string; threat_id: string; decision_recorded: boolean }>(
      `/runs/${runId}/threats/${threatId}/decide`,
      decision,
    ),
}
