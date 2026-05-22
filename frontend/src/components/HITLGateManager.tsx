import React, { useMemo, useState } from 'react'
import { Box, Button, Card, CardContent, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Typography, Stack, Paper, Alert, Chip, Divider } from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import SaveIcon from '@mui/icons-material/Save'
import type { Gate } from '../types/api'

const BASELINE_GATE_SEQUENCE = [
  'gate_0_input_integrity',
  'gate_1_normalization_review',
  'gate_1_scope_confirmation',
  'gate_2_boundary_approval',
  'gate_3_stride_calibration',
  'gate_4_threat_plausibility',
  'gate_9_stix_packaging_review',
  'gate_5_mitigation_adequacy',
  'gate_8_diagram_review',
  'gate_7_export_consistency',
]

const CONDITIONAL_GATE_AFTER: Record<string, string> = {
  gate_6_merge_conflict_resolution: 'gate_1_scope_confirmation',
}

const BASELINE_GATE_INDEX = new Map(
  BASELINE_GATE_SEQUENCE.map((gateId, index) => [gateId, index]),
)

const DEFAULT_GATE_NAME: Record<string, string> = {
  gate_0_input_integrity: 'Input Integrity Gate',
  gate_1_normalization_review: 'Normalization Review Gate',
  gate_1_scope_confirmation: 'Scope Confirmation Gate',
  gate_2_boundary_approval: 'Trust Boundary Approval Gate',
  gate_3_stride_calibration: 'STRIDE Calibration Gate',
  gate_4_threat_plausibility: 'Threat Plausibility Gate',
  gate_9_stix_packaging_review: 'STIX Packaging Review Gate',
  gate_5_mitigation_adequacy: 'Mitigation Adequacy Gate',
  gate_8_diagram_review: 'Diagram Review Gate',
  gate_7_export_consistency: 'Export Consistency Gate',
  gate_6_merge_conflict_resolution: 'Merge Conflict Resolution Gate',
}

const DEFAULT_GATE_STAGE_ID: Record<string, string> = {
  gate_0_input_integrity: 'agent_01',
  gate_1_normalization_review: 'agent_01',
  gate_1_scope_confirmation: 'agent_02',
  gate_2_boundary_approval: 'agent_03',
  gate_3_stride_calibration: 'agent_04',
  gate_4_threat_plausibility: 'agent_05',
  gate_9_stix_packaging_review: 'agent_06',
  gate_5_mitigation_adequacy: 'agent_07',
  gate_8_diagram_review: 'agent_08',
  gate_7_export_consistency: 'agent_09',
  gate_6_merge_conflict_resolution: 'agent_02',
}

function stageSortKey(stageId: string): number {
  const match = /^agent_(\d+)$/.exec(stageId)
  if (!match) {
    return Number.MAX_SAFE_INTEGER
  }
  return Number.parseInt(match[1], 10)
}

function stageDisplay(stageId: string): string {
  const key = stageSortKey(stageId)
  if (key === Number.MAX_SAFE_INTEGER) {
    return stageId
  }
  return `Stage ${key} (${stageId})`
}

function gateExecutionLabel(gateId: string): string {
  const baselineIndex = BASELINE_GATE_INDEX.get(gateId)
  if (baselineIndex !== undefined) {
    return `Gate ${baselineIndex}`
  }
  if (gateId === 'gate_6_merge_conflict_resolution') {
    return 'Gate 2.1'
  }
  return 'Gate ?'
}

interface HITLGateManagerProps {
  gates: Gate[]
  onGateDecision?: (gateId: string, action: string, rationale: string) => Promise<void>
  onResumePipeline?: (gateId: string) => Promise<void>
  pausedGateId?: string | null
}

function summarizeArtifact(data: Record<string, unknown> | null | undefined): string[] {
  if (!data || typeof data !== 'object') {
    return []
  }

  return Object.entries(data)
    .slice(0, 6)
    .map(([key, value]) => {
      if (Array.isArray(value)) {
        return `${key}: ${value.length} item${value.length === 1 ? '' : 's'}`
      }
      if (value && typeof value === 'object') {
        return `${key}: ${Object.keys(value).length} field${Object.keys(value).length === 1 ? '' : 's'}`
      }
      return `${key}: ${String(value)}`
    })
}

