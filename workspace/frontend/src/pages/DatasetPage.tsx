import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Container, Paper, Typography, Stack, Button, TextField, Grid, Divider, Table, TableHead, TableRow, TableCell, TableBody, Select, MenuItem, Chip } from '@mui/material'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

type Preview = { rows: any[]; columns: string[]; row_count: number; column_count: number }

export default function DatasetPage() {
  const { id } = useParams()
  const [preview, setPreview] = useState<Preview | null>(null)
  const [columns, setColumns] = useState<string[]>([])
  const [imputationMethod, setImputationMethod] = useState('median')
  const [outlierMethod, setOutlierMethod] = useState('iqr')
  const [weightColumn, setWeightColumn] = useState<string>('')

  useEffect(() => {
    const fetchPreview = async () => {
      const res = await axios.get(`${API_BASE}/datasets/${id}/preview`)
      setPreview(res.data.preview)
      setColumns(res.data.preview.columns)
    }
    fetchPreview()
  }, [id])

  const runClean = async () => {
    await axios.post(`${API_BASE}/datasets/${id}/clean`, {
      imputation_method: imputationMethod,
      outlier_method: outlierMethod,
    })
    const res = await axios.get(`${API_BASE}/datasets/${id}/preview`)
    setPreview(res.data.preview)
  }

  const runAnalyze = async () => {
    const res = await axios.post(`${API_BASE}/datasets/${id}/analyze`, {
      weight_column: weightColumn || null,
    })
    alert('Analysis complete. Check console for details.')
    console.log(res.data)
  }

  const reportUrl = useMemo(() => `${API_BASE}/datasets/${id}/report`, [id])

  return (
    <Container sx={{ py: 4 }}>
      <Stack spacing={3}>
        <Typography variant="h5">Dataset {id}</Typography>

        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Configuration</Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <TextField select fullWidth label="Imputation" value={imputationMethod} onChange={e => setImputationMethod(e.target.value)}>
                <MenuItem value="mean">Mean</MenuItem>
                <MenuItem value="median">Median</MenuItem>
                <MenuItem value="knn">KNN (fallback to median)</MenuItem>
                <MenuItem value="none">None</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField select fullWidth label="Outliers" value={outlierMethod} onChange={e => setOutlierMethod(e.target.value)}>
                <MenuItem value="iqr">IQR Winsorize</MenuItem>
                <MenuItem value="zscore">Z-score Winsorize</MenuItem>
                <MenuItem value="none">None</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField select fullWidth label="Weight column" value={weightColumn} onChange={e => setWeightColumn(e.target.value)}>
                <MenuItem value="">None</MenuItem>
                {columns.map(c => (<MenuItem key={c} value={c}>{c}</MenuItem>))}
              </TextField>
            </Grid>
          </Grid>
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            <Button variant="contained" onClick={runClean}>Run Cleaning</Button>
            <Button variant="outlined" onClick={runAnalyze}>Analyze</Button>
            <Button variant="text" href={reportUrl} target="_blank">Open Report</Button>
          </Stack>
        </Paper>

        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Preview ({preview?.row_count ?? 0} rows)</Typography>
          <Divider sx={{ my: 1 }} />
          <div style={{ overflow: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {preview?.columns.map(c => <TableCell key={c}>{c}</TableCell>)}
                </TableRow>
              </TableHead>
              <TableBody>
                {preview?.rows.map((r, idx) => (
                  <TableRow key={idx}>
                    {preview.columns.map(c => <TableCell key={c}>{String(r[c])}</TableCell>)}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Paper>
      </Stack>
    </Container>
  )
}