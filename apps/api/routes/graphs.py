from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from packages.shared_schemas.observation import Observation
from packages.shared_schemas.graph import ContextGraph
from services.context_engine.engine import ContextGraphEngine
from services.context_engine.repository import MemoryGraphRepository
from services.state.state_keeper import default_state_keeper
from apps.api.dependencies import get_db

# Group these under a specific prefix
router = APIRouter(prefix="/context", tags=["Context Graph"])

# Instantiate the singleton engine using our Memory repository for now.
# (Later, we'll swap this with PostgresGraphRepository and inject db dependency)
engine = ContextGraphEngine(
    repository=MemoryGraphRepository(),
    state_keeper=default_state_keeper,
)

class CreateSessionRequest(BaseModel):
    session_id: str

@router.post("/sessions", response_model=ContextGraph)
def create_session(request: CreateSessionRequest):
    """Initializes a new blank graph for a given session."""
    try:
        return engine.create_graph(request.session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}/graph", response_model=ContextGraph)
def get_graph(session_id: str):
    """Returns the current canonical state of the graph."""
    graph = engine.get_graph(session_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Session not found")
    return graph

@router.post("/observations", response_model=ContextGraph)
async def add_observation(observation: Observation, db: AsyncSession = Depends(get_db)):
    """
    Ingests a raw observation, resolves entities, updates state,
    and returns the newly updated graph.
    """
    try:
        return await engine.add_observation(observation.session_id, observation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))