import { useEffect, useState, useCallback } from 'react'
import {
  AppBar,
  Toolbar,
  Box,
  Container,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Button,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Checkbox,
  FormControlLabel,
  Paper,
  Typography,
  Chip,
} from '@mui/material'
import * as XLSX from 'xlsx'
import { apiClient } from './api/client'
import type { RunEntry, FullStateResponse, Stage, Gate, LLMMetrics } from './types/api'
import { RoleSelect } from './components/RoleSelect'
import { PipelineConfig } from './components/PipelineConfig'
import type { PipelineConfigData } from './components/PipelineConfig'
import { InputEntry } from './components/InputEntry'
import { ExecutionProgress } from './components/ExecutionProgress'
import { HITLGateManager } from './components/HITLGateManager'
import { TokenUsageDashboard } from './components/TokenUsageDashboard'
import { ArtifactsViewer } from './components/ArtifactsViewer'
import { LastPromptViewer } from './components/LastPromptViewer'
import { PromptEditor } from './components/PromptEditor'

type TabValue = 'gates' | 'tokens' | 'artifacts' | 'last_prompt' | 'prompt_editor'
type WizardStep = 'home' | 'role-select' | 'pipeline-config' | 'input-entry' | 'creating-run' | 'monitoring'
type ParsedInputBundle = {
  rawText: string
  tables: Array<Record<string, string>>
  parseWarnings: string[]
}

function uuidv4() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (char) => {
    const rnd = (Math.random() * 16) | 0
    const value = char === 'x' ? rnd : (rnd & 0x3) | 0x8
    return value.toString(16)
  })
}

function mapPipelineConfigToRuntimeSettings(config: PipelineConfigData) {
  return {
    model: {
      provider: config.provider,
      model_name: config.modelName,
      api_key: config.apiKey,
      offline_only: config.provider === 'fixture',
      connection_url: config.connectionUrl,
      endpoint_mode: 'chat_completions',
      request_timeout_seconds: 90,
      request_max_attempts: 2,
    },
    pipeline: {
      execution_mode: 'langgraph-compatible',
      enabled_stage_ids: config.enabledStages,
      stop_on_validation_error: false,
      require_hitl_gates: config.requireHitlGates,
    },
  }
}

function _sheetToRows(sheet: XLSX.WorkSheet, sourceFile: string): Array<Record<string, string>> {
  const grid = XLSX.utils.sheet_to_json<(string | number | boolean | null)[]>(sheet, {
    header: 1,
    defval: '',
    raw: false,
    blankrows: false,
  })

  if (!grid.length) {
    return []
  }

  const headerRow = (grid[0] ?? []) as Array<string | number | boolean | null>
  const headerCells = headerRow.map((value: string | number | boolean | null, index: number) => {
    const text = String(value ?? '').trim()
    return text || `col_${index}`
  })

  const dedupedHeaders: string[] = []
  const used = new Map<string, number>()
  for (const header of headerCells) {
    const seen = used.get(header) ?? 0
    used.set(header, seen + 1)
    dedupedHeaders.push(seen === 0 ? header : `${header}_${seen + 1}`)
  }

  return (grid.slice(1) as Array<Array<string | number | boolean | null>>).map((row) => {
    const entry: Record<string, string> = { _source_file: sourceFile }
    dedupedHeaders.forEach((header, index) => {
      entry[header] = String(row[index] ?? '')
    })
    return entry
  })
}

