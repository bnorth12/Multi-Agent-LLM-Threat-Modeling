import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  Divider,
} from '@mui/material'
import type { Threat } from '../types/api'

interface ThreatReviewProps {
  threats: Threat[]
  onThreatDecision?: (threatId: string, decision: string, notes: string) => Promise<void>
}

export const ThreatReview: React.FC<ThreatReviewProps> = ({ threats, onThreatDecision }) => {
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null)
  const [decisionNotes, setDecisionNotes] = useState('')
  const [loading, setLoading] = useState(false)

  React.useEffect(() => {
    if (!selectedThreat) {
      return
    }
    setDecisionNotes(selectedThreat.decision?.notes ?? '')
  }, [selectedThreat])

  const handleSubmitDecision = async (decision: string) => {
    if (!selectedThreat) return

    setLoading(true)
    try {
      if (onThreatDecision) {
        await onThreatDecision(selectedThreat.id, decision, decisionNotes)
      }
      setSelectedThreat(null)
      setDecisionNotes('')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (score: number): 'success' | 'warning' | 'error' => {
    if (score < 5) return 'success'
    if (score < 10) return 'warning'
    return 'error'
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Threat Review ({threats.length} threats)
      </Typography>

      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell sx={{ fontWeight: 600 }}>Threat</TableCell>
              <TableCell sx={{ fontWeight: 600, width: 100 }} align="center">
                Likelihood
              </TableCell>
              <TableCell sx={{ fontWeight: 600, width: 100 }} align="center">
                Impact
              </TableCell>
              <TableCell sx={{ fontWeight: 600, width: 80 }} align="center">
                Risk
              </TableCell>
              <TableCell sx={{ fontWeight: 600, width: 100 }} align="center">
                Mitigations
              </TableCell>
              <TableCell sx={{ fontWeight: 600, width: 80 }} align="center">
                Action
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {threats.map((threat) => (
              <TableRow key={threat.id} sx={{ '&:hover': { backgroundColor: '#f9f9f9' }, cursor: 'pointer' }} onClick={() => setSelectedThreat(threat)}>
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {threat.name}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                    {threat.interface_id}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip label={threat.likelihood} size="small" variant="outlined" />
                </TableCell>
                <TableCell align="center">
                  <Chip label={threat.impact} size="small" variant="outlined" />
                </TableCell>
                <TableCell align="center">
                  <Chip label={threat.risk_score} size="small" color={getRiskColor(threat.risk_score)} />
                </TableCell>
                <TableCell align="center">
                  <Typography variant="body2">{threat.technical_mitigations.length + threat.administrative_mitigations.length}</Typography>
                </TableCell>
                <TableCell align="center">
                  <Button size="small" variant="outlined" onClick={(e) => {
                    e.stopPropagation()
                    setSelectedThreat(threat)
                  }}>
                    Review
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={selectedThreat !== null} onClose={() => setSelectedThreat(null)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedThreat?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                Description
              </Typography>
              <Typography variant="body2">{selectedThreat?.description}</Typography>
            </Box>

            <Divider />

            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  Likelihood
                </Typography>
                <Chip label={selectedThreat?.likelihood} />
              </Box>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  Impact
                </Typography>
                <Chip label={selectedThreat?.impact} />
              </Box>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  Risk Score
                </Typography>
                <Chip label={selectedThreat?.risk_score} color={getRiskColor(selectedThreat?.risk_score || 0)} />
              </Box>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  MITRE ATT&CK
                </Typography>
                <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap' }}>
                  {selectedThreat?.mitre_attack_techniques.map((t) => (
                    <Chip key={t} label={t} size="small" />
                  ))}
                </Stack>
              </Box>
            </Box>

            <Divider />

            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                Technical Mitigations ({selectedThreat?.technical_mitigations.length || 0})
              </Typography>
              <Stack spacing={1}>
                {selectedThreat?.technical_mitigations.map((m) => (
                  <Box key={m.control_id} sx={{ p: 1.5, backgroundColor: (theme) => theme.palette.mode === 'dark' ? '#23272b' : '#f9f9f9', borderRadius: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500, color: (theme) => theme.palette.mode === 'dark' ? theme.palette.text.primary : undefined }}>
                      {m.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: (theme) => theme.palette.mode === 'dark' ? theme.palette.text.secondary : 'text.secondary', display: 'block' }}>
                      {m.description}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                Administrative Mitigations ({selectedThreat?.administrative_mitigations.length || 0})
              </Typography>
              <Stack spacing={1}>
                {selectedThreat?.administrative_mitigations.map((m) => (
                  <Box key={m.control_id} sx={{ p: 1.5, backgroundColor: (theme) => theme.palette.mode === 'dark' ? '#23272b' : '#f9f9f9', borderRadius: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500, color: (theme) => theme.palette.mode === 'dark' ? theme.palette.text.primary : undefined }}>
                      {m.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: (theme) => theme.palette.mode === 'dark' ? theme.palette.text.secondary : 'text.secondary', display: 'block' }}>
                      {m.description}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Box>

            <TextField label="Review Notes" multiline rows={3} fullWidth placeholder="Add your review notes..." value={decisionNotes} onChange={(e) => setDecisionNotes(e.target.value)} />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedThreat(null)}>Cancel</Button>
          <Button color="warning" onClick={() => handleSubmitDecision('needs_work')} disabled={loading}>
            Needs Work
          </Button>
          <Button variant="contained" color="success" onClick={() => handleSubmitDecision('approve')} disabled={loading}>
            Approve
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  )
}
