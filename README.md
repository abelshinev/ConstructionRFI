# **CONSTRUCTION RFI COPILOT**


### _bismillah alrahaman alraheem_

## CURRENT OVERVIEW


```
construction-copilot/
│
├── apps/ ...
│   ├── api/     ✓          # FastAPI gateway
│   ├── frontend/...        # Next.js frontend
│   └── worker/  ✓          # Celery/RQ workers
│
├── services/
│   ├── vision/
│   ├── ocr/  ... <--- in queue
│   ├── speech/
│   ├── retrieval/
│   ├── agent/
│   └── ingestion/
│
├── packages/
│   ├── shared-schemas/
│   ├── shared-utils/
│   └── config/
│
├── logs/
│   └── app.log
│
├── infra/ ✓
│   ├── docker/ ✓
│   ├── compose/ ✓
│   ├── k8s/ (later)
│   └── terraform/ (MUCH later)
│
├── scripts/
│
├── docs/
│
├── storage/
│   ├── database/ (!) <-- IN TESTING
│   ├── raw/
│   └── temp/
│
└── README.md
```

## TO DO LIST [ ABSTRACT ]

1. FASTAPI BACKEND BUILD
2. INGEST PIPELINE
2.a Setup Postgres 
2.b Celery Tasks 
3. OCR MODEL DEVELOPMENT [ in progress ]
4. OCR MODEL HOSTING
5. OCR-BACKEND INTEGRATION

### DEV NOTES

DECOUPLE CELERY FROM API: Create shared instance in packages/tasks. Needs Attention