async function _parseInputFiles(files: File[]): Promise<ParsedInputBundle> {
  const rawParts: string[] = []
  const tables: Array<Record<string, string>> = []
  const parseWarnings: string[] = []

  for (const file of files) {
    const lower = file.name.toLowerCase()
    const ext = lower.includes('.') ? lower.split('.').pop() ?? '' : ''

    if (ext === 'md' || ext === 'txt' || ext === 'yaml' || ext === 'yml') {
      const text = await file.text()
      rawParts.push(`# --- ${file.name} ---\n${text}`)
      continue
    }

    if (ext === 'csv') {
      try {
        const text = await file.text()
        const workbook = XLSX.read(text, { type: 'string', raw: false })
        const firstSheetName = workbook.SheetNames[0]
        const firstSheet = firstSheetName ? workbook.Sheets[firstSheetName] : undefined
        if (!firstSheet) {
          parseWarnings.push(`CSV file '${file.name}' had no readable sheet.`)
          continue
        }
        tables.push(..._sheetToRows(firstSheet, file.name))
      } catch {
        parseWarnings.push(`Failed to parse CSV file '${file.name}'.`)
      }
      continue
    }

    if (ext === 'xlsx') {
      try {
        const buffer = await file.arrayBuffer()
        const workbook = XLSX.read(buffer, { type: 'array', raw: false })
        if (!workbook.SheetNames.length) {
          parseWarnings.push(`XLSX file '${file.name}' had no worksheets.`)
          continue
        }
        for (const sheetName of workbook.SheetNames) {
          const sheet = workbook.Sheets[sheetName]
          if (!sheet) {
            continue
          }
          tables.push(..._sheetToRows(sheet, `${file.name}:${sheetName}`))
        }
      } catch {
        parseWarnings.push(`Failed to parse XLSX file '${file.name}'.`)
      }
      continue
    }

    parseWarnings.push(`Unsupported file extension for '${file.name}'.`)
  }

  return {
    rawText: rawParts.join('\n\n'),
    tables,
    parseWarnings,
  }
}

