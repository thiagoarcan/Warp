import uuid


def new_id(prefix: str) -> str:
    """Generate a stable prefixed UUID string."""
    return f"{prefix}_{uuid.uuid4().hex}"