function gateReadableSummary(gate: Gate | null): string[] {
  if (!gate?.artifact_snapshot || typeof gate.artifact_snapshot !== 'object') {
    return []
  }

  const snapshot = gate.artifact_snapshot as Record<string, unknown>
  if (gate.gate_id === 'gate_0_input_integrity') {
    const preflight = snapshot.input_preflight as Record<string, unknown> | undefined
    if (!preflight || typeof preflight !== 'object') {
      return summarizeArtifact(snapshot)
    }
    const checks = (preflight.checks as Record<string, unknown> | undefined) ?? {}
    return [
      `Raw text length: ${String(preflight.raw_text_length ?? 0)}`,
      `Table count: ${String(preflight.table_count ?? 0)}`,
      `Source present: ${String(checks.source_present ?? false)}`,
      `Has raw text: ${String(checks.has_raw_text ?? false)}`,
      `Has tables: ${String(checks.has_tables ?? false)}`,
    ]
  }

  if (gate.gate_id === 'gate_1_normalization_review') {
    const review = snapshot.normalization_review as Record<string, unknown> | undefined
    if (!review || typeof review !== 'object') {
      return summarizeArtifact(snapshot)
    }
    const system = (review.system as Record<string, unknown> | undefined) ?? {}
    const counts = (review.counts as Record<string, unknown> | undefined) ?? {}
    const checks = (review.checks as Record<string, unknown> | undefined) ?? {}
    return [
      `System name: ${String(system.name ?? 'missing')}`,
      `Subsystems: ${String(counts.subsystems ?? 0)}`,
      `Components: ${String(counts.components ?? 0)}`,
      `Functions: ${String(counts.functions ?? 0)}`,
      `Interfaces: ${String(counts.interfaces ?? 0)}`,
      `System name present: ${String(checks.system_name_present ?? false)}`,
      `Interface count nonzero: ${String(checks.interface_count_nonzero ?? false)}`,
    ]
  }

  return summarizeArtifact(snapshot)
}

