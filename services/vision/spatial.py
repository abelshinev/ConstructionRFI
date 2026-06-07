import math
import logging

logger = logging.getLogger(__name__)

def calculate_center(bbox):
    """Calculates the (x, y) center pixel of a bounding box [x1, y1, x2, y2]"""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def pixel_distance(center1, center2):
    """Calculates the Euclidean distance between two center points"""
    return math.hypot(center2[0] - center1[0], center2[1] - center1[1])

def analyze_scene_safety(telemetry_data, danger_radius_pixels=300):
    """
    Cross-references PPE detections with Heavy Equipment detections.
    Returns a list of safety violations.
    """
    violations = []
    
    ppe_objects = telemetry_data.get("ppe_objects", [])
    equipment_objects = telemetry_data.get("equipment_objects", [])

    # If there's no equipment, there's no proximity danger
    if not equipment_objects:
        return {"status": "SAFE", "violations": violations}

    # Compare every piece of equipment against every detected worker/PPE
    for equip in equipment_objects:
        equip_center = calculate_center(equip["bounding_box"])
        
        for ppe in ppe_objects:
            ppe_center = calculate_center(ppe["bounding_box"])
            distance = pixel_distance(equip_center, ppe_center)
            
            # If the distance is less than our threshold, trigger an alert
            if distance < danger_radius_pixels:
                violations.append({
                    "severity": "CRITICAL",
                    "rule_broken": "Proximity Violation",
                    "description": f"{ppe['type']} detected dangerously close ({int(distance)}px) to {equip['type']}.",
                    "equipment_involved": equip["type"],
                    "entity_involved": ppe["type"]
                })

    if violations:
        return {"status": "DANGER", "violations": violations}
    
    return {"status": "SAFE", "violations": []}