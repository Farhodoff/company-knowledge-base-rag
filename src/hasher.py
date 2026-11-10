import hashlib
from pathlib import Path

def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a document file to avoid duplicate vector indexing."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()
