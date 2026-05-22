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
})
