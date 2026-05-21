import { createTheme } from '@mui/material/styles'

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3ea8ff',
      light: '#5eb4ff',
      dark: '#2b7fcc',
    },
    secondary: {
      main: '#7c3aed',
    },
    background: {
      default: '#0f1419',
      paper: '#1a1f2e',
    },
    error: {
      main: '#ff5252',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ffa726',
    },
    divider: 'rgba(255,255,255,0.12)',
  },
  typography: {
    fontFamily: "'Segoe UI', 'Inter', 'Noto Sans', Arial, sans-serif",
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#12171f',
          borderRight: '1px solid rgba(255,255,255,0.12)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1f2e',
          borderBottom: '1px solid rgba(255,255,255,0.12)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1f2e',
          backgroundImage: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1f2e',
        },
      },
    },
  },
})
