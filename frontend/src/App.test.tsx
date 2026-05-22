import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockRun = vi.hoisted(() => ({
  run_id: 'run-123',
  run_name: 'Demo Run',
  archived: false,
  status: 'running',
  pause_gate: null,
  error: null,
  last_heartbeat_time: 1716282600,
  heartbeat_timeout_seconds: 30,
  heartbeat_age_seconds: 5,
  start_time: null,
  end_time: null,
  settings: null,
  result_state: null,
  live_state: null,
}))

vi.mock('./api/client', () => ({
  apiClient: {
    getHealth: vi.fn().mockResolvedValue({ status: 'ok' }),
    getRuns: vi.fn().mockResolvedValue({ runs: [mockRun] }),
    getFullState: vi.fn().mockResolvedValue({
      metadata: {},
      state: {
        next_stage_id: 'agent_03',
        hitl_paused_at_gate: null,
        hitl_rejected_at_gate: null,
      },
      stages: [{ stage_id: 'agent_03', label: 'Trust Boundary Validator', status: 'running' }],
      threats: [],
      gates: [],
      metrics: null,
    }),
    updateConfig: vi.fn().mockResolvedValue({}),
    createRun: vi.fn().mockResolvedValue({}),
    submitGateDecision: vi.fn().mockResolvedValue({}),
    resumeRun: vi.fn().mockResolvedValue({}),
    submitThreatDecision: vi.fn().mockResolvedValue({}),
    updateRunMetadata: vi.fn().mockResolvedValue({}),
    purgeRun: vi.fn().mockResolvedValue({}),
  },
}))

vi.mock('./components/RoleSelect', () => ({
  RoleSelect: () => null,
}))

vi.mock('./components/PipelineConfig', () => ({
  PipelineConfig: () => null,
}))

vi.mock('./components/InputEntry', () => ({
  InputEntry: () => null,
}))

vi.mock('./components/ExecutionProgress', () => ({
  ExecutionProgress: () => null,
}))

vi.mock('./components/HITLGateManager', () => ({
  HITLGateManager: () => null,
}))

vi.mock('./components/ThreatReview', () => ({
  ThreatReview: () => null,
}))

vi.mock('./components/TokenUsageDashboard', () => ({
  TokenUsageDashboard: () => null,
}))

vi.mock('./components/ArtifactsViewer', () => ({
  ArtifactsViewer: () => null,
}))

vi.mock('./components/LastPromptViewer', () => ({
  LastPromptViewer: () => null,
}))

vi.mock('./components/PromptEditor', () => ({
  PromptEditor: () => null,
}))

import App from './App'

describe('App shell', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('keeps the navigation pane visible and does not render a menu toggle', async () => {
    const user = userEvent.setup()

    render(<App />)

    await waitFor(() => expect(screen.getByText('Demo Run')).toBeInTheDocument())
    expect(screen.queryByRole('button', { name: 'Menu' })).not.toBeInTheDocument()
    expect(screen.getByText('All Runs')).toBeInTheDocument()

    const threatModelerTitle = screen.getByText('Threat Modeler')
    expect(threatModelerTitle).toBeVisible()

    await user.click(screen.getByText('Demo Run'))

    await waitFor(() => expect(screen.getByText('Active Run')).toBeInTheDocument())
    expect(screen.getByText('Threat Modeler')).toBeVisible()
    expect(screen.queryByRole('button', { name: 'Menu' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Execution' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Canonical Graph' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Trust Boundaries' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'STRIDE Viewer' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Threats' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Mermaid Diagrams' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'STIX Bundle' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Report' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'HITL GATES' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'TOKENS' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Last Prompt' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Prompt Editor' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Canonical Graph' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Trust Boundaries' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'STRIDE Viewer' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Threats' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Mermaid Diagrams' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'STIX Bundle' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Report' })).toBeInTheDocument()
    expect(screen.getByText('Running Trust Boundary Validator')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Last Prompt' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Prompt Editor' })).toBeInTheDocument()
  })
})
