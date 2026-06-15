import math
import uuid
from typing import List, Dict, Any

def calculate_center(bbox: List[float]) -> tuple:
    """Returns the (x, y) center pixel of a bounding box [x1, y1, x2, y2]"""
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

def is_inside(inner_center: tuple, outer_bbox: List[float]) -> bool:
    """Checks if a point (x,y) is inside a bounding box"""
    x, y = inner_center
    x1, y1, x2, y2 = outer_bbox
    return (x1 <= x <= x2) and (y1 <= y <= y2)

def pixel_distance(center1: tuple, center2: tuple) -> float:
    """Calculates Euclidean distance between two points"""
    return math.hypot(
        center2[0] - center1[0], 
        center2[1] - center1[1]
    )

def build_observation_state(raw_telemetry: Dict[str, Any], tracking_threshold: int = 1000) -> Dict[str, Any]:
    """
    Transforms raw vision telemetry into a pure, factual scene graph payload.
    Groups PPE to the humans wearing them.
    """
    entities = []
    spatial_relationships = []
    
    raw_ppe_detections = raw_telemetry.get("ppe_objects", [])
    raw_equipment = raw_telemetry.get("equipment_objects", [])

    # --- 1. ENTITY ASSOCIATION: Grouping Workers and PPE ---
    
    # Separate people from the gear
    people = [obj for obj in raw_ppe_detections if obj["type"].lower() in ["person", "worker"]]
    gear = [obj for obj in raw_ppe_detections if obj["type"].lower() not in ["person", "worker"]]
    
    workers = []
    
    # If YOLO detected people, assign gear to them
    for person in people:
        person_center = calculate_center(person["bounding_box"])
        worker_entity = {
            "id": f"worker_{uuid.uuid4().hex[:6]}",
            "category": "WORKER",
            "confidence": person["confidence"],
            "bbox": person["bounding_box"],
            "center": person_center,
            "equipment": {
                "helmet": False,
                "vest": False
                # Add other PPE types here as needed
            }
        }
        
        # Check all gear to see if it physically overlaps this person
        assigned_gear_indices = []
        for i, item in enumerate(gear):
            item_center = calculate_center(item["bounding_box"])
            
            # If the gear's center is inside the person's bounding box
            if is_inside(item_center, person["bounding_box"]):
                if "hardhat" in item["type"].lower() or "helmet" in item["type"].lower():
                    worker_entity["equipment"]["helmet"] = True
                elif "vest" in item["type"].lower():
                    worker_entity["equipment"]["vest"] = True
                    
                assigned_gear_indices.append(i)
                
        # Remove assigned gear from the pool so it isn't orphaned
        for i in sorted(assigned_gear_indices, reverse=True):
            gear.pop(i)
            
        workers.append(worker_entity)
        entities.append(worker_entity)

    # Handle "Orphaned" Gear (Gear detected, but YOLO missed the person)
    # We can create a placeholder "unknown_worker" for these based on the gear's location
    for item in gear:
        entities.append({
            "id": f"orphaned_gear_{uuid.uuid4().hex[:6]}",
            "category": "UNASSIGNED_PPE",
            "class": item["type"],
            "bbox": item["bounding_box"],
            "center": calculate_center(item["bounding_box"])
        })

    # --- 2. ADD HEAVY EQUIPMENT ENTITIES ---
    machinery = []
    for obj in raw_equipment:
        machine_entity = {
            "id": f"machinery_{uuid.uuid4().hex[:6]}",
            "category": "HEAVY_EQUIPMENT",
            "class": obj["type"],
            "confidence": obj["confidence"],
            "bbox": obj["bounding_box"],
            "center": calculate_center(obj["bounding_box"])
        }
        machinery.append(machine_entity)
        entities.append(machine_entity)

    # --- 3. SPATIAL FACTS (The Edges) ---
    # We only measure between Workers and Machinery. We don't judge the distance.
    for m in machinery:
        for w in workers:
            dist = pixel_distance(m["center"], w["center"])
            
            # Only record if they are within a tracking threshold to prevent graph bloat
            if dist <= tracking_threshold:
                spatial_relationships.append({
                    "source_id": w["id"],
                    "target_id": m["id"],
                    "relationship": "SPATIAL_PROXIMITY",
                    "distance_pixels": round(dist, 2)
                })

    # Clean up computation artifacts
    for e in entities:
        if "center" in e:
            del e["center"]

    return {
        "status": "OBSERVATION_COMPLETE",
        "total_entities": len(entities),
        "entities": entities,
        "spatial_relationships": spatial_relationships
    }