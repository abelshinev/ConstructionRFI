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

## HOW TO REPRO 
Step 1: Docker for Postgres and redis
```bash
docker compose -f .\infra\compose\docker-compose.yml up -d postgres redis minio
```
Step 2: Get alembic up 
```bash
alembic upgrade head
```
> NOTE: DELETE existing versions if running into authentication error with postgres and execute this command before startup 
```bash
alembic revision --autogenerate -m "re init database"
```

Step 3: Run uvicorn FastAPI app
```bash
uvicorn apps.api.main:app --reload
```

Step 4: Run Celery for monitoring `process_status` updates
```bash
celery -A apps.worker.main.celery_app worker --loglevel=info -P threads
```

Very soon updating to run all services using docker compose.

### DEV NOTES

DECOUPLE CELERY FROM API: Create shared instance in packages/tasks. Needs Attention