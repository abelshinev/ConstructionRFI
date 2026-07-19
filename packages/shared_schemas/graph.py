from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime, UTC
from uuid import UUID, uuid4

from .ontology import NodeType, RelationshipType

# --- 1. Typed Properties ---
class BaseNodeProperties(BaseModel):
    """The base class for all node properties."""
    notes: Optional[str] = None

class WorkerProperties(BaseNodeProperties):
    helmet: Optional[bool] = None
    vest: Optional[bool] = None
    gloves: Optional[bool] = None
    role_title: Optional[str] = None

class EquipmentProperties(BaseNodeProperties):
    equipment_class: Optional[str] = None # e.g., "excavator", "crane"
    operational: Optional[bool] = None

class LocationProperties(BaseNodeProperties):
    zone_name: Optional[str] = None
    restricted: Optional[bool] = None

# A Union type so Pydantic knows how to parse any of these
NodeProperties = Union[WorkerProperties, EquipmentProperties, LocationProperties, BaseNodeProperties]


# --- 2. Provenance Tracking ---
class Provenance(BaseModel):
    source_asset_id: str
    observation_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


# --- 3. Canonical Graph Models ---
class GraphNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: NodeType
    properties: NodeProperties = Field(default_factory=BaseNodeProperties)
    provenance_history: List[Provenance] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class GraphEdge(BaseModel):
    source: UUID
    target: UUID
    relationship: RelationshipType
    provenance_history: List[Provenance] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class GraphMetadata(BaseModel):
    session_id: str
    version: int = 1
    total_nodes: int = 0
    total_edges: int = 0

class ContextGraph(BaseModel):
    metadata: GraphMetadata
    nodes: dict[UUID, GraphNode] = Field(default_factory=dict) # Using dict for O(1) lookups
    edges: List[GraphEdge] = Field(default_factory=list)