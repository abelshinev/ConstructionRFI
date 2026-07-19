from enum import Enum

class NodeType(str, Enum):
    WORKER = "WORKER"
    SUPERVISOR = "SUPERVISOR"
    PPE = "PPE"
    EQUIPMENT = "EQUIPMENT"
    VEHICLE = "VEHICLE"
    TOOL = "TOOL"
    LOCATION = "LOCATION"
    DOCUMENT = "DOCUMENT"
    ISSUE = "ISSUE"
    REGULATION = "REGULATION"
    INSPECTION = "INSPECTION"

class RelationshipType(str, Enum):
    WEARING = "WEARING"
    NEAR = "NEAR"
    LOCATED_AT = "LOCATED_AT"
    REFERENCES = "REFERENCES"
    OBSERVED_IN = "OBSERVED_IN"
    REPORTED_BY = "REPORTED_BY"
    ASSIGNED_TO = "ASSIGNED_TO"
    SUPPORTS = "SUPPORTS"

class ObservationType(str, Enum):
    VISION = "VISION"
    OCR = "OCR"
    SPEECH = "SPEECH"
    DOCUMENT = "DOCUMENT"

class SourceType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    PDF = "PDF"