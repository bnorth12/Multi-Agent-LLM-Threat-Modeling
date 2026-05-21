import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  TextField,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
} from '@mui/material'
import FileUploadIcon from '@mui/icons-material/FileUpload'
import DeleteIcon from '@mui/icons-material/Delete'
import FolderIcon from '@mui/icons-material/Folder'

interface InputEntryProps {
  open: boolean
  onStart: (systemName: string, files: File[]) => void
  onBack: () => void
  onCancel: () => void
}

export function InputEntry({ open, onStart, onBack, onCancel }: InputEntryProps) {
  const [systemName, setSystemName] = React.useState('')
  const [files, setFiles] = React.useState<File[]>([])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)])
    }
  }

  const handleRemoveFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleStart = () => {
    if (!systemName.trim()) {
      alert('Please enter a system name')
      return
    }
    if (files.length === 0) {
      alert('Please upload at least one file')
      return
    }
    onStart(systemName, files)
  }

  const clearForm = () => {
    setSystemName('')
    setFiles([])
  }

  const handleCancel = () => {
    clearForm()
    onCancel()
  }

  return (
    <Dialog open={open} maxWidth="sm" fullWidth onClose={handleCancel}>
      <DialogTitle>Input Entry — Start a New Run</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="System Name"
            value={systemName}
            onChange={(e) => setSystemName(e.target.value)}
            fullWidth
            placeholder="e.g., MyApp-v2.1"
            helperText="Descriptive name for this threat modeling run"
          />

          <Box>
            <Button
              component="label"
              startIcon={<FileUploadIcon />}
              variant="outlined"
              fullWidth
            >
              Upload Architecture Files
              <input
                type="file"
                hidden
                multiple
                accept=".csv,.xlsx,.md,.txt,.yaml,.yml"
                onChange={handleFileInput}
              />
            </Button>
            <Box sx={{ fontSize: '0.75rem', color: 'text.secondary', mt: 0.5 }}>
              Supported: CSV, XLSX, Markdown, TXT, YAML
            </Box>
          </Box>

          {files.length > 0 && (
            <Box>
              <strong>Uploaded Files ({files.length})</strong>
              <List dense>
                {files.map((file, idx) => (
                  <ListItem
                    key={`${file.name}-${idx}`}
                    secondaryAction={
                      <IconButton edge="end" onClick={() => handleRemoveFile(idx)}>
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      <FolderIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={`${(file.size / 1024).toFixed(1)} KB`}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {files.length === 0 && (
            <Alert severity="info">
              Upload one or more architecture description files (CSV, Excel, Markdown, etc.) to begin threat modeling.
            </Alert>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancel}>Cancel</Button>
        <Button onClick={onBack}>Back</Button>
        <Button
          onClick={handleStart}
          variant="contained"
          disabled={!systemName.trim() || files.length === 0}
        >
          ▶ Start Threat Model Run
        </Button>
      </DialogActions>
    </Dialog>
  )
}
