import React from 'react'
import { Paper, Box, Typography, Alert, CircularProgress } from '@mui/material'
import { apiClient } from '../api/client'
import type { PromptStateResponse } from '../types/api'

interface LastPromptViewerProps {
  runId: string
}

function stringifyPrompt(value: unknown): string {
  if (value == null) {
    return 'No prompt has been recorded for this run yet.'
  }
  if (typeof value === 'string') {
    return value
  }
  return JSON.stringify(value, null, 2)
}

export function LastPromptViewer({ runId }: LastPromptViewerProps) {
  const [data, setData] = React.useState<PromptStateResponse | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const loadPromptData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await apiClient.getPromptState(runId)
        setData(response)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load prompt data')
      } finally {
        setLoading(false)
      }
    }

    loadPromptData()
  }, [runId])

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Last Prompt
      </Typography>
      {loading && <CircularProgress size={24} />}
      {error && <Alert severity="error">{error}</Alert>}
      {!loading && !error && (
        <>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Latest Prompt Payload
            </Typography>
            <Box sx={{ p: 2, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 1, fontFamily: 'monospace', fontSize: '0.8rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {stringifyPrompt(data?.last_prompt ?? null)}
            </Box>
          </Box>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            Prompt history entries: {data?.prompt_history?.length ?? 0}
          </Typography>
        </>
      )}
    </Paper>
  )
}
