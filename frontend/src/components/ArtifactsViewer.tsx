import React from 'react'
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  ToggleButtonGroup,
  ToggleButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material'
import { apiClient } from '../api/client'
import mermaid from 'mermaid'

interface ArtifactsViewerProps {
  runId: string
}

interface TrustBoundaryRow {
  id: string
  name: string
  fromNode: string
  toNode: string
  boundaryName: string
  protocol: string
}

interface StrideRow {
  id: string
  name: string
  boundaryName: string
  stride: {
    S: number
    T: number
    R: number
    I: number
    D: number
    E: number
  }
}

interface MermaidDiagramOption {
  id: string
  title: string
  code: string
}

function extractTrustBoundaryRows(canonicalContent: any): TrustBoundaryRow[] {
  const interfaces = Array.isArray(canonicalContent?.interfaces) ? canonicalContent.interfaces : []
  return interfaces
    .filter((iface: any) => Boolean(iface?.trust_boundary_crossing))
    .map((iface: any, index: number) => ({
      id: String(iface?.id ?? `boundary-${index + 1}`),
      name: String(iface?.name ?? 'Unnamed Interface'),
      fromNode: String(iface?.from_node ?? 'Unknown'),
      toNode: String(iface?.to_node ?? 'Unknown'),
      boundaryName: String(iface?.trust_boundary_name ?? 'Unnamed Boundary'),
      protocol: String(iface?.protocol ?? 'Unknown'),
    }))
}

function toScore(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }
  if (typeof value === 'string') {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : 0
  }
  return 0
}

function extractStrideRows(canonicalContent: any): StrideRow[] {
  const interfaces = Array.isArray(canonicalContent?.interfaces) ? canonicalContent.interfaces : []
  return interfaces
    .filter((iface: any) => iface?.stride && typeof iface.stride === 'object')
    .map((iface: any, index: number) => ({
      id: String(iface?.id ?? `stride-${index + 1}`),
      name: String(iface?.name ?? 'Unnamed Interface'),
      boundaryName: String(iface?.trust_boundary_name ?? 'N/A'),
      stride: {
        S: toScore(iface?.stride?.S),
        T: toScore(iface?.stride?.T),
        R: toScore(iface?.stride?.R),
        I: toScore(iface?.stride?.I),
        D: toScore(iface?.stride?.D),
        E: toScore(iface?.stride?.E),
      },
    }))
}

