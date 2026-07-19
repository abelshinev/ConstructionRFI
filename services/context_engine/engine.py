from typing import Dict, Optional
from uuid import uuid4

from packages.shared_schemas.graph import ContextGraph, GraphMetadata, GraphNode, GraphEdge, Provenance
from packages.shared_schemas.observation import Observation

class ContextGraphEngine:
    def __init__(self):
        # For this prototype, we will store active sessions in memory.
        # In production, this would load/save to Postgres/Redis.
        self._active_sessions: Dict[str, ContextGraph] = {}

    def create_graph(self, session_id: str) -> ContextGraph:
        """Initializes a brand new session graph."""
        if session_id in self._active_sessions:
            raise ValueError(f"Session {session_id} already exists.")
            
        new_graph = ContextGraph(
            metadata=GraphMetadata(session_id=session_id)
        )
        self._active_sessions[session_id] = new_graph
        return new_graph

    def get_graph(self, session_id: str) -> Optional[ContextGraph]:
        """Retrieves the current state of the world model."""
        return self._active_sessions.get(session_id)

    def add_observation(self, session_id: str, observation: Observation) -> ContextGraph:
        """
        Ingests an observation and blindly appends it to the graph.
        (Entity Resolution will be injected here in the next phase).
        """
        graph = self.get_graph(session_id)
        if not graph:
            raise ValueError(f"Session {session_id} not found. Create it first.")

        # We need to map the observation's local_ids to canonical Graph UUIDs
        # so we can connect the edges properly.
        id_mapping: Dict[str, str] = {}

        # 1. PROCESS NODES (Naive Append)
        for obs_node in observation.nodes:
            # Generate a canonical UUID for the graph
            canonical_id = uuid4()
            id_mapping[obs_node.local_id] = canonical_id

            # Create provenance record
            prov = Provenance(
                source_asset_id=observation.source_asset_id,
                observation_id=str(observation.observation_id),
                confidence=obs_node.confidence,
                timestamp=observation.timestamp
            )

            # Create the canonical graph node
            graph_node = GraphNode(
                id=canonical_id,
                type=obs_node.type,
                properties=obs_node.properties,
                provenance_history=[prov]
            )

            # Append to graph dict
            graph.nodes[canonical_id] = graph_node
            graph.metadata.total_nodes += 1

        # 2. PROCESS EDGES (Naive Append)
        for obs_edge in observation.edges:
            # Look up the canonical UUIDs we just created
            source_uuid = id_mapping.get(obs_edge.source_local_id)
            target_uuid = id_mapping.get(obs_edge.target_local_id)

            if not source_uuid or not target_uuid:
                continue # Skip invalid edges

            prov = Provenance(
                source_asset_id=observation.source_asset_id,
                observation_id=str(observation.observation_id),
                confidence=obs_edge.confidence,
                timestamp=observation.timestamp
            )

            graph_edge = GraphEdge(
                source=source_uuid,
                target=target_uuid,
                relationship=obs_edge.relationship,
                provenance_history=[prov]
            )

            graph.edges.append(graph_edge)
            graph.metadata.total_edges += 1

        # 3. UPDATE METADATA
        graph.metadata.version += 1

        return graph