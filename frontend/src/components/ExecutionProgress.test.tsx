import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { ExecutionProgress } from './ExecutionProgress'

afterEach(() => {
  cleanup()
})

describe('ExecutionProgress', () => {
  it('shows running activity and stale watchdog telemetry in the timeline header', () => {
    render(
      <ExecutionProgress
        stages={[
          { stage_id: 'agent_01', label: 'Input Normalizer', status: 'complete' },
          { stage_id: 'agent_02', label: 'Context Builder', status: 'running' },
        ]}
        currentStage="agent_02"
        currentStageLabel="Context Builder"
        statusText="Running Context Builder"
        showRuntimeActivity
        heartbeatAgeSeconds={12}
        heartbeatTimeoutSeconds={10}
        gates={[]}
      />,
    )

    expect(screen.getByText('Execution Timeline')).toBeInTheDocument()
    expect(screen.getByText('Running Context Builder', { selector: '.MuiChip-label' })).toBeInTheDocument()
    expect(screen.getByText('Running Context Builder', { selector: '.MuiTypography-caption' })).toBeInTheDocument()
    expect(screen.getByText('Watchdog Stale 12.0s / 10.0s')).toBeInTheDocument()
  })

  it('omits runtime chips when no active stage or watchdog telemetry is present', () => {
    render(
      <ExecutionProgress
        stages={[{ stage_id: 'agent_01', label: 'Input Normalizer', status: 'complete' }]}
        currentStage={null}
        currentStageLabel={null}
        statusText="Run completed"
        showRuntimeActivity={false}
        heartbeatAgeSeconds={null}
        heartbeatTimeoutSeconds={null}
        gates={[]}
      />,
    )

    expect(screen.queryByText(/Pipeline running|Running /, { selector: '.MuiChip-label' })).not.toBeInTheDocument()
    expect(screen.queryByText(/Watchdog/)).not.toBeInTheDocument()
    expect(screen.getByText('Run completed')).toBeInTheDocument()
  })

  it('renders narrow parse segments with brown in-progress and green complete states', () => {
    render(
      <ExecutionProgress
        stages={[
          { stage_id: 'agent_01', label: 'Input Normalizer', status: 'complete' },
          { stage_id: 'agent_02', label: 'Context Builder', status: 'complete' },
          { stage_id: 'agent_03', label: 'Trust Boundary Validator', status: 'complete' },
          { stage_id: 'agent_04', label: 'STRIDE Scorer', status: 'complete' },
          { stage_id: 'agent_05', label: 'Threat Generator', status: 'running' },
        ]}
        currentStage="agent_05"
        currentStageLabel="Threat Generator"
        gates={[
          {
            gate_id: 'gate_3_stride_calibration',
            gate_name: 'gate_3_stride_calibration',
            stage_id: 'agent_04',
            status: 'approved',
            artifact_snapshot: null,
            draft_artifact: null,
            is_resolved: true,
            is_rejected: false,
            decision: null,
          },
          {
            gate_id: 'gate_4_threat_plausibility',
            gate_name: 'gate_4_threat_plausibility',
            stage_id: 'agent_05',
            status: 'pending',
            artifact_snapshot: null,
            draft_artifact: null,
            is_resolved: false,
            is_rejected: false,
            decision: null,
          },
        ]}
      />,
    )

    expect(screen.getByText('Parsing In Progress')).toBeInTheDocument()
    expect(screen.getByText('Parse Complete')).toBeInTheDocument()

    expect(screen.getByTestId('parsing-segment-gate_3_stride_calibration')).toHaveStyle({ backgroundColor: '#4caf50' })
    expect(screen.getByTestId('parsing-segment-gate_4_threat_plausibility')).toHaveStyle({ backgroundColor: '#8d6e63' })
  })
})
