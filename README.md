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

1. ~~FASTAPI BACKEND BUILD~~
2. ~~INGEST PIPELINE~~
2.a ~~Setup Postgres ~~
2.b ~~Celery Tasks ~~
2.c ~~Ensure docker runs all the tools~~
3. OCR MODEL DEVELOPMENT [ in progress ]
4. OCR MODEL HOSTING
5. OCR-BACKEND INTEGRATION
6. Vision Models Development

## HOW TO REPRO 

### Step 1: Docker for Postgres and redis
```bash
docker compose --env-file .env -f infra/compose/docker-compose.yml up --build -d
```

### Step 2: Get alembic up 
```bash
docker exec -it rfi_api alembic upgrade head
```

> NOTE: DELETE existing versions if running into authentication error with postgres and execute this command before startup 
```bash
alembic revision --autogenerate -m "re init database"
```

### DEV NOTES

DECOUPLE CELERY FROM API: Create shared instance in packages/tasks. Needs Attention