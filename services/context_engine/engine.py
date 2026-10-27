from typing import Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime, UTC

from packages.shared_schemas.graph import ContextGraph, GraphMetadata, GraphNode, GraphEdge, Provenance
from packages.shared_schemas.observation import Observation
from .resolver import EntityResolver
from .repository import GraphRepository, MemoryGraphRepository


class ContextGraphEngine:
    def __init__(self, repository: Optional[GraphRepository] = None):
        # Inject the repository, default to memory for ease of testing
        self.repository = repository or MemoryGraphRepository()
        self.resolver = EntityResolver()

    def create_graph(self, session_id: str) -> ContextGraph:
        if self.repository.get_graph(session_id):
            raise ValueError(f"Session {session_id} already exists.")
        
        new_graph = ContextGraph(metadata=GraphMetadata(session_id=session_id))
        self.repository.save_graph(new_graph)
        return new_graph

    def get_graph(self, session_id: str) -> Optional[ContextGraph]:
        return self.repository.get_graph(session_id)

    def add_observation(self, session_id: str, observation: Observation) -> ContextGraph:
        graph = self.get_graph(session_id)
        if not graph:
            raise ValueError(f"Session {session_id} not found.")

        id_mapping: Dict[str, UUID] = {}

        # --- 1. RESOLVE OR CREATE NODES ---
        for obs_node in observation.nodes:
            existing_uuid = self.resolver.find_existing_node(graph, obs_node)

            if existing_uuid:
                self.resolver.merge_node(graph.nodes[existing_uuid], obs_node, observation)
                id_mapping[obs_node.local_id] = existing_uuid
            else:
                canonical_id = uuid4()
                id_mapping[obs_node.local_id] = canonical_id

                prov = Provenance(
                    source_asset_id=observation.source_asset_id,
                    observation_id=str(observation.observation_id),
                    confidence=obs_node.confidence,
                    timestamp=observation.timestamp
                )

                graph_node = GraphNode(
                    id=canonical_id,
                    type=obs_node.type,
                    properties=obs_node.properties,
                    provenance_history=[prov]
                )

                graph.nodes[canonical_id] = graph_node
                graph.metadata.total_nodes += 1

        # --- 2. RESOLVE OR CREATE EDGES ---
        for obs_edge in observation.edges:
            source_uuid = id_mapping.get(obs_edge.source_local_id)
            target_uuid = id_mapping.get(obs_edge.target_local_id)

            if not source_uuid or not target_uuid:
                continue 

            existing_edge = next(
                (e for e in graph.edges 
                 if e.source == source_uuid 
                 and e.target == target_uuid 
                 and e.relationship == obs_edge.relationship), 
                None
            )

            new_prov = Provenance(
                source_asset_id=observation.source_asset_id,
                observation_id=str(observation.observation_id),
                confidence=obs_edge.confidence,
                timestamp=observation.timestamp
            )

            if existing_edge:
                existing_edge.provenance_history.append(new_prov)
                if obs_edge.distance_pixels is not None:
                    existing_edge.measurements["distance_pixels"] = obs_edge.distance_pixels
                existing_edge.updated_at = datetime.now(UTC)
            else:
                graph_edge = GraphEdge(
                    source=source_uuid,
                    target=target_uuid,
                    relationship=obs_edge.relationship,
                    measurements=(
                        {"distance_pixels": obs_edge.distance_pixels}
                        if obs_edge.distance_pixels is not None
                        else {}
                    ),
                    provenance_history=[new_prov]
                )
                graph.edges.append(graph_edge)
                graph.metadata.total_edges += 1

        graph.metadata.version += 1
        
        # --- 3. PERSIST CHANGES ---
        self.repository.save_graph(graph)
        
        return graph