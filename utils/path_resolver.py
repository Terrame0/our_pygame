import sys
from pathlib import Path

def resolve_path(relative_path) -> Path:
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).resolve().parent.parent
    return base_path / Path(relative_path)