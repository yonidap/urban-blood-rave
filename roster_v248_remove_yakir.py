from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parent
app_path = ROOT / "deployed" / "app.py"
text = app_path.read_text(encoding="utf-8")
MARKER = "# v2.48 roster: Yakir removed"

if MARKER in text:
    print("v2.48 roster update already applied.")
    raise SystemExit(0)


def seed_entries(source: str):
    tree = ast.parse(source)
    assign = next(
        (
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "PLAYERS_SEED" for t in node.targets)
        ),
        None,
    )
    if not assign or not isinstance(assign.value, ast.List):
        raise SystemExit("v2.48 roster: PLAYERS_SEED list not found")

    rows = []
    for elt in assign.value.elts:
        if not isinstance(elt, ast.Call) or not isinstance(elt.func, ast.Name) or elt.func.id != "dict":
            raise SystemExit("v2.48 roster: unexpected PLAYERS_SEED entry")
        values = {}
        for kw in elt.keywords:
            if kw.arg and isinstance(kw.value, ast.Constant):
                values[kw.arg] = kw.value.value
        rows.append((elt, values))
    return rows


entries = seed_entries(text)
yakir = [(node, values) for node, values in entries if values.get("id") == "yakir"]
if len(yakir) != 1:
    raise SystemExit(f"v2.48 roster: expected exactly one Yakir seed, found {len(yakir)}")

node, _ = yakir[0]
lines = text.splitlines(keepends=True)
del lines[node.lineno - 1:node.end_lineno]
text = "".join(lines)
text += "\n# v2.48 roster: Yakir removed\n"

updated = seed_entries(text)
ids = [values.get("id") for _, values in updated]
protected_ids = [values.get("id") for _, values in updated if values.get("protected") is True]
expected_ids = [
    "shalev", "gal", "dan", "alan", "kiso", "hacker", "yonatan",
    "tal", "maor", "rafael", "lutz", "uri",
]
if ids != expected_ids:
    raise SystemExit(f"v2.48 roster: unexpected final roster {ids}")
if protected_ids != ["gal", "tal", "uri"]:
    raise SystemExit(f"v2.48 roster: unexpected protected roster {protected_ids}")

compile(text, str(app_path), "exec")
app_path.write_text(text, encoding="utf-8")
print("Applied v2.48 roster: 12 players, Yakir removed, 3 protected Humans remain.")
