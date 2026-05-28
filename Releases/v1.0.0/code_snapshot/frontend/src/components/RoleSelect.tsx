import React from 'react'
import { Box, Dialog, DialogTitle, DialogContent, DialogActions, Button, RadioGroup, FormControlLabel, Radio, Typography } from '@mui/material'

interface RoleSelectProps {
  open: boolean
  onSelect: (role: string) => void
  onCancel: () => void
}

const ROLES = ['Author', 'Reviewer', 'Approver']

const ROLE_DESCRIPTIONS: Record<string, string> = {
  Author: 'Create and submit architecture for analysis. Initiate pipeline runs.',
  Reviewer: 'Review outputs and HITL gates. Approve or reject decisions.',
  Approver: 'Final approval authority over threat model and release decisions.',
}

export function RoleSelect({ open, onSelect, onCancel }: RoleSelectProps) {
  const [selected, setSelected] = React.useState('Author')

  const handleConfirm = () => {
    onSelect(selected)
  }

  return (
    <Dialog open={open} maxWidth="sm" fullWidth>
      <DialogTitle>Select Your Role</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <RadioGroup
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            {ROLES.map((role) => (
              <Box key={role} sx={{ mb: 2 }}>
                <FormControlLabel
                  value={role}
                  control={<Radio />}
                  label={<strong>{role}</strong>}
                />
                <Typography variant="caption" sx={{ display: 'block', ml: 4, color: 'text.secondary' }}>
                  {ROLE_DESCRIPTIONS[role]}
                </Typography>
              </Box>
            ))}
          </RadioGroup>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button onClick={handleConfirm} variant="contained">
          Confirm Role
        </Button>
      </DialogActions>
    </Dialog>
  )
}