function stripMermaidFence(text: string): string {
  const trimmed = text.trim()
  if (!trimmed.startsWith('```')) {
    return trimmed
  }
  return trimmed
    .replace(/^```mermaid\s*/i, '')
    .replace(/^```\s*/i, '')
    .replace(/```\s*$/, '')
    .trim()
}

function extractMermaidBlocks(text: string): string[] {
  const blocks: string[] = []
  const regex = /```mermaid\s*([\s\S]*?)```/gi
  let match = regex.exec(text)
  while (match) {
    if (match[1]?.trim()) {
      blocks.push(match[1].trim())
    }
    match = regex.exec(text)
  }
  return blocks
}

function extractMermaidDiagrams(content: unknown): MermaidDiagramOption[] {
  const build = (id: string, title: string, code: string): MermaidDiagramOption => ({
    id,
    title,
    code,
  })

  if (!content) {
    return []
  }

  const fromUnknownValue = (value: unknown, fallbackId: string, fallbackTitle: string): MermaidDiagramOption | null => {
    if (typeof value === 'string') {
      const stripped = stripMermaidFence(value)
      return stripped ? build(fallbackId, fallbackTitle, stripped) : null
    }
    if (value && typeof value === 'object') {
      const obj = value as Record<string, unknown>
      const title = typeof obj.title === 'string' && obj.title.trim() ? obj.title : fallbackTitle
      const rawCode =
        (typeof obj.code === 'string' && obj.code) ||
        (typeof obj.diagram === 'string' && obj.diagram) ||
        (typeof obj.mermaid === 'string' && obj.mermaid) ||
        (typeof obj.content === 'string' && obj.content)
      if (rawCode) {
        const stripped = stripMermaidFence(rawCode)
        return stripped ? build(fallbackId, title, stripped) : null
      }
    }
    return null
  }

  if (typeof content === 'string') {
    const blocks = extractMermaidBlocks(content)
    if (blocks.length > 0) {
      return blocks.map((block, index) => build(`block-${index + 1}`, `Diagram ${index + 1}`, block))
    }

    try {
      const parsed = JSON.parse(content)
      return extractMermaidDiagrams(parsed)
    } catch {
      const stripped = stripMermaidFence(content)
      return stripped ? [build('diagram-1', 'Diagram 1', stripped)] : []
    }
  }

  if (Array.isArray(content)) {
    return content
      .map((item, index) => fromUnknownValue(item, `diagram-${index + 1}`, `Diagram ${index + 1}`))
      .filter((item): item is MermaidDiagramOption => Boolean(item))
  }

  if (content && typeof content === 'object') {
    const obj = content as Record<string, unknown>

    if (Array.isArray(obj.diagrams)) {
      return obj.diagrams
        .map((item, index) => fromUnknownValue(item, `diagram-${index + 1}`, `Diagram ${index + 1}`))
        .filter((item): item is MermaidDiagramOption => Boolean(item))
    }

    if (obj.diagrams && typeof obj.diagrams === 'object') {
      const entries = Object.entries(obj.diagrams as Record<string, unknown>)
      return entries
        .map(([key, value], index) => fromUnknownValue(value, key || `diagram-${index + 1}`, key || `Diagram ${index + 1}`))
        .filter((item): item is MermaidDiagramOption => Boolean(item))
    }

    if (typeof obj.mermaid === 'string') {
      const stripped = stripMermaidFence(obj.mermaid)
      if (stripped) {
        return [build('diagram-1', 'Diagram 1', stripped)]
      }
    }

    const possible = Object.entries(obj)
      .map(([key, value], index) => fromUnknownValue(value, key || `diagram-${index + 1}`, key || `Diagram ${index + 1}`))
      .filter((item): item is MermaidDiagramOption => Boolean(item))
    if (possible.length > 0) {
      return possible
    }
  }

  return []
}

export function ArtifactsViewer({ runId }: ArtifactsViewerProps) {
  const [tabValue, setTabValue] = React.useState(0)
  const [artifacts, setArtifacts] = React.useState<Record<string, any>>({})
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [mermaidViewMode, setMermaidViewMode] = React.useState<'split' | 'diagram' | 'text'>('split')
  const [selectedDiagramId, setSelectedDiagramId] = React.useState<string>('')
  const [editableMermaidText, setEditableMermaidText] = React.useState<string>('')
  const [mermaidSvg, setMermaidSvg] = React.useState<string>('')
  const [mermaidRenderError, setMermaidRenderError] = React.useState<string | null>(null)

  const mermaidDiagrams = React.useMemo(
    () => extractMermaidDiagrams(artifacts.mermaid?.content),
    [artifacts.mermaid?.content],
  )

  const selectedDiagramMeta = React.useMemo(() => {
    if (mermaidDiagrams.length === 0) {
      return { index: 0, total: 0, title: '' }
    }
    const index = mermaidDiagrams.findIndex((diagram) => diagram.id === selectedDiagramId)
    const safeIndex = index >= 0 ? index : 0
    return {
      index: safeIndex + 1,
      total: mermaidDiagrams.length,
      title: mermaidDiagrams[safeIndex]?.title ?? '',
    }
  }, [mermaidDiagrams, selectedDiagramId])

  React.useEffect(() => {
    if (mermaidDiagrams.length === 0) {
      setSelectedDiagramId('')
      setEditableMermaidText('')
      return
    }

    const found = mermaidDiagrams.some((diagram) => diagram.id === selectedDiagramId)
    if (!found) {
      setSelectedDiagramId(mermaidDiagrams[0].id)
      setEditableMermaidText(mermaidDiagrams[0].code)
      return
    }

    const selected = mermaidDiagrams.find((diagram) => diagram.id === selectedDiagramId)
    if (selected) {
      setEditableMermaidText(selected.code)
    }
  }, [mermaidDiagrams, selectedDiagramId])

  React.useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose',
      theme: 'default',
    })
  }, [])

  React.useEffect(() => {
    const renderMermaid = async () => {
      if (!editableMermaidText.trim()) {
        setMermaidSvg('')
        setMermaidRenderError(null)
        return
      }

      try {
        const renderId = `mermaid-artifact-${Date.now()}`
        const { svg } = await mermaid.render(renderId, editableMermaidText)
        setMermaidSvg(svg)
        setMermaidRenderError(null)
      } catch (err) {
        setMermaidSvg('')
        setMermaidRenderError(err instanceof Error ? err.message : 'Failed to render Mermaid diagram')
      }
    }

    renderMermaid()
  }, [editableMermaidText])

  React.useEffect(() => {
    const loadArtifacts = async () => {
      setLoading(true)
      setError(null)
      try {
        const [canonical, mermaid, stix, report] = await Promise.all([
          apiClient.getArtifact(runId, 'canonical'),
          apiClient.getArtifact(runId, 'mermaid'),
          apiClient.getArtifact(runId, 'stix'),
          apiClient.getArtifact(runId, 'report'),
        ])

        setArtifacts({ canonical, mermaid, stix, report })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load artifacts')
      } finally {
        setLoading(false)
      }
    }
    loadArtifacts()
  }, [runId])

  return (
    <Box>
      <Tabs value={tabValue} onChange={(_, val) => setTabValue(val)} sx={{ mb: 2 }}>
        <Tab label="📊 Canonical Graph" />
        <Tab label="🛡️ Trust Boundaries" />
        <Tab label="🎯 STRIDE Viewer" />
        <Tab label="🎨 Mermaid Diagrams" />
        <Tab label="📋 STIX Bundle" />
        <Tab label="📄 Report" />
      </Tabs>

      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}

      {!loading && tabValue === 0 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ fontWeight: 600, mb: 2 }}>Canonical Graph (JSON)</Box>
          <Box sx={{ fontFamily: 'monospace', fontSize: '0.85rem', overflow: 'auto', maxHeight: '400px' }}>
            <pre>{JSON.stringify(artifacts.canonical?.content, null, 2)}</pre>
          </Box>
        </Paper>
      )}

      {!loading && tabValue === 1 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ fontWeight: 600, mb: 2 }}>Trust Boundary Crossings</Box>
          {(() => {
            const rows = extractTrustBoundaryRows(artifacts.canonical?.content)
            if (rows.length === 0) {
              return <Alert severity="info">No trust boundary crossings identified yet</Alert>
            }

            return (
              <Box sx={{ display: 'grid', gap: 1.25 }}>
                {rows.map((row) => (
                  <Paper
                    key={row.id}
                    variant="outlined"
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                    }}
                  >
                    <Box sx={{ fontWeight: 700 }}>{row.name}</Box>
                    <Box sx={{ fontSize: '0.9rem', opacity: 0.9 }}>Boundary: {row.boundaryName}</Box>
                    <Box sx={{ fontSize: '0.9rem', opacity: 0.9 }}>Path: {row.fromNode}{' -> '}{row.toNode}</Box>
                    <Box sx={{ fontSize: '0.85rem', opacity: 0.8 }}>Protocol: {row.protocol}</Box>
                  </Paper>
                ))}
              </Box>
            )
          })()}
        </Paper>
      )}

      {!loading && tabValue === 2 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ fontWeight: 600, mb: 2 }}>STRIDE Scores by Interface</Box>
          {(() => {
            const rows = extractStrideRows(artifacts.canonical?.content)
            if (rows.length === 0) {
              return <Alert severity="info">No STRIDE scores available yet</Alert>
            }

            return (
              <Box sx={{ display: 'grid', gap: 1.25 }}>
                {rows.map((row) => (
                  <Paper key={row.id} variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                    <Box sx={{ fontWeight: 700 }}>{row.name}</Box>
                    <Box sx={{ fontSize: '0.85rem', opacity: 0.8, mb: 0.5 }}>Boundary: {row.boundaryName}</Box>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(6, minmax(48px, 1fr))', gap: 0.75 }}>
                      <Box sx={{ fontSize: '0.85rem' }}>S: {row.stride.S}</Box>
                      <Box sx={{ fontSize: '0.85rem' }}>T: {row.stride.T}</Box>
                      <Box sx={{ fontSize: '0.85rem' }}>R: {row.stride.R}</Box>
                      <Box sx={{ fontSize: '0.85rem' }}>I: {row.stride.I}</Box>
                      <Box sx={{ fontSize: '0.85rem' }}>D: {row.stride.D}</Box>
                      <Box sx={{ fontSize: '0.85rem' }}>E: {row.stride.E}</Box>
                    </Box>
                  </Paper>
                ))}
              </Box>
            )
          })()}
        </Paper>
      )}

      {!loading && tabValue === 3 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexWrap: 'wrap', gap: 1 }}>
            <Box sx={{ fontWeight: 600 }}>Mermaid Diagrams</Box>
            <ToggleButtonGroup
              size="small"
              exclusive
              value={mermaidViewMode}
              onChange={(_, next) => {
                if (next) {
                  setMermaidViewMode(next)
                }
              }}
            >
              <ToggleButton value="split">Split</ToggleButton>
              <ToggleButton value="diagram">Diagram</ToggleButton>
              <ToggleButton value="text">Text</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {mermaidDiagrams.length === 0 ? (
            <Alert severity="info">No diagrams generated yet</Alert>
          ) : (
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns:
                  mermaidViewMode === 'split' ? { xs: '1fr', md: '1fr 1fr' } : '1fr',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
                <FormControl size="small" sx={{ minWidth: 260, maxWidth: 420 }}>
                  <InputLabel id="mermaid-diagram-selector-label">Diagram</InputLabel>
                  <Select
                    labelId="mermaid-diagram-selector-label"
                    label="Diagram"
                    value={selectedDiagramId}
                    onChange={(event) => {
                      const nextId = String(event.target.value)
                      setSelectedDiagramId(nextId)
                      const next = mermaidDiagrams.find((diagram) => diagram.id === nextId)
                      setEditableMermaidText(next?.code ?? '')
                    }}
                  >
                    {mermaidDiagrams.map((diagram) => (
                      <MenuItem key={diagram.id} value={diagram.id}>
                        {diagram.title}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                  {selectedDiagramMeta.index} of {selectedDiagramMeta.total}
                  {selectedDiagramMeta.title ? ` - ${selectedDiagramMeta.title}` : ''}
                </Typography>
              </Box>

              {(mermaidViewMode === 'split' || mermaidViewMode === 'text') && (
                <Paper variant="outlined" sx={{ p: 2, minHeight: 260 }}>
                  <Box sx={{ fontWeight: 600, mb: 1 }}>Mermaid Text (Editable)</Box>
                  <TextField
                    fullWidth
                    multiline
                    minRows={14}
                    maxRows={24}
                    value={editableMermaidText}
                    onChange={(event) => setEditableMermaidText(event.target.value)}
                    sx={{
                      '& .MuiInputBase-input': {
                        fontFamily: 'monospace',
                        fontSize: '0.85rem',
                      },
                    }}
                  />
                </Paper>
              )}

              {(mermaidViewMode === 'split' || mermaidViewMode === 'diagram') && (
                <Paper variant="outlined" sx={{ p: 2, minHeight: 260 }}>
                  <Box sx={{ fontWeight: 600, mb: 1 }}>Diagram Preview</Box>
                  {mermaidRenderError ? (
                    <Alert severity="warning">Unable to render Mermaid preview: {mermaidRenderError}</Alert>
                  ) : (
                    <Box
                      sx={{ overflow: 'auto', maxHeight: 460, '& svg': { maxWidth: '100%', height: 'auto' } }}
                      dangerouslySetInnerHTML={{ __html: mermaidSvg }}
                    />
                  )}
                </Paper>
              )}
            </Box>
          )}
        </Paper>
      )}

      {!loading && tabValue === 4 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ fontWeight: 600, mb: 2 }}>STIX 2.1 Bundle (JSON)</Box>
          <Box sx={{ fontFamily: 'monospace', fontSize: '0.85rem', overflow: 'auto', maxHeight: '400px' }}>
            <pre>{JSON.stringify(artifacts.stix?.content, null, 2)}</pre>
          </Box>
        </Paper>
      )}

      {!loading && tabValue === 5 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ fontWeight: 600, mb: 2 }}>Final Report</Box>
          {artifacts.report?.content ? (
            <Box sx={{ fontSize: '0.95rem', lineHeight: 1.6, maxHeight: '400px', overflow: 'auto' }}>
              {artifacts.report.content}
            </Box>
          ) : (
            <Alert severity="info">Report not yet available</Alert>
          )}
        </Paper>
      )}
    </Box>
  )
}
