import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Paper, Typography, Button, Stack, LinearProgress } from '@mui/material'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const onUpload = async () => {
    if (!file) return
    setIsLoading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await axios.post(`${API_BASE}/upload`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
      navigate(`/datasets/${res.data.dataset_id}`)
    } catch (err) {
      alert('Upload failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container sx={{ py: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h5">Upload Survey File</Typography>
          <input type="file" accept=".csv,.xlsx,.xls" onChange={e => setFile(e.target.files?.[0] ?? null)} />
          {isLoading && <LinearProgress />}
          <Button variant="contained" onClick={onUpload} disabled={!file || isLoading}>Upload</Button>
        </Stack>
      </Paper>
    </Container>
  )
}