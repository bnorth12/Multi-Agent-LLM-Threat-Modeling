import React from 'react'
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, LinearProgress, Stack } from '@mui/material'
import type { LLMMetrics } from '../types/api'

interface TokenUsageDashboardProps {
  metrics: LLMMetrics
}

export const TokenUsageDashboard: React.FC<TokenUsageDashboardProps> = ({ metrics }) => {
  const getUsagePercent = (current: number, total: number) => {
    return total > 0 ? (current / total) * 100 : 0
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 3 }}>
        LLM Token Usage
      </Typography>

      <Box sx={{ mb: 4, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2 }}>
        <Box sx={{ p: 2, backgroundColor: '#f0f5ff', borderRadius: 1 }}>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            Total Tokens
          </Typography>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {metrics.total_tokens.toLocaleString()}
          </Typography>
        </Box>
        <Box sx={{ p: 2, backgroundColor: '#f0fff0', borderRadius: 1 }}>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            Total Requests
          </Typography>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {metrics.request_count}
          </Typography>
        </Box>
        <Box sx={{ p: 2, backgroundColor: '#fff0f0', borderRadius: 1 }}>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            Cached Tokens
          </Typography>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {metrics.cached_tokens.toLocaleString()}
          </Typography>
        </Box>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Token Breakdown
        </Typography>
        <Stack spacing={1.5}>
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption">Prompt Tokens</Typography>
              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                {metrics.prompt_tokens.toLocaleString()} ({getUsagePercent(metrics.prompt_tokens, metrics.total_tokens).toFixed(1)}%)
              </Typography>
            </Box>
            <LinearProgress variant="determinate" value={getUsagePercent(metrics.prompt_tokens, metrics.total_tokens)} sx={{ height: 6, borderRadius: 3 }} />
          </Box>
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption">Completion Tokens</Typography>
              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                {metrics.completion_tokens.toLocaleString()} ({getUsagePercent(metrics.completion_tokens, metrics.total_tokens).toFixed(1)}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getUsagePercent(metrics.completion_tokens, metrics.total_tokens)}
              sx={{ height: 6, borderRadius: 3, backgroundColor: '#f0f0f0', '& .MuiLinearProgress-bar': { backgroundColor: '#4caf50' } }}
            />
          </Box>
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption">Reasoning Tokens</Typography>
              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                {metrics.reasoning_tokens.toLocaleString()} ({getUsagePercent(metrics.reasoning_tokens, metrics.total_tokens).toFixed(1)}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getUsagePercent(metrics.reasoning_tokens, metrics.total_tokens)}
              sx={{ height: 6, borderRadius: 3, backgroundColor: '#f0f0f0', '& .MuiLinearProgress-bar': { backgroundColor: '#ff9800' } }}
            />
          </Box>
        </Stack>
      </Box>

      <Box>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Usage by Stage
        </Typography>
        <TableContainer sx={{ maxHeight: 400 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 600 }}>Stage</TableCell>
                <TableCell sx={{ fontWeight: 600 }} align="right">
                  Requests
                </TableCell>
                <TableCell sx={{ fontWeight: 600 }} align="right">
                  Tokens
                </TableCell>
                <TableCell sx={{ fontWeight: 600 }} align="right">
                  Prompt
                </TableCell>
                <TableCell sx={{ fontWeight: 600 }} align="right">
                  Completion
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(metrics.by_stage).map(([stageId, data]) => (
                <TableRow key={stageId}>
                  <TableCell>{stageId}</TableCell>
                  <TableCell align="right">{data.request_count}</TableCell>
                  <TableCell align="right">{data.total_tokens.toLocaleString()}</TableCell>
                  <TableCell align="right">{data.prompt_tokens.toLocaleString()}</TableCell>
                  <TableCell align="right">{data.completion_tokens.toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Paper>
  )
}