export const HITLGateManager: React.FC<HITLGateManagerProps> = ({
  gates,
  onGateDecision,
  onResumePipeline,
  pausedGateId,
}) => {
  const [selectedGate, setSelectedGate] = useState<Gate | null>(null)
  const [decisionRationale, setDecisionRationale] = useState('')

  // When a gate is selected, initialize rationale from persisted decision if available
  React.useEffect(() => {
    if (selectedGate && selectedGate.decision && selectedGate.decision.rationale) {
      setDecisionRationale(selectedGate.decision.rationale)
    } else if (selectedGate) {
      setDecisionRationale('')
    }
  }, [selectedGate])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const orderedGates = useMemo(() => {
    const byId = new Map(gates.map((gate) => [gate.gate_id, gate]))

    const baseline = BASELINE_GATE_SEQUENCE.map((gateId) => {
      const existing = byId.get(gateId)
      if (existing) {
        return existing
      }
      return {
        gate_id: gateId,
        gate_name: DEFAULT_GATE_NAME[gateId] ?? gateId,
        stage_id: DEFAULT_GATE_STAGE_ID[gateId] ?? 'agent_01',
        status: 'pending',
        artifact_snapshot: null,
        draft_artifact: null,
        is_resolved: false,
        is_rejected: false,
        decision: null,
      } as Gate
    })

    const conditionalGates = gates.filter((gate) => {
      if (!(gate.gate_id in CONDITIONAL_GATE_AFTER)) {
        return false
      }
      const normalizedStatus = gate.status.toLowerCase()
      return normalizedStatus !== 'pending' || gate.is_resolved || gate.is_rejected || !!gate.decision
    })
    for (const conditional of conditionalGates) {
      const anchorId = CONDITIONAL_GATE_AFTER[conditional.gate_id]
      const anchorIndex = baseline.findIndex((gate) => gate.gate_id === anchorId)
      const insertAt = anchorIndex >= 0 ? anchorIndex + 1 : baseline.length
      baseline.splice(insertAt, 0, conditional)
    }

    return baseline
  }, [gates])
  const effectiveGateStatus = (gate: Gate): string => {
    const normalized = gate.status.toLowerCase()
    if (pausedGateId && gate.gate_id === pausedGateId && normalized === 'pending') {
      return 'open'
    }
    return normalized
  }

  const gateCounts = useMemo(() => {
    return orderedGates.reduce(
      (counts, gate) => {
        const normalizedStatus = effectiveGateStatus(gate)
        if (gate.is_rejected || normalizedStatus === 'rejected') {
          counts.rejected += 1
        } else if (normalizedStatus === 'bypassed') {
          counts.bypassed += 1
        } else if (gate.is_resolved) {
          counts.approved += 1
        } else {
          counts.pending += 1
        }
        return counts
      },
      { approved: 0, rejected: 0, bypassed: 0, pending: 0 },
    )
  }, [orderedGates, pausedGateId])
  const resumableGate = useMemo(
    () => gates.find((gate) => gate.gate_id === pausedGateId && gate.is_resolved),
    [gates, pausedGateId],
  )

  const closeDialog = () => {
    setSelectedGate(null)
    setDecisionRationale('')
    setError(null)
  }

  const handleSubmitDecision = async (action: string) => {
    if (!selectedGate) {
      return
    }

    if (action !== 'save_draft' && !decisionRationale.trim()) {
      setError('Rationale is required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      if (onGateDecision) {
        await onGateDecision(selectedGate.gate_id, action, decisionRationale)
      }
      if (action !== 'save_draft') {
        closeDialog()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Decision submission failed')
    } finally {
      setLoading(false)
    }
  }

  const handleResume = async (gateId: string) => {
    setLoading(true)
    setError(null)
    try {
      if (onResumePipeline) {
        await onResumePipeline(gateId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Resume failed')
    } finally {
      setLoading(false)
    }
  }

  const selectedArtifactSummary = gateReadableSummary(selectedGate)
  const selectedStatus = selectedGate ? effectiveGateStatus(selectedGate) : ''
  const isPausedLockActive = !!pausedGateId
  const isSelectedPausedGate = !!selectedGate && selectedGate.gate_id === pausedGateId
  const canDecide = ['open', 'draft', 'rejected'].includes(selectedStatus) && (!isPausedLockActive || isSelectedPausedGate)
  const canResumeSelected = !!selectedGate && !!pausedGateId && selectedGate.gate_id === pausedGateId && selectedGate.is_resolved

  const isGateLocked = (gate: Gate): boolean => {
    if (!pausedGateId) {
      return false
    }
    return gate.gate_id !== pausedGateId
  }

  const handleReviewGate = (gate: Gate) => {
    if (isGateLocked(gate)) {
      return
    }
    setSelectedGate(gate)
  }

  const gateVisual = (gate: Gate): {
    icon: React.ReactNode
    accent: string
    background: string
    label: string
  } => {
    const normalizedStatus = effectiveGateStatus(gate)
    if (gate.is_rejected || normalizedStatus === 'rejected') {
      return {
        icon: <CancelIcon sx={{ color: 'error.main' }} />,
        accent: '#ef5350',
        background: 'rgba(239, 83, 80, 0.08)',
        label: 'Rejected',
      }
    }
    if (normalizedStatus === 'bypassed') {
      return {
        icon: <Box sx={{ width: 20, height: 20, borderRadius: '50%', border: '2px solid #9e9e9e' }} />,
        accent: '#9e9e9e',
        background: 'rgba(158, 158, 158, 0.10)',
        label: 'Bypassed',
      }
    }
    if (gate.is_resolved) {
      return {
        icon: <CheckCircleIcon sx={{ color: 'success.main' }} />,
        accent: '#4caf50',
        background: 'rgba(76, 175, 80, 0.10)',
        label: 'Approved',
      }
    }
    if (['open', 'draft'].includes(normalizedStatus)) {
      return {
        icon: <PlayArrowIcon sx={{ color: 'warning.main' }} />,
        accent: '#ffa726',
        background: 'rgba(255, 167, 38, 0.10)',
        label: normalizedStatus === 'draft' ? 'Draft' : 'Paused',
      }
    }
    return {
      icon: <Box sx={{ width: 20, height: 20, borderRadius: '50%', border: '2px solid #90a4ae' }} />,
      accent: '#90a4ae',
      background: 'rgba(144, 164, 174, 0.10)',
      label: 'Pending',
    }
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        HITL Gates
      </Typography>

      <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap' }}>
        <Chip label={`Approved (${gateCounts.approved})`} sx={{ backgroundColor: 'rgba(76, 175, 80, 0.18)', color: '#81c784' }} />
        <Chip label={`Rejected (${gateCounts.rejected})`} sx={{ backgroundColor: 'rgba(239, 83, 80, 0.18)', color: '#ef9a9a' }} />
        <Chip label={`Bypassed (${gateCounts.bypassed})`} sx={{ backgroundColor: 'rgba(158, 158, 158, 0.18)', color: '#cfd8dc' }} />
        <Chip label={`Pending (${gateCounts.pending})`} sx={{ backgroundColor: 'rgba(144, 164, 174, 0.18)', color: '#b0bec5' }} />
      </Stack>

      {pausedGateId && (
        <Alert severity={resumableGate ? 'success' : 'warning'} sx={{ mb: 2 }}>
          {resumableGate
            ? `${resumableGate.gate_name} is approved. Resume the pipeline to continue execution.`
            : `Pipeline paused at ${pausedGateId}. Review and decide this gate before continuing.`}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Stack spacing={1.25}>
        {orderedGates.map((gate) => {
          const visual = gateVisual(gate)
          return (
            <Card
              key={gate.gate_id}
              sx={{
                cursor: isGateLocked(gate) ? 'not-allowed' : 'pointer',
                opacity: isGateLocked(gate) ? 0.6 : 1,
                backgroundColor: visual.background,
                border: `1px solid ${visual.accent}33`,
                '&:hover': isGateLocked(gate) ? undefined : { boxShadow: 3 },
              }}
              onClick={() => handleReviewGate(gate)}
            >
              <CardContent sx={{ pb: 1, '&:last-child': { pb: 2 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {visual.icon}
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {gateExecutionLabel(gate.gate_id)} • {gate.gate_name}
                      </Typography>
                      <Chip size="small" label={visual.label} sx={{ backgroundColor: `${visual.accent}22`, color: visual.accent }} />
                    </Box>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {stageDisplay(gate.stage_id)} • {gate.gate_id}
                    </Typography>
                    {gate.decision && (
                      <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 0.5 }}>
                        {visual.label} by {gate.decision.actor}: {gate.decision.rationale}
                      </Typography>
                    )}
                    {gate.artifact_snapshot && (
                      <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                        {gateReadableSummary(gate).slice(0, 2).map((item) => (
                          <Chip key={item} label={item} size="small" variant="outlined" />
                        ))}
                      </Stack>
                    )}
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Button
                      variant="text"
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleReviewGate(gate)
                      }}
                      disabled={isGateLocked(gate)}
                    >
                      {isGateLocked(gate) ? 'Locked' : 'Review'}
                    </Button>
                    {pausedGateId === gate.gate_id && gate.is_resolved && (
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<PlayArrowIcon />}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleResume(gate.gate_id)
                        }}
                        disabled={loading}
                      >
                        Resume Pipeline
                      </Button>
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )
        })}
      </Stack>

      <Dialog open={selectedGate !== null} onClose={closeDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedGate?.gate_name}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                Gate ID
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {selectedGate?.gate_id}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                Stage
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {selectedGate?.stage_id}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                Current Status
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                {selectedStatus || selectedGate?.status}
              </Typography>
            </Box>
            {selectedArtifactSummary.length > 0 && (
              <>
                <Divider />
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Gate Context
                  </Typography>
                  <Stack spacing={1}>
                    {selectedArtifactSummary.map((item) => (
                      <Typography key={item} variant="body2" sx={{ color: 'text.secondary' }}>
                        {item}
                      </Typography>
                    ))}
                  </Stack>
                </Box>
              </>
            )}
            <TextField
              label="Rationale"
              multiline
              rows={4}
              fullWidth
              placeholder="Explain your decision..."
              value={decisionRationale}
              onChange={(e) => setDecisionRationale(e.target.value)}
              disabled={selectedGate?.is_resolved || (isPausedLockActive && !isSelectedPausedGate)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>Cancel</Button>
          <Button
            variant="outlined"
            startIcon={<SaveIcon />}
            onClick={() => handleSubmitDecision('save_draft')}
            disabled={loading || !canDecide}
          >
            Save Draft
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={() => handleSubmitDecision('reject')}
            disabled={loading || !canDecide || !decisionRationale.trim()}
          >
            Reject
          </Button>
          <Button
            variant="contained"
            color="success"
            onClick={() => handleSubmitDecision('accept_as_is')}
            disabled={loading || !canDecide || !decisionRationale.trim()}
          >
            Approve
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={() => selectedGate && handleResume(selectedGate.gate_id)}
            disabled={loading || !canResumeSelected}
          >
            Resume Pipeline
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  )
}
