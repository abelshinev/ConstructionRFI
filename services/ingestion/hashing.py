import hashlib
from pathlib import Path

# adding sha256 cipher for hashing 
def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()