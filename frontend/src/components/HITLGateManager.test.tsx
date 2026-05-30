import { fireEvent, render, screen, within, cleanup } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { HITLGateManager } from './HITLGateManager'
import type { Gate } from '../types/api'

afterEach(() => {
  cleanup()
})

function buildGate(overrides: Partial<Gate>): Gate {
  return {
    gate_id: 'gate_2_boundary_approval',
    gate_name: 'Gate 2 Boundary Approval',
    stage_id: 'agent_03',
    status: 'open',
    artifact_snapshot: {
      interfaces: [{ id: 'if-1' }, { id: 'if-2' }],
      summary: 'Trust boundary crossing review',
    },
    draft_artifact: null,
    is_resolved: false,
    is_rejected: false,
    decision: null,
    ...overrides,
  }
}

describe('HITLGateManager', () => {
  it('submits approve decision from the review dialog', async () => {
    const onGateDecision = vi.fn<
      (gateId: string, action: string, rationale: string) => Promise<void>
    >().mockResolvedValue(undefined)

    render(
      <HITLGateManager
        gates={[buildGate({ status: 'open' })]}
        onGateDecision={onGateDecision}
        pausedGateId="gate_2_boundary_approval"
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Review' }))
    const dialog = await screen.findByRole('dialog')

    fireEvent.change(within(dialog).getByRole('textbox', { name: 'Rationale' }), {
      target: { value: 'Approved' },
    })
    fireEvent.click(within(dialog).getByRole('button', { name: 'Approve' }))

    expect(onGateDecision).toHaveBeenCalledWith(
      'gate_2_boundary_approval',
      'accept_as_is',
      'Approved',
    )
  })

  it('submits reject decision from the review dialog', async () => {
    const onGateDecision = vi.fn<
      (gateId: string, action: string, rationale: string) => Promise<void>
    >().mockResolvedValue(undefined)

    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_4_threat_plausibility',
            gate_name: 'Gate 4 Threat Plausibility',
            stage_id: 'agent_05',
            status: 'rejected',
            is_rejected: true,
          }),
        ]}
        onGateDecision={onGateDecision}
      />,
    )

    const threatGateTitle = screen.getByText('Gate 5 • Gate 4 Threat Plausibility')
    const threatGateRow = threatGateTitle.closest('.MuiCardContent-root')
    expect(threatGateRow).not.toBeNull()
    fireEvent.click(within(threatGateRow as HTMLElement).getByRole('button', { name: 'Review' }))
    const dialog = await screen.findByRole('dialog')

    fireEvent.change(within(dialog).getByRole('textbox', { name: 'Rationale' }), {
      target: { value: 'Rejecting' },
    })
    fireEvent.click(within(dialog).getByRole('button', { name: 'Reject' }))

    expect(onGateDecision).toHaveBeenCalledWith(
      'gate_4_threat_plausibility',
      'reject',
      'Rejecting',
    )
  })

  it('shows a single resume control for the currently paused approved gate', async () => {
    const onResumePipeline = vi.fn<(gateId: string) => Promise<void>>().mockResolvedValue(undefined)

    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_3_stride_calibration',
            gate_name: 'Gate 3 STRIDE Calibration',
            stage_id: 'agent_04',
            status: 'accepted_as_is',
            is_resolved: true,
            decision: {
              gate_id: 'gate_3_stride_calibration',
              actor: 'analyst',
              role: 'Reviewer',
              action: 'accept_as_is',
              rationale: 'STRIDE mapping looks correct.',
            },
          }),
          buildGate({
            gate_id: 'gate_5_mitigation_adequacy',
            gate_name: 'Gate 5 Mitigation Adequacy',
            stage_id: 'agent_07',
            status: 'accepted_as_is',
            is_resolved: true,
            decision: {
              gate_id: 'gate_5_mitigation_adequacy',
              actor: 'analyst',
              role: 'Reviewer',
              action: 'accept_as_is',
              rationale: 'Mitigations are acceptable.',
            },
          }),
        ]}
        onResumePipeline={onResumePipeline}
        pausedGateId="gate_3_stride_calibration"
      />,
    )

    expect(screen.getAllByText('Approved (2)')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Rejected (0)')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Bypassed (0)')[0]).toBeInTheDocument()
    expect(screen.getAllByText(/Pending \(\d+\)/).length).toBeGreaterThan(0)

    const strideGateTitle = screen.getAllByText('Gate 4 • Gate 3 STRIDE Calibration')[0]
    const strideGateRow = strideGateTitle.closest('.MuiCardContent-root')
    expect(strideGateRow).not.toBeNull()
    const resumeButton = within(strideGateRow as HTMLElement).getByRole('button', {
      name: 'Resume Pipeline',
    })

    fireEvent.click(resumeButton)
    expect(onResumePipeline).toHaveBeenCalledWith('gate_3_stride_calibration')
  })

  it('renders all provided gates in order with summary counts', () => {
    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_1_normalization_review',
            gate_name: 'Normalization Review Gate',
            stage_id: 'agent_01',
            status: 'pending',
          }),
          buildGate({
            gate_id: 'gate_8_diagram_review',
            gate_name: 'Diagram Review Gate',
            stage_id: 'agent_08',
            status: 'bypassed',
            is_resolved: true,
          }),
          buildGate({
            gate_id: 'gate_1_scope_confirmation',
            gate_name: 'Scope Confirmation Gate',
            stage_id: 'agent_02',
            status: 'accepted_as_is',
            is_resolved: true,
          }),
          buildGate({
            gate_id: 'gate_6_merge_conflict_resolution',
            gate_name: 'Merge Conflict Resolution Gate',
            stage_id: 'agent_02',
            status: 'open',
          }),
          buildGate({
            gate_id: 'gate_7_export_consistency',
            gate_name: 'Export Consistency Gate',
            stage_id: 'agent_09',
            status: 'open',
          }),
          buildGate({
            gate_id: 'gate_4_threat_plausibility',
            gate_name: 'Threat Plausibility Gate',
            stage_id: 'agent_05',
            status: 'rejected',
            is_rejected: true,
          }),
        ]}
      />,
    )

    expect(screen.getAllByText('Approved (1)')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Rejected (1)')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Bypassed (1)')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Pending (8)')[0]).toBeInTheDocument()

    const gateTitles = Array.from(
      document.querySelectorAll('.MuiCardContent-root .MuiTypography-body2'),
    )
      .map((node) => node.textContent ?? '')
      .filter((text) => /^Gate (\d|2\.1) • .* Gate$/.test(text))
    const uniqueGateTitles = [...new Set(gateTitles)]

    expect(uniqueGateTitles).toContain('Gate 1 • Normalization Review Gate')
    expect(uniqueGateTitles).toContain('Gate 2 • Scope Confirmation Gate')
    expect(uniqueGateTitles).toContain('Gate 2.1 • Merge Conflict Resolution Gate')
    expect(uniqueGateTitles).toContain('Gate 5 • Threat Plausibility Gate')
    expect(uniqueGateTitles).toContain('Gate 8 • Diagram Review Gate')
    expect(uniqueGateTitles).toContain('Gate 9 • Export Consistency Gate')

    expect(uniqueGateTitles.indexOf('Gate 2 • Scope Confirmation Gate')).toBeGreaterThan(-1)
    expect(uniqueGateTitles.indexOf('Gate 2.1 • Merge Conflict Resolution Gate')).toBeGreaterThan(-1)
    expect(uniqueGateTitles.indexOf('Gate 3 • Trust Boundary Approval Gate')).toBeGreaterThan(-1)
  })

  it('locks non-paused gates while run is paused', async () => {
    const onGateDecision = vi.fn<
      (gateId: string, action: string, rationale: string) => Promise<void>
    >().mockResolvedValue(undefined)

    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_2_boundary_approval',
            gate_name: 'Gate 2 Boundary Approval',
            status: 'open',
          }),
          buildGate({
            gate_id: 'gate_4_threat_plausibility',
            gate_name: 'Gate 4 Threat Plausibility',
            stage_id: 'agent_05',
            status: 'draft',
          }),
        ]}
        onGateDecision={onGateDecision}
        pausedGateId="gate_2_boundary_approval"
      />,
    )

    const reviewButtons = screen.getAllByRole('button', { name: 'Review' })
    const lockedButtons = screen.getAllByRole('button', { name: 'Locked' })
    expect(reviewButtons.length).toBeGreaterThan(0)
    expect(lockedButtons.length).toBeGreaterThan(0)
    expect(reviewButtons[0]).toBeEnabled()
    expect(lockedButtons[0]).toBeDisabled()

    fireEvent.click(lockedButtons[0])
    expect(onGateDecision).not.toHaveBeenCalled()
  })

  it('allows decisions when paused gate arrives as pending', async () => {
    const onGateDecision = vi.fn<
      (gateId: string, action: string, rationale: string) => Promise<void>
    >().mockResolvedValue(undefined)

    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_0_input_integrity',
            gate_name: 'Input Integrity Gate',
            stage_id: 'agent_01',
            status: 'pending',
            artifact_snapshot: {
              input_preflight: {
                raw_text_length: 48,
                raw_text_preview: 'System: AV\nOwner: Flight Ops',
                table_count: 1,
                table_headers_preview: ['system', 'owner'],
                checks: {
                  source_present: true,
                  has_raw_text: true,
                  has_tables: true,
                },
              },
            },
          }),
        ]}
        onGateDecision={onGateDecision}
        pausedGateId="gate_0_input_integrity"
      />,
    )

    const gateTitle = screen.getByText(/Gate 0 .* Input Integrity Gate/)
    const gateRow = gateTitle.closest('.MuiCardContent-root')
    expect(gateRow).not.toBeNull()
    fireEvent.click(within(gateRow as HTMLElement).getByRole('button', { name: 'Review' }))
    const dialog = await screen.findByRole('dialog')

    fireEvent.change(within(dialog).getByRole('textbox', { name: 'Rationale' }), {
      target: { value: 'Input preflight checks look correct.' },
    })

    const approveButton = within(dialog).getByRole('button', { name: 'Approve' })
    expect(approveButton).toBeEnabled()
    fireEvent.click(approveButton)

    expect(onGateDecision).toHaveBeenCalledWith(
      'gate_0_input_integrity',
      'accept_as_is',
      'Input preflight checks look correct.',
    )
  })

  it('shows Gate 0 preflight details when parsed input data is available', async () => {
    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_0_input_integrity',
            gate_name: 'Input Integrity Gate',
            stage_id: 'agent_01',
            status: 'pending',
            artifact_snapshot: {
              input_preflight: {
                raw_text_length: 48,
                raw_text_preview: 'System: AV\nOwner: Flight Ops',
                table_count: 1,
                table_row_count: 1,
                table_non_empty_row_count: 1,
                table_header_count: 2,
                table_headers_preview: ['system', 'owner'],
                summary: {
                  source_presence: 'present',
                  text_summary: '48 non-whitespace characters',
                  table_summary: '1 row(s), 2 unique header(s)',
                },
                checks: {
                  source_present: true,
                  source_provenance_complete: true,
                  has_raw_text: true,
                  has_tables: true,
                },
              },
            },
          }),
        ]}
        pausedGateId="gate_0_input_integrity"
      />,
    )

    const gateTitle = screen.getByText(/Gate 0 .* Input Integrity Gate/)
    const gateRow = gateTitle.closest('.MuiCardContent-root')
    expect(gateRow).not.toBeNull()
    const reviewButton = within(gateRow as HTMLElement).getByRole('button', { name: 'Review' })
    expect(reviewButton).toBeEnabled()

    fireEvent.click(reviewButton)
    const dialog = await screen.findByRole('dialog')

    expect(within(dialog).getByText('Input Integrity Summary')).toBeInTheDocument()
    expect(within(dialog).getByText('Source presence: present')).toBeInTheDocument()
    expect(within(dialog).getByText('Text summary: 48 non-whitespace characters')).toBeInTheDocument()
    expect(within(dialog).getByText('Table summary: 1 row(s), 2 unique header(s)')).toBeInTheDocument()
    expect(within(dialog).getByText('Raw Text Preview')).toBeInTheDocument()
    expect(within(dialog).getByText(/System: AV/)).toBeInTheDocument()
    expect(within(dialog).getByText('Detected Table Headers')).toBeInTheDocument()
    expect(within(dialog).getByText('system')).toBeInTheDocument()
    expect(within(dialog).getByText('owner')).toBeInTheDocument()
  })

  it('shows waiting state and disables review when paused gate has no context data yet', () => {
    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_7_export_consistency',
            gate_name: 'Export Consistency Gate',
            stage_id: 'agent_09',
            status: 'open',
            artifact_snapshot: null,
          }),
        ]}
        pausedGateId="gate_7_export_consistency"
      />,
    )

    expect(screen.getByText('Pipeline paused at gate_7_export_consistency. Waiting for parser data before gate review is enabled.')).toBeInTheDocument()
    const waitingButton = screen.getByRole('button', { name: 'Waiting on Data' })
    expect(waitingButton).toBeDisabled()
  })

  it('disables review when an open gate has no context data even outside pause mode', () => {
    render(
      <HITLGateManager
        gates={[
          buildGate({
            gate_id: 'gate_3_stride_calibration',
            gate_name: 'Gate 3 STRIDE Calibration',
            stage_id: 'agent_04',
            status: 'open',
            artifact_snapshot: null,
          }),
        ]}
      />,
    )

    const waitingButton = screen.getByRole('button', { name: 'Waiting on Data' })
    expect(waitingButton).toBeDisabled()
  })
})
