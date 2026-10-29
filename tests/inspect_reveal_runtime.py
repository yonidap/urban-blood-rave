import inspect
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployed'))
os.environ.setdefault('HOST_KEY', 'ci-host-key')
import app as game  # noqa: E402

for name in sorted(dir(game)):
    low = name.lower()
    if not any(k in low for k in ('clue', 'reveal', 'queue')):
        continue
    obj = getattr(game, name)
    if callable(obj):
        print(f'\n=== {name} ===')
        try:
            print(inspect.getsource(obj))
        except Exception as exc:
            print(f'<source unavailable: {exc}>')
