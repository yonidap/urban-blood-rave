from pathlib import Path

ROOT = Path(__file__).resolve().parent
app_path = ROOT / "deployed" / "app.py"
app = app_path.read_text(encoding="utf-8")

MARKER = "# v2.37 privacy-safe generic push payloads"
if MARKER not in app:
    app += r'''

# v2.37 privacy-safe generic push payloads
# Keep routing/timing/tag behavior unchanged, but never expose gameplay details
# in lock-screen notification text. All push notifications look identical.
_previous_send_push_to_player = send_push_to_player

async def send_push_to_player(p, title, body, tag):
    return await _previous_send_push_to_player(
        p,
        'NOTIFICATION',
        '',
        tag,
    )
'''

app_path.write_text(app, encoding="utf-8")
print("Applied v2.37 privacy-safe generic push notification payloads.")
