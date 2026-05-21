import React from 'react';
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Box, Chip } from '@mui/material';
import type { Threat, Mitigation } from '../types/api';

interface MitigationViewerProps {
  threats: Threat[];
}

export const MitigationViewer: React.FC<MitigationViewerProps> = ({ threats }) => {
  // Flatten all mitigations with threat context
  const mitigations: Array<{
    threatName: string;
    mitigation: Mitigation;
    type: 'Technical' | 'Administrative';
  }> = [];

  threats.forEach((threat) => {
    threat.technical_mitigations.forEach((m) => mitigations.push({ threatName: threat.name, mitigation: m, type: 'Technical' }));
    threat.administrative_mitigations.forEach((m) => mitigations.push({ threatName: threat.name, mitigation: m, type: 'Administrative' }));
  });

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Mitigation Viewer ({mitigations.length} mitigations)
      </Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Threat</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Residual Risk</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mitigations.map(({ threatName, mitigation, type }, idx) => (
              <TableRow key={type + mitigation.control_id + idx}>
                <TableCell>{threatName}</TableCell>
                <TableCell><Chip label={type} size="small" color={type === 'Technical' ? 'primary' : 'secondary'} /></TableCell>
                <TableCell>{mitigation.title}</TableCell>
                <TableCell>{mitigation.description}</TableCell>
                <TableCell>{mitigation.residual_risk}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {mitigations.length === 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">No mitigations found for current threats.</Typography>
        </Box>
      )}
    </Paper>
  );
};
