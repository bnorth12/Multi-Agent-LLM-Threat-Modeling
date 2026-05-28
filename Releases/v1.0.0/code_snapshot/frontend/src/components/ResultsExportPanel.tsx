import { useMemo, useState } from 'react'
import { Alert, Box, Button, Paper, Stack, Typography } from '@mui/material'
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import type { Threat } from '../types/api'
import { apiClient } from '../api/client'

interface ResultsExportPanelProps {
  runId: string
  threats: Threat[]
  artifactsEnabled: boolean
}

type ExportArtifact = 'canonical' | 'stix' | 'mermaid' | 'report'

function toSerializableText(content: unknown): string {
  if (typeof content === 'string') {
    return content
  }
  return JSON.stringify(content ?? {}, null, 2)
}

function downloadTextFile(filename: string, content: string, mimeType = 'text/plain;charset=utf-8') {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}

export function ResultsExportPanel({ runId, threats, artifactsEnabled }: ResultsExportPanelProps) {
  const [error, setError] = useState<string | null>(null)
  const [downloading, setDownloading] = useState<ExportArtifact | 'mitigations' | null>(null)

  const mitigationsSnapshot = useMemo(() => {
    const rows = threats.flatMap((threat) => {
      const technical = threat.technical_mitigations.map((mitigation) => ({
        threat_id: threat.id,
        threat_name: threat.name,
        mitigation_type: 'technical',
        ...mitigation,
      }))
      const administrative = threat.administrative_mitigations.map((mitigation) => ({
        threat_id: threat.id,
        threat_name: threat.name,
        mitigation_type: 'administrative',
        ...mitigation,
      }))
      return [...technical, ...administrative]
    })

    return {
      run_id: runId,
      generated_at: new Date().toISOString(),
      mitigation_count: rows.length,
      mitigations: rows,
    }
  }, [runId, threats])

  const handleArtifactExport = async (artifact: ExportArtifact) => {
    setError(null)
    setDownloading(artifact)
    try {
      const response = await apiClient.getArtifact(runId, artifact)
      const extension = artifact === 'report' ? 'md' : artifact === 'mermaid' ? 'md' : 'json'
      const mime = extension === 'json' ? 'application/json;charset=utf-8' : 'text/markdown;charset=utf-8'
      downloadTextFile(`${runId}_${artifact}.${extension}`, toSerializableText(response.content), mime)
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to export ${artifact}`)
    } finally {
      setDownloading(null)
    }
  }

  const handleMitigationsExport = () => {
    setError(null)
    setDownloading('mitigations')
    try {
      downloadTextFile(`${runId}_mitigations.json`, JSON.stringify(mitigationsSnapshot, null, 2), 'application/json;charset=utf-8')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export mitigations')
    } finally {
      setDownloading(null)
    }
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 1 }}>
        Results Export
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Download generated artifacts for this run. Mitigations export is available here through the header Results Export view.
      </Typography>

      {!artifactsEnabled && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Artifact export is enabled after run completion.
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25} sx={{ flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          startIcon={<DownloadOutlinedIcon />}
          onClick={() => handleArtifactExport('canonical')}
          disabled={!artifactsEnabled || downloading !== null}
        >
          Export Canonical JSON
        </Button>
        <Button
          variant="contained"
          startIcon={<DownloadOutlinedIcon />}
          onClick={() => handleArtifactExport('stix')}
          disabled={!artifactsEnabled || downloading !== null}
        >
          Export STIX 2.1
        </Button>
        <Button
          variant="contained"
          startIcon={<DownloadOutlinedIcon />}
          onClick={() => handleArtifactExport('mermaid')}
          disabled={!artifactsEnabled || downloading !== null}
        >
          Export Mermaid
        </Button>
        <Button
          variant="contained"
          startIcon={<DownloadOutlinedIcon />}
          onClick={() => handleArtifactExport('report')}
          disabled={!artifactsEnabled || downloading !== null}
        >
          Export Report
        </Button>
        <Button
          variant="outlined"
          startIcon={<DownloadOutlinedIcon />}
          onClick={handleMitigationsExport}
          disabled={downloading !== null}
        >
          Export Mitigations JSON
        </Button>
      </Stack>

      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Threat records loaded: {threats.length}
        </Typography>
      </Box>
    </Paper>
  )
}
