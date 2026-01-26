from pathlib import Path

SQL_DIR = Path(__file__).parent  # Directory containing __init__.py (same level as sql/ files)


def load_sql(filename: str) -> str:
    """Load SQL from sql/ directory at package level."""
    file_path = SQL_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")
    return file_path.read_text()
