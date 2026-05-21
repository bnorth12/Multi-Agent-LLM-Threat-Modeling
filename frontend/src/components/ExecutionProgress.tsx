import React from 'react'
import { Box, Typography, Tooltip } from '@mui/material'
import type { Stage, Gate } from '../types/api'

const TIMELINE_GATE_IDS = [
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

const GATE_STAGE_ID: Record<string, string> = {
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
}

const GATE_BOUNDARY_INDEX: Record<string, number> = {
  // 0 = before stage 1, 1..9 = after stage N
  gate_0_input_integrity: 0,
  gate_1_normalization_review: 1,
  gate_1_scope_confirmation: 2,
  gate_2_boundary_approval: 3,
  gate_3_stride_calibration: 4,
  gate_4_threat_plausibility: 5,
  gate_9_stix_packaging_review: 6,
  gate_5_mitigation_adequacy: 7,
  gate_8_diagram_review: 8,
  gate_7_export_consistency: 9,
  // Conditional merge conflict gate shares the post-stage-2 boundary.
  gate_6_merge_conflict_resolution: 2,
}

const ALL_STAGES: Stage[] = [
  { stage_id: 'agent_01', label: 'Input Normalizer', status: 'pending' },
  { stage_id: 'agent_02', label: 'Context Builder', status: 'pending' },
  { stage_id: 'agent_03', label: 'Trust Boundary Validator', status: 'pending' },
  { stage_id: 'agent_04', label: 'STRIDE Scorer', status: 'pending' },
  { stage_id: 'agent_05', label: 'Threat Generator', status: 'pending' },
  { stage_id: 'agent_06', label: 'STIX Packager', status: 'pending' },
  { stage_id: 'agent_07', label: 'Mitigation Generator', status: 'pending' },
  { stage_id: 'agent_08', label: 'Diagram Generator', status: 'pending' },
  { stage_id: 'agent_09', label: 'Report Writer', status: 'pending' },
]

interface ExecutionProgressProps {
  stages: Stage[]
  currentStage?: string | null
  gates?: Gate[] | null
  pausedGateId?: string | null
  statusText?: string | null
}

export const ExecutionProgress: React.FC<ExecutionProgressProps> = ({ stages, currentStage, gates, pausedGateId, statusText }) => {
  const stageMap = new Map(stages.map((stage) => [stage.stage_id, stage]))
  const displayedStages = ALL_STAGES.map((stage) => stageMap.get(stage.stage_id) ?? stage)
  const completedCount = displayedStages.filter((s) => s.status === 'complete').length
  const progressPercent = displayedStages.length > 0 ? (completedCount / displayedStages.length) * 100 : 0

  const isGatePausedForStage = (stageId: string): boolean => {
    const stageGates = (gates ?? []).filter((gate) => gate.stage_id === stageId)
    if (pausedGateId && stageGates.some((gate) => gate.gate_id === pausedGateId)) {
      return true
    }
    return stageGates.some((gate) => ['open', 'draft', 'paused'].includes(gate.status.toLowerCase()))
  }

  const getStageColor = (status: string, stageId: string): string => {
    if (isGatePausedForStage(stageId)) return '#ffa726'
    if (stageId === currentStage) return '#2196f3'
    if (status === 'complete') return '#4caf50'
    if (status === 'running') return '#2196f3'
    if (status === 'skipped') return '#9e9e9e'
    return '#757575'
  }

  const getStageOpacity = (stageId: string): number => {
    if (stageId === currentStage) return 1
    if (displayedStages.find((s) => s.stage_id === stageId)?.status === 'complete') return 1
    return 0.5
  }

  const getGateColor = (status: string): string => {
    const normalized = status.toLowerCase()
    if (['open', 'draft', 'paused'].includes(normalized)) return '#ffa726'
    if (['accepted_as_is', 'accepted_changes', 'approved'].includes(normalized)) return '#4caf50'
    if (['rejected'].includes(normalized)) return '#ef5350'
    if (['pending', 'bypassed'].includes(normalized)) return '#9e9e9e'
    return '#90a4ae'
  }

  const gateMarkers = React.useMemo(() => {
    if (displayedStages.length === 0) {
      return [] as Array<{ gate: Gate; xPos: number }>
    }

    const gateById = new Map((gates ?? []).map((gate) => [gate.gate_id, gate]))

    const timelineGates: Gate[] = TIMELINE_GATE_IDS.map((gateId) => {
      const existing = gateById.get(gateId)
      if (existing) {
        return existing
      }
      return {
        gate_id: gateId,
        gate_name: gateId,
        stage_id: GATE_STAGE_ID[gateId] ?? 'agent_01',
        status: 'pending',
        artifact_snapshot: null,
        draft_artifact: null,
        is_resolved: false,
        is_rejected: false,
        decision: null,
      }
    })

    type MarkerSeed = { gate: Gate; baseX: number; anchor: string }
    const seeds: MarkerSeed[] = []

    for (const gate of timelineGates) {
      const configuredBoundary = GATE_BOUNDARY_INDEX[gate.gate_id]
      if (configuredBoundary === undefined) {
        continue
      }

      const boundaryIndex = configuredBoundary
      const baseX = (boundaryIndex / displayedStages.length) * 100
      const anchor = `boundary:${boundaryIndex}`
      seeds.push({ gate, baseX, anchor })
    }

    const countsByAnchor = new Map<string, number>()
    for (const seed of seeds) {
      countsByAnchor.set(seed.anchor, (countsByAnchor.get(seed.anchor) ?? 0) + 1)
    }

    const usedByAnchor = new Map<string, number>()
    return seeds.map((seed) => {
      const used = usedByAnchor.get(seed.anchor) ?? 0
      usedByAnchor.set(seed.anchor, used + 1)
      const totalAtAnchor = countsByAnchor.get(seed.anchor) ?? 1
      const spreadStep = 0.85
      const offset = (used - (totalAtAnchor - 1) / 2) * spreadStep
      return {
        gate: seed.gate,
        xPos: Math.max(0, Math.min(100, seed.baseX + offset)),
      }
    })
  }, [gates, displayedStages])

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      {/* Compact Status Row */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
        <Typography variant="caption" sx={{ fontWeight: 600, color: 'primary.main', textTransform: 'uppercase', letterSpacing: 0.5 }}>
          Execution Timeline
        </Typography>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          {completedCount}/{displayedStages.length} • {Math.round(progressPercent)}%
        </Typography>
      </Box>

      {/* Timeline Visualization */}
      <Box sx={{ position: 'relative', height: 40, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 1, border: '1px solid rgba(62, 168, 255, 0.2)', overflow: 'visible' }}>
        {/* Stage Segments */}
        <Box sx={{ display: 'flex', height: '100%', position: 'relative' }}>
          {displayedStages.map((stage, index) => {
            const color = getStageColor(stage.status, stage.stage_id)
            const opacity = getStageOpacity(stage.stage_id)
            return (
              <Tooltip key={stage.stage_id} title={`${stage.label} - ${stage.status}`} arrow placement="top">
                <Box
                  sx={{
                    flex: 1,
                    backgroundColor: color,
                    opacity,
                    borderRight: index < displayedStages.length - 1 ? '1px solid rgba(255,255,255,0.1)' : 'none',
                    cursor: 'pointer',
                    transition: 'opacity 0.2s ease',
                    '&:hover': { opacity: 1 },
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.65rem',
                    fontWeight: 600,
                    color: 'rgba(255,255,255,0.9)',
                    textAlign: 'center',
                    px: 0.5,
                  }}
                >
                  <Box component="span" sx={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{stage.label}</Box>
                </Box>
              </Tooltip>
            )
          })}
        </Box>

        {/* HITL Gate Markers (Triangle Markers) */}
        {gateMarkers.length > 0 && (
          <Box
            component="svg"
            sx={{
              position: 'absolute',
              top: '-12px',
              left: 0,
              right: 0,
              width: '100%',
              height: '12px',
              pointerEvents: 'none',
            }}
            viewBox="0 0 100 12"
            preserveAspectRatio="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            {gateMarkers.map(({ gate, xPos }, idx) => {
              const statusColor = getGateColor(gate.status)

              return (
                <Tooltip key={gate.gate_id} title={`Gate: ${gate.gate_id} - ${gate.status}`} placement="top">
                  <g key={`gate-${idx}`}>
                    {/* Downward-pointing triangle */}
                    <polygon
                      points={`${xPos},0 ${xPos - 1},12 ${xPos + 1},12`}
                      fill={statusColor}
                      stroke="#000"
                      strokeWidth="0.5"
                      opacity="0.8"
                    />
                  </g>
                </Tooltip>
              )
            })}
          </Box>
        )}
      </Box>

      {/* Compact Legend */}
      <Box sx={{ display: 'flex', gap: 2, fontSize: '0.7rem', justifyContent: 'flex-start' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box sx={{ width: 10, height: 10, backgroundColor: '#4caf50', borderRadius: 0.5 }} />
          <span>Complete</span>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box sx={{ width: 10, height: 10, backgroundColor: '#2196f3', borderRadius: 0.5 }} />
                    <span>Running</span>
        </Box>
        {gates && gates.some((g) => ['open', 'draft', 'paused'].includes(g.status.toLowerCase())) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 10, height: 8, clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)', backgroundColor: '#ffa726' }} />
            <span>Gate Paused</span>
          </Box>
        )}
        {gates && gates.some((g) => ['pending', 'bypassed'].includes(g.status.toLowerCase())) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 10, height: 8, clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)', backgroundColor: '#9e9e9e' }} />
            <span>Gate Pending/Bypassed</span>
          </Box>
        )}
      </Box>

      {statusText && (
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.75)', width: '100%', textAlign: 'center' }}>
          {statusText}
        </Typography>
      )}
    </Box>
  )
}
