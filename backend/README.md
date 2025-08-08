# Backend - Survey Data Processing API

Run locally:

```
python3 -m pip install --break-system-packages -r backend/requirements.txt
python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- POST `/upload` (multipart file)
- GET `/datasets/{id}/preview`
- POST `/datasets/{id}/config`
- POST `/datasets/{id}/clean`
- POST `/datasets/{id}/analyze`
- GET `/datasets/{id}/report`