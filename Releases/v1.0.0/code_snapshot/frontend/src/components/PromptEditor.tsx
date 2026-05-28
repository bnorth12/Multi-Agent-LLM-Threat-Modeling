import React from 'react'
import { Paper, Box, Typography, FormControl, InputLabel, Select, MenuItem, TextField, Button, Alert } from '@mui/material'
import { apiClient } from '../api/client'

export function PromptEditor() {
  const [agentIds, setAgentIds] = React.useState<string[]>([])
  const [agentId, setAgentId] = React.useState('')
  const [promptStorePath, setPromptStorePath] = React.useState('')
  const [prompt, setPrompt] = React.useState('')
  const [expectedOutput, setExpectedOutput] = React.useState('')
  const [temperature, setTemperature] = React.useState(0)
  const [message, setMessage] = React.useState<string | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const loadPrompts = async () => {
      try {
        const response = await apiClient.getPrompts()
        const ids = Object.keys(response.prompts)
        setAgentIds(ids)
        setPromptStorePath(response.prompt_store_path ?? '')
        if (ids.length > 0) {
          setAgentId(ids[0])
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load prompts')
      }
    }
    loadPrompts()
  }, [])

  React.useEffect(() => {
    const loadPromptDetail = async () => {
      if (!agentId) return
      try {
        const response = await apiClient.getPrompt(agentId)
        setPrompt(response.prompt)
        setExpectedOutput(response.expected_output)
        setTemperature(response.temperature)
        setPromptStorePath(response.prompt_store_path ?? '')
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load prompt detail')
      }
    }
    loadPromptDetail()
  }, [agentId])

  const handleSave = async () => {
    if (!agentId) return
    setMessage(null)
    setError(null)
    try {
      await apiClient.updatePrompt(agentId, {
        prompt,
        expected_output: expectedOutput,
        temperature,
      })
      setMessage(`Saved prompt updates for ${agentId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save prompt')
    }
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Agent Prompt Editor
      </Typography>
      {promptStorePath && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Prompt Source: {promptStorePath}
        </Typography>
      )}
      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <FormControl fullWidth>
          <InputLabel>Agent</InputLabel>
          <Select value={agentId} label="Agent" onChange={(e) => setAgentId(e.target.value)}>
            {agentIds.map((id) => (
              <MenuItem key={id} value={id}>{id}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          label="System Prompt"
          multiline
          minRows={8}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />

        <TextField
          label="Expected Output"
          multiline
          minRows={4}
          value={expectedOutput}
          onChange={(e) => setExpectedOutput(e.target.value)}
        />

        <TextField
          label="Temperature"
          type="number"
          value={temperature}
          onChange={(e) => setTemperature(Number(e.target.value))}
          inputProps={{ step: 0.1, min: 0, max: 2 }}
        />

        <Button variant="contained" onClick={handleSave}>Save Prompt</Button>
      </Box>
    </Paper>
  )
}
