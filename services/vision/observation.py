import math
from typing import List, Dict, Any
import uuid

def calculate_center(bbox: List[float]) -> tuple:
    """Returns the (x, y) center pixel of a bounding box [x1, y1, x2, y2]"""
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

def pixel_distance(center1: tuple, center2: tuple) -> float:
    """Calculates Euclidean distance between two points"""
    return math.hypot(center2[0] - center1[0], center2[1] - center1[1])

def build_observation_state(raw_telemetry: Dict[str, Any], danger_radius: int = 250) -> Dict[str, Any]:
    """
    Takes raw dual-model output and builds a relational graph payload for the GNN.
    """
    entities = []
    spatial_relationships = []
    
    # 1. Standardize all detections into "Entities" with unique IDs
    # Process PPE
    for obj in raw_telemetry.get("ppe_objects", []):
        entities.append({
            "id": f"worker_gear_{uuid.uuid4().hex[:6]}",
            "category": "PPE",
            "class": obj["type"],
            "confidence": obj["confidence"],
            "bbox": obj["bounding_box"],
            "center": calculate_center(obj["bounding_box"])
        })
        
    # Process Equipment
    for obj in raw_telemetry.get("equipment_objects", []):
        entities.append({
            "id": f"machinery_{uuid.uuid4().hex[:6]}",
            "category": "HEAVY_EQUIPMENT",
            "class": obj["type"],
            "confidence": obj["confidence"],
            "bbox": obj["bounding_box"],
            "center": calculate_center(obj["bounding_box"])
        })

    # 2. Compute Spatial Relationships (The "Edges")
    # Separate them for easier comparison
    gear = [e for e in entities if e["category"] == "PPE"]
    machinery = [e for e in entities if e["category"] == "HEAVY_EQUIPMENT"]
    
    for m in machinery:
        for g in gear:
            dist = pixel_distance(m["center"], g["center"])
            
            # Rule 1: Danger Zone Proximity
            if dist < danger_radius:
                spatial_relationships.append({
                    "source_id": g["id"],
                    "target_id": m["id"],
                    "relationship": "IN_DANGER_ZONE",
                    "distance_pixels": round(dist, 2),
                    "severity": "CRITICAL"
                })
            # Rule 2: Safe Observation (Optional: if the GNN needs to know they exist but are safe)
            elif dist < (danger_radius * 2):
                spatial_relationships.append({
                    "source_id": g["id"],
                    "target_id": m["id"],
                    "relationship": "SAFE_PROXIMITY",
                    "distance_pixels": round(dist, 2),
                    "severity": "INFO"
                })

    # Clean up the payload (remove the temporary center points to save bandwidth)
    for e in entities:
        del e["center"]

    # 3. Return the final formatted state
    return {
        "status": "PROCESSED",
        "total_entities": len(entities),
        "entities": entities,
        "spatial_relationships": spatial_relationships
    }