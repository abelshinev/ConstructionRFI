from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, UTC
from uuid import UUID, uuid4

from .ontology import NodeType, RelationshipType, ObservationType, SourceType
from .graph import NodeProperties, BaseNodeProperties

# --- Transient Observation Models ---

class ObservationNode(BaseModel):
    """
    A transient entity detected in a single observation.
    Uses a 'local_id' because it has not yet been resolved against the canonical graph.
    """
    local_id: str = Field(description="Temporary ID unique to this observation payload")
    type: NodeType
    properties: NodeProperties = Field(default_factory=BaseNodeProperties)
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Optional raw spatial data. The Entity Resolver can use this to determine 
    # if this node is the same as an existing node in the graph.
    bbox: Optional[List[float]] = None 

class ObservationEdge(BaseModel):
    """
    A transient relationship detected in a single observation.
    Connects two local_ids.
    """
    source_local_id: str
    target_local_id: str
    relationship: RelationshipType
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Optional raw fact from vision. Again, pure facts, not policy.
    distance_pixels: Optional[float] = None 

class Observation(BaseModel):
    """
    The universal abstraction for all perception outputs.
    Whether from Vision, OCR, or Speech, it must be mapped to this schema.
    """
    observation_id: UUID = Field(default_factory=uuid4)
    session_id: str
    
    # Provenance data
    observation_type: ObservationType
    source_type: SourceType
    source_asset_id: str 
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # The extracted data
    nodes: List[ObservationNode] = Field(default_factory=list)
    edges: List[ObservationEdge] = Field(default_factory=list)