from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
runpy.run_path(str(ROOT / "player_hotfix.py"), run_name="__main__")
