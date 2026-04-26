from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

UI_DIST = BASE_DIR / "ui/dist"
print(UI_DIST.exists())
