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
│   ├── ocr/  ✓
│   ├── speech/ ✓
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

### Context Graph Detail

The Context Graph is the project's canonical world model for a single investigation session. It aggregates multimodal observations into a structured representation of the construction environment. Rather than reasoning itself, it provides the Situation Agent with a complete, session-scoped understanding of the investigation. The Situation Agent enriches this understanding with retrieved regulations, project specifications, and historical context to produce actionable recommendations, warnings, and human-readable outputs such as RFIs, compliance reports, and safety summaries.