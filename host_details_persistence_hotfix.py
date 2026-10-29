from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "host.html"
html = page.read_text(encoding="utf-8")

MARKER = "// host details persistence hotfix"

if MARKER not in html:
    state_anchor = "let readiness={players:[],scheduler:{ok:true}};\n"
    if state_anchor not in html:
        raise SystemExit("host details hotfix: readiness state anchor missing")
    html = html.replace(
        state_anchor,
        state_anchor
        + "// host details persistence hotfix\n"
        + "const ubrHostDetailsOpen={gameState:false,manual:false};\n"
        + "function ubrRememberHostDetail(name,el){ubrHostDetailsOpen[name]=!!el.open}\n",
        1,
    )

    game_details = '<details><summary><b>GAME STATE · SPOILERS</b></summary>'
    game_details_persistent = '<details ${ubrHostDetailsOpen.gameState?\'open\':\'\'} ontoggle="ubrRememberHostDetail(\'gameState\',this)"><summary><b>GAME STATE · SPOILERS</b></summary>'
    if game_details not in html:
        raise SystemExit("host details hotfix: game-state details anchor missing")
    html = html.replace(game_details, game_details_persistent, 1)

    manual_details = '''    <details>\n      <summary><b>ADVANCED MANUAL OVERRIDES</b></summary>'''
    manual_details_persistent = '''    <details ${ubrHostDetailsOpen.manual?'open':''} ontoggle="ubrRememberHostDetail('manual',this)">\n      <summary><b>ADVANCED MANUAL OVERRIDES</b></summary>'''
    if manual_details not in html:
        raise SystemExit("host details hotfix: manual details anchor missing")
    html = html.replace(manual_details, manual_details_persistent, 1)

page.write_text(html, encoding="utf-8")
print("Applied host details persistence hotfix: open sections survive live re-renders.")