function App() {
  const [wizardStep, setWizardStep] = useState<WizardStep>('home')
  const [selectedRole, setSelectedRole] = useState<string | null>(null)
  const [pipelineConfig, setPipelineConfig] = useState<PipelineConfigData | null>(null)
  const [runs, setRuns] = useState<RunEntry[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [fullState, setFullState] = useState<FullStateResponse | null>(null)
  const [stages, setStages] = useState<Stage[]>([])
  const [gates, setGates] = useState<Gate[]>([])
  const [metrics, setMetrics] = useState<LLMMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tabValue, setTabValue] = useState<TabValue>('gates')
  const [artifactTabIndex, setArtifactTabIndex] = useState(0)
  const [showAllRuns, setShowAllRuns] = useState(false)
  const [selectedRunIds, setSelectedRunIds] = useState<Set<string>>(new Set())
  const [selectedRunSetAt, setSelectedRunSetAt] = useState<number>(0)
  const [pendingWizardRunId, setPendingWizardRunId] = useState<string | null>(null)
  const [pendingWizardRunSetAt, setPendingWizardRunSetAt] = useState<number>(0)
  const [health, setHealth] = useState(false)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await apiClient.getHealth()
        setHealth(true)
      } catch {
        setHealth(false)
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadRuns = useCallback(async () => {
    try {
      const response = await apiClient.getRuns()
      setRuns(response.runs)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load runs')
    }
  }, [])

  useEffect(() => {
    loadRuns()
  }, [loadRuns])

  useEffect(() => {
    const pollRuns = setInterval(() => {
      loadRuns()
    }, 5000)
    return () => clearInterval(pollRuns)
  }, [loadRuns])

  useEffect(() => {
    if (!selectedRunId) {
      return
    }
    const selectedStillExists = runs.some((run) => run.run_id === selectedRunId)
    if (!selectedStillExists) {
      const withinSelectionGrace = Date.now() - selectedRunSetAt < 15000
      if (withinSelectionGrace) {
        return
      }
      setSelectedRunId(null)
      setWizardStep('home')
    }
  }, [runs, selectedRunId, selectedRunSetAt])

  useEffect(() => {
    if (wizardStep !== 'monitoring' || selectedRunId || runs.length === 0) {
      return
    }

    if (pendingWizardRunId) {
      const wizardRun = runs.find((run) => run.run_id === pendingWizardRunId)
      if (wizardRun) {
        setSelectedRunId(wizardRun.run_id)
        setSelectedRunSetAt(Date.now())
        return
      }

      // Do not auto-select a different run while the just-created run is still being indexed.
      if (Date.now() - pendingWizardRunSetAt < 30000) {
        return
      }

      setPendingWizardRunId(null)
      setPendingWizardRunSetAt(0)
    }

    const newestRun = [...runs].sort((a, b) => {
      const ta = a.start_time ? Date.parse(a.start_time) : 0
      const tb = b.start_time ? Date.parse(b.start_time) : 0
      return tb - ta
    })[0]
    if (newestRun?.run_id) {
      setSelectedRunId(newestRun.run_id)
      setSelectedRunSetAt(Date.now())
    }
  }, [wizardStep, selectedRunId, runs, pendingWizardRunId, pendingWizardRunSetAt])

  useEffect(() => {
    if (!pendingWizardRunId || pendingWizardRunSetAt <= 0) {
      return
    }

    const remainingMs = 30000 - (Date.now() - pendingWizardRunSetAt)
    if (remainingMs <= 0) {
      setPendingWizardRunId(null)
      setPendingWizardRunSetAt(0)
      return
    }

    const timer = setTimeout(() => {
      setPendingWizardRunId(null)
      setPendingWizardRunSetAt(0)
    }, remainingMs)

    return () => clearTimeout(timer)
  }, [pendingWizardRunId, pendingWizardRunSetAt])

  const loadRunState = useCallback(async (runId: string, options?: { silent?: boolean }) => {
    const silent = options?.silent ?? false
    if (!silent) {
      setLoading(true)
      setError(null)
    }
    try {
      const response = await apiClient.getFullState(runId)
      setFullState(response)
      setStages(response.stages)
      setGates(response.gates)
      setMetrics(response.metrics)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load run state'
      if (!msg.includes('No state available')) {
        setError(msg)
      }
      if (!silent) {
        setFullState(null)
        setStages([])
        setGates([])
        setMetrics(null)
      }
    } finally {
      if (!silent) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    if (selectedRunId) {
      loadRunState(selectedRunId)
    }
  }, [selectedRunId, loadRunState])

  useEffect(() => {
    if (!selectedRunId) {
      return
    }

    const selectedRun = runs.find((run) => run.run_id === selectedRunId)
    const selectedStatus = (selectedRun?.status ?? '').toLowerCase()
    const pausedByState = !!(fullState?.state.hitl_paused_at_gate ?? selectedRun?.pause_gate)
    const pausedByGates = gates.some((gate) => ['open', 'draft', 'paused'].includes(gate.status.toLowerCase()))
    const shouldPoll = selectedStatus === 'running' || pausedByState || pausedByGates

    if (shouldPoll) {
      const poll = setInterval(() => {
        loadRunState(selectedRunId, { silent: true })
      }, 5000)
      return () => clearInterval(poll)
    }
  }, [selectedRunId, runs, fullState, gates, loadRunState])

  const handleStartWizard = () => {
    setSelectedRole(null)
    setPipelineConfig(null)
    setPendingWizardRunId(null)
    setPendingWizardRunSetAt(0)
    setWizardStep('role-select')
  }

  const handleCancelWizard = () => {
    setWizardStep('home')
  }

  const handleBackToRoleSelect = () => {
    setWizardStep('role-select')
  }

  const handleBackToPipelineConfig = () => {
    setWizardStep('pipeline-config')
  }

  const handleRoleSelect = (role: string) => {
    setSelectedRole(role)
    setWizardStep('pipeline-config')
  }

  const handlePipelineConfirm = async (config: PipelineConfigData) => {
    try {
      setPipelineConfig(config)
      await apiClient.updateConfig(mapPipelineConfigToRuntimeSettings(config))
      setWizardStep('input-entry')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply pipeline configuration')
    }
  }

  const handleCreateRun = async (systemName: string, files: File[]) => {
    try {
      setWizardStep('creating-run')
      const newRunId = uuidv4()
      setPendingWizardRunId(newRunId)
      setPendingWizardRunSetAt(Date.now())
      const parsedInputs = await _parseInputFiles(files)
      const rawTextParts = [`# System: ${systemName}`, `# Role: ${selectedRole ?? 'Author'}`]
      if (parsedInputs.rawText.trim()) {
        rawTextParts.push(parsedInputs.rawText)
      }
      const rawText = rawTextParts.join('\n\n')

      await apiClient.createRun(newRunId, {
        runName: systemName,
        settings: pipelineConfig ? mapPipelineConfigToRuntimeSettings(pipelineConfig) : undefined,
        initialState: {
          raw_text: rawText,
          tables: parsedInputs.tables,
        },
      })

      if (parsedInputs.parseWarnings.length) {
        setError(`Input parse warnings: ${parsedInputs.parseWarnings.join(' ')}`)
      }

      setSelectedRunId(newRunId)
      setSelectedRunSetAt(Date.now())
      const response = await apiClient.getRuns()
      setRuns(response.runs)
      setTabValue('gates')
      setWizardStep('monitoring')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create run')
      setPendingWizardRunId(null)
      setPendingWizardRunSetAt(0)
      setWizardStep('input-entry')
    }
  }

  const handleGateDecision = async (gateId: string, action: string, rationale: string) => {
    if (!selectedRunId) return
    try {
      await apiClient.submitGateDecision(selectedRunId, gateId, { actor: 'web_ui', role: selectedRole ?? 'analyst', action, rationale })
      await loadRuns()
      await loadRunState(selectedRunId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit gate decision')
    }
  }

  const handleResumePipeline = async (gateId: string) => {
    if (!selectedRunId) return
    try {
      await apiClient.resumeRun(selectedRunId, gateId)
      await loadRuns()
      await loadRunState(selectedRunId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resume pipeline')
    }
  }

  const handleRenameRun = async () => {
    if (!selectedRunId) return
    const currentName = currentRun?.run_name || selectedRunId
    const nextName = window.prompt('Enter run name', currentName)
    if (!nextName || !nextName.trim()) return
    await apiClient.updateRunMetadata(selectedRunId, { run_name: nextName.trim() })
    const response = await apiClient.getRuns()
    setRuns(response.runs)
  }

  const handleArchiveToggle = async () => {
    if (!selectedRunId || !currentRun) return
    await apiClient.updateRunMetadata(selectedRunId, { archived: !currentRun.archived })
    const response = await apiClient.getRuns()
    setRuns(response.runs)
  }

  const handlePurgeSelected = async () => {
    if (!selectedRunIds.size) return
    await Promise.all(Array.from(selectedRunIds).map((runId) => apiClient.purgeRun(runId)))
    const response = await apiClient.getRuns()
    setRuns(response.runs)
    setSelectedRunIds(new Set())
    if (selectedRunId && selectedRunIds.has(selectedRunId)) {
      setSelectedRunId(null)
    }
    if (!response.runs.length) {
      setWizardStep('home')
    }
  }

  const handleArchiveSelected = async () => {
    if (!selectedRunIds.size) return
    await Promise.all(
      Array.from(selectedRunIds).map((runId) => apiClient.updateRunMetadata(runId, { archived: true })),
    )
    const response = await apiClient.getRuns()
    setRuns(response.runs)
    setSelectedRunIds(new Set())
  }

  const handleSelectVisibleRuns = (checked: boolean) => {
    if (checked) {
      setSelectedRunIds(new Set(visibleRuns.map((run) => run.run_id)))
    } else {
      setSelectedRunIds(new Set())
    }
  }

  const handleToggleRunSelection = (runId: string) => {
    setSelectedRunIds((prev) => {
      const next = new Set(prev)
      if (next.has(runId)) {
        next.delete(runId)
      } else {
        next.add(runId)
      }
      return next
    })
  }

  const currentRun = runs.find((r) => r.run_id === selectedRunId)
  const normalizedRunStatus = (currentRun?.status ?? '').toLowerCase()
  const pausedGateId = fullState?.state.hitl_paused_at_gate ?? currentRun?.pause_gate ?? null
  const hasOpenGate = gates.some((gate) => ['open', 'draft', 'paused'].includes(gate.status.toLowerCase()))
  const isPaused = !!pausedGateId || hasOpenGate
  const isRejected = !!fullState?.state.hitl_rejected_at_gate || normalizedRunStatus === 'rejected'
  const displayRunStatus = isRejected ? 'rejected' : isPaused ? 'paused' : currentRun?.status ?? 'unknown'
  const isRunActivelyExecuting = ['queued', 'running', 'paused'].includes(normalizedRunStatus) || isPaused
  const timelineCurrentStage = isRunActivelyExecuting ? fullState?.state.next_stage_id : null
  const currentStageLabel = stages.find((stage) => stage.stage_id === timelineCurrentStage)?.label ?? null
  const pausedGateName = gates.find((gate) => gate.gate_id === pausedGateId)?.gate_name ?? pausedGateId ?? null
  const timelineStatusText = isRejected
    ? `Rejected${pausedGateName ? ` at ${pausedGateName}` : ''}`
    : pausedGateName
      ? `Paused for ${pausedGateName}`
      : normalizedRunStatus === 'running' && currentStageLabel
        ? `Running ${currentStageLabel}`
        : normalizedRunStatus === 'queued'
          ? 'Queued for execution'
          : ['completed', 'complete', 'succeeded', 'success'].includes(normalizedRunStatus)
            ? 'Run completed'
            : currentStageLabel
              ? `Current stage ${currentStageLabel}`
              : `Status ${displayRunStatus}`
  const sortedRuns = [...runs].sort((a, b) => {
    const ta = a.start_time ? Date.parse(a.start_time) : 0
    const tb = b.start_time ? Date.parse(b.start_time) : 0
    return tb - ta
  })
  const visibleRuns = showAllRuns ? sortedRuns : sortedRuns.slice(0, 12)
  const artifactsAvailable = !!currentRun && ['complete', 'completed', 'success', 'succeeded'].includes(normalizedRunStatus)
  const gateApproved = !!currentRun && !pausedGateId && artifactsAvailable

  const navButtonTone = (view: TabValue) => {
    if (tabValue === view) {
      return '#ffffff'
    }
    if (view === 'artifacts' || view === 'last_prompt' || view === 'prompt_editor' || view === 'tokens') {
      if (gateApproved) {
        return '#40c4ff'
      }
      if (artifactsAvailable) {
        return '#66bb6a'
      }
    }
    return 'rgba(255,255,255,0.72)'
  }

  const navButtonSx = (view: TabValue) => ({
    justifyContent: 'flex-start',
    borderRadius: 1,
    color: navButtonTone(view),
    backgroundColor: tabValue === view ? 'rgba(62, 168, 255, 0.2)' : 'transparent',
    '&:hover': {
      backgroundColor: tabValue === view ? 'rgba(62, 168, 255, 0.28)' : 'rgba(255,255,255,0.06)',
    },
  })

  const artifactButtons = [
    { label: 'Canonical Graph', index: 0 },
    { label: 'Trust Boundaries', index: 1 },
    { label: 'STRIDE Viewer', index: 2 },
    { label: 'Threats', index: 3 },
    { label: 'Mermaid Diagrams', index: 4 },
    { label: 'STIX Bundle', index: 5 },
    { label: 'Report', index: 6 },
  ]

  const artifactButtonSx = (index: number) => ({
    justifyContent: 'flex-start',
    borderRadius: 1,
    color: tabValue === 'artifacts' && artifactTabIndex === index ? '#ffffff' : 'rgba(255,255,255,0.72)',
    backgroundColor: tabValue === 'artifacts' && artifactTabIndex === index ? 'rgba(62, 168, 255, 0.2)' : 'transparent',
    '&:hover': {
      backgroundColor: tabValue === 'artifacts' && artifactTabIndex === index ? 'rgba(62, 168, 255, 0.28)' : 'rgba(255,255,255,0.06)',
    },
  })

  const isWizardBadgeActive = (runId: string) =>
    pendingWizardRunId === runId && pendingWizardRunSetAt > 0 && Date.now() - pendingWizardRunSetAt < 30000

  return (
    <Box sx={{ display: 'flex', height: '100vh', backgroundColor: 'background.default' }}>
      <RoleSelect open={wizardStep === 'role-select'} onSelect={handleRoleSelect} onCancel={handleCancelWizard} />
      <PipelineConfig
        open={wizardStep === 'pipeline-config'}
        onConfirm={handlePipelineConfirm}
        onBack={handleBackToRoleSelect}
        onCancel={handleCancelWizard}
      />
      <InputEntry
        open={wizardStep === 'input-entry'}
        onStart={handleCreateRun}
        onBack={handleBackToPipelineConfig}
        onCancel={handleCancelWizard}
      />

      <Drawer variant="persistent" anchor="left" open sx={{ width: 320, flexShrink: 0, '& .MuiDrawer-paper': { width: 320, boxSizing: 'border-box', overflowY: 'auto' } }}>
        <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
          <Box sx={{ fontSize: 16, fontWeight: 700, mb: 1 }}>Threat Modeler</Box>
          <Box sx={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>Control Console v0.1</Box>
        </Box>

        <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
          <Box sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'primary.main', mb: 1, textTransform: 'uppercase' }}>Setup</Box>
          <Button fullWidth size="small" variant="outlined" onClick={handleStartWizard} sx={{ justifyContent: 'flex-start' }}>New Run Wizard</Button>
          <Button fullWidth size="small" variant="text" sx={{ justifyContent: 'flex-start', mt: 1, opacity: 0.85 }}>
            Role: {selectedRole ?? 'Not selected'}
          </Button>
          <Button fullWidth size="small" variant="text" sx={{ justifyContent: 'flex-start', mt: 1, opacity: 0.85 }}>
            Pipeline: {pipelineConfig?.provider ?? 'Default'}
          </Button>
        </Box>

        {selectedRunId && currentRun && (
          <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
            <Box sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'primary.main', mb: 1, textTransform: 'uppercase' }}>Active Run</Box>
            <Box sx={{ p: 1.5, backgroundColor: 'rgba(62, 168, 255, 0.1)', borderRadius: 1 }}>
              <Box sx={{ fontSize: '0.85rem', fontWeight: 600 }}>{currentRun.run_name}</Box>
              <Box sx={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.65)' }}>{selectedRunId.slice(0, 12)}</Box>
              <Box sx={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)', mt: 0.5 }}>Status: <strong>{displayRunStatus}</strong></Box>
              {isPaused && <Box sx={{ fontSize: '0.75rem', color: '#ffa726', mt: 0.5 }}>Paused</Box>}
              {isRejected && <Box sx={{ fontSize: '0.75rem', color: '#ff5252', mt: 0.5 }}>Rejected</Box>}
              {currentRun.archived && <Box sx={{ fontSize: '0.75rem', color: '#bdbdbd', mt: 0.5 }}>Archived</Box>}
            </Box>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Button size="small" variant="outlined" onClick={handleRenameRun}>Rename</Button>
              <Button size="small" variant="outlined" onClick={handleArchiveToggle}>{currentRun.archived ? 'Unarchive' : 'Archive'}</Button>
            </Box>
          </Box>
        )}

        {selectedRunId && (
          <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
            <Box sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'primary.main', mb: 1, textTransform: 'uppercase' }}>HITL GATES</Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Button fullWidth size="small" variant={tabValue === 'gates' ? 'contained' : 'text'} onClick={() => setTabValue('gates')} sx={navButtonSx('gates')}>HITL Gates ({gates.length})</Button>
            </Box>
          </Box>
        )}

        {selectedRunId && (
          <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
            <Box sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'primary.main', mb: 1, textTransform: 'uppercase' }}>Artifacts</Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              {artifactButtons.map((artifact) => (
                <Button
                  key={artifact.label}
                  fullWidth
                  size="small"
                  variant={tabValue === 'artifacts' && artifactTabIndex === artifact.index ? 'contained' : 'text'}
                  onClick={() => {
                    setTabValue('artifacts')
                    setArtifactTabIndex(artifact.index)
                  }}
                  sx={artifactButtonSx(artifact.index)}
                >
                  {artifact.label}
                </Button>
              ))}
            </Box>
          </Box>
        )}

        {selectedRunId && (
          <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
            <Box sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'primary.main', mb: 1, textTransform: 'uppercase' }}>Operator Views</Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Button fullWidth size="small" variant={tabValue === 'tokens' ? 'contained' : 'text'} onClick={() => setTabValue('tokens')} sx={navButtonSx('tokens')}>Tokens</Button>
              <Button fullWidth size="small" variant={tabValue === 'last_prompt' ? 'contained' : 'text'} onClick={() => setTabValue('last_prompt')} sx={navButtonSx('last_prompt')}>Last Prompt</Button>
              <Button fullWidth size="small" variant={tabValue === 'prompt_editor' ? 'contained' : 'text'} onClick={() => setTabValue('prompt_editor')} sx={navButtonSx('prompt_editor')}>Prompt Editor</Button>
            </Box>
          </Box>
        )}

        <Box sx={{ p: 2 }}>
          <Box sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'primary.main', mb: 1, textTransform: 'uppercase' }}>All Runs</Box>
          {runs.length > 12 && (
            <Button size="small" onClick={() => setShowAllRuns(!showAllRuns)} sx={{ mb: 1 }}>
              {showAllRuns ? 'Show Recent Only' : `Show All (${runs.length})`}
            </Button>
          )}
          <FormControlLabel
            control={
              <Checkbox
                size="small"
                checked={visibleRuns.length > 0 && visibleRuns.every((run) => selectedRunIds.has(run.run_id))}
                indeterminate={selectedRunIds.size > 0 && !visibleRuns.every((run) => selectedRunIds.has(run.run_id))}
                onChange={(e) => handleSelectVisibleRuns(e.target.checked)}
              />
            }
            label="Select All Visible"
            sx={{ mb: 0.5 }}
          />
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <Button size="small" variant="outlined" color="warning" onClick={handleArchiveSelected} disabled={!selectedRunIds.size}>Archive Selected</Button>
            <Button size="small" variant="outlined" color="error" onClick={handlePurgeSelected} disabled={!selectedRunIds.size}>Purge Selected</Button>
          </Box>
          <List sx={{ p: 0 }}>
            {visibleRuns.map((run) => (
              <ListItem key={run.run_id} disablePadding sx={{ mb: 0.5 }}>
                <Checkbox
                  checked={selectedRunIds.has(run.run_id)}
                  onChange={() => handleToggleRunSelection(run.run_id)}
                  onClick={(event) => event.stopPropagation()}
                  size="small"
                  sx={{ mr: 0.5 }}
                />
                <ListItemButton
                  selected={selectedRunId === run.run_id}
                  onClick={() => {
                    setSelectedRunId(run.run_id)
                    setSelectedRunSetAt(Date.now())
                    setPendingWizardRunId(null)
                    setPendingWizardRunSetAt(0)
                    setWizardStep('monitoring')
                  }}
                  sx={{ backgroundColor: selectedRunId === run.run_id ? 'rgba(62, 168, 255, 0.2)' : 'transparent', borderRadius: 1 }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                        <Box component="span" sx={{ fontSize: '0.85rem' }}>{run.run_name || `${run.run_id.slice(0, 10)}...`}</Box>
                        {isWizardBadgeActive(run.run_id) && (
                          <Chip label="Created by wizard" size="small" color="info" sx={{ height: 18, fontSize: '0.62rem' }} />
                        )}
                      </Box>
                    }
                    secondary={`${run.status}${run.archived ? ' · archived' : ''}`}
                    secondaryTypographyProps={{ fontSize: '0.7rem' }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static" sx={{ color: 'primary.main' }}>
          <Toolbar>
            <Box sx={{ flex: 1 }}>Threat Modeler Control Console</Box>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: health ? '#4caf50' : '#f44336', mr: 1 }} />
            <Box>{health ? 'Connected' : 'Disconnected'}</Box>
          </Toolbar>
          {selectedRunId && wizardStep !== 'creating-run' && (
            <Box sx={{ px: 2, pb: 1.5 }}>
              <Paper sx={{ mb: 1, px: 1, py: 0.5 }}>
                <Tabs
                  value={tabValue === 'artifacts' ? false : tabValue}
                  onChange={(_, next) => setTabValue(next as TabValue)}
                  variant="scrollable"
                  scrollButtons="auto"
                  allowScrollButtonsMobile
                >
                  <Tab label="HITL GATES" value="gates" />
                  <Tab label="TOKENS" value="tokens" />
                  <Tab label="Last Prompt" value="last_prompt" />
                  <Tab label="Prompt Editor" value="prompt_editor" />
                </Tabs>
              </Paper>
              <Paper sx={{ px: 1, py: 0.5 }}>
                <Tabs
                  value={artifactTabIndex}
                  onChange={(_, next) => {
                    setArtifactTabIndex(next as number)
                    setTabValue('artifacts')
                  }}
                  variant="scrollable"
                  scrollButtons="auto"
                  allowScrollButtonsMobile
                >
                  <Tab label="Canonical Graph" value={0} />
                  <Tab label="Trust Boundaries" value={1} />
                  <Tab label="STRIDE Viewer" value={2} />
                  <Tab label="Threats" value={3} />
                  <Tab label="Mermaid Diagrams" value={4} />
                  <Tab label="STIX Bundle" value={5} />
                  <Tab label="Report" value={6} />
                </Tabs>
              </Paper>
            </Box>
          )}
        </AppBar>

        <Box sx={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
          <Container maxWidth="lg" sx={{ py: 3, flex: 1 }}>
            {error && <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>{error}</Alert>}

            {wizardStep === 'home' && !selectedRunId && (
              <Paper sx={{ p: 3, mb: 2 }}>
                <Typography variant="h5" sx={{ mb: 1 }}>Home</Typography>
                <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                  Start with role selection, pipeline configuration, system name and architecture inputs, then monitor run state from backend projections.
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button variant="contained" onClick={handleStartWizard}>Start Setup Wizard</Button>
                  <Button variant="outlined" onClick={() => setWizardStep('monitoring')}>Open Monitoring</Button>
                </Box>
              </Paper>
            )}

            {wizardStep === 'creating-run' && (
              <Paper sx={{ p: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
                <CircularProgress size={24} />
                <Typography variant="body1">Creating run and sending setup inputs to backend...</Typography>
              </Paper>
            )}

            {!selectedRunId && wizardStep !== 'home' && wizardStep !== 'creating-run' && (
              <Alert severity="info">Select or create a run to begin</Alert>
            )}

            {selectedRunId && wizardStep !== 'creating-run' && (
              <>
                {currentRun && <Alert severity={isPaused ? 'warning' : isRejected ? 'error' : 'info'} sx={{ mb: 2 }}>Status: <strong>{displayRunStatus}</strong></Alert>}
                {!loading && !isPaused && isRunActivelyExecuting && currentRun?.settings != null && currentRun?.heartbeat_age_seconds != null && currentRun?.heartbeat_timeout_seconds != null && (
                  <Alert
                    severity={currentRun.heartbeat_age_seconds > currentRun.heartbeat_timeout_seconds ? 'error' : 'info'}
                    sx={{ mb: 2 }}
                  >
                    LLM Watchdog: heartbeat age {currentRun.heartbeat_age_seconds.toFixed(1)}s / timeout {currentRun.heartbeat_timeout_seconds.toFixed(1)}s
                  </Alert>
                )}
                {loading && <CircularProgress />}
                {!loading && tabValue === 'gates' && (
                  <HITLGateManager
                    gates={gates}
                    onGateDecision={handleGateDecision}
                    onResumePipeline={handleResumePipeline}
                    pausedGateId={pausedGateId}
                  />
                )}
                {!loading && tabValue === 'tokens' && metrics && <TokenUsageDashboard metrics={metrics} />}
                {!loading && tabValue === 'artifacts' && <ArtifactsViewer runId={selectedRunId} initialTab={artifactTabIndex} onTabChange={setArtifactTabIndex} />}
                {!loading && tabValue === 'last_prompt' && <LastPromptViewer runId={selectedRunId} />}
                {!loading && tabValue === 'prompt_editor' && <PromptEditor />}
              </>
            )}
          </Container>
        </Box>

        {selectedRunId && <Box sx={{ borderTop: '1px solid rgba(255,255,255,0.12)', backgroundColor: 'background.paper', p: 1.5 }}><ExecutionProgress stages={stages} currentStage={timelineCurrentStage} gates={gates} pausedGateId={pausedGateId} statusText={timelineStatusText} /></Box>}
      </Box>
    </Box>
  )
}

export default App
