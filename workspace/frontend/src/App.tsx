import { AppBar, Toolbar, Typography, Container, Button, Stack } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

function App() {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>AI Survey Prep</Typography>
          <Button color="inherit" component={RouterLink} to="/upload">Upload</Button>
          <Button color="inherit" href="/">Home</Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ py: 4 }}>
        <Stack spacing={2}>
          <Typography variant="h4">Welcome</Typography>
          <Typography>Use the Upload page to ingest CSV/Excel, configure cleaning, apply weights, analyze, and generate reports.</Typography>
          <Button variant="contained" size="large" component={RouterLink} to="/upload">Get Started</Button>
        </Stack>
      </Container>
    </>
  )
}

export default App
