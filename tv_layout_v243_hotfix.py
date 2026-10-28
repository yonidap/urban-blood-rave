from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

MARKER = "/* v2.43 TV fit + compact clue IDs */"
if MARKER in html:
    print("v2.43 TV fit hotfix already applied.")
    raise SystemExit(0)

css = r'''
    /* v2.43 TV fit + compact clue IDs */
    .screen{padding:1.5vh 3vw}
    .main{height:97vh}
    .bottom-zone{margin-top:.8vh;gap:22px;align-items:start;min-height:0}
    .clues{gap:5px}
    .clues-heading{margin-bottom:0}
    .clue-grid{gap:6px 18px}
    .clue-row{gap:10px;padding:8px 12px;min-height:64px}
    .clue-id{font-size:clamp(16px,1vw,19px);letter-spacing:.10em;min-width:28px}
    .clue-text{font-size:clamp(22px,1.65vw,31px);line-height:1.12}
    .scar-gallery{align-self:start!important;margin-top:40px;width:fit-content!important;max-width:636px!important}
    .scar-gallery.scar-cols-1{grid-template-columns:minmax(320px,360px)!important;width:360px!important;max-width:360px!important}
    .scar-gallery.scar-cols-2{grid-template-columns:repeat(2,minmax(285px,310px))!important;width:auto!important;max-width:636px!important}
    @media(max-width:1200px){
      .scar-gallery.scar-cols-1{width:330px!important;max-width:330px!important;grid-template-columns:minmax(300px,330px)!important}
      .scar-gallery.scar-cols-2{grid-template-columns:repeat(2,minmax(255px,285px))!important;max-width:586px!important}
    }
'''
if "</style>" not in html:
    raise SystemExit("v2.43 TV fit: </style> not found")
html = html.replace("</style>", css + "\n</style>", 1)

old_clue = "<div class=\"clue-id\">CLUE ${String(c.index).padStart(2,'0')}</div>"
new_clue = "<div class=\"clue-id\">${String(c.index).padStart(2,'0')}</div>"
if old_clue not in html:
    raise SystemExit("v2.43 TV fit: clue history ID anchor not found")
html = html.replace(old_clue, new_clue, 1)

old_gallery = "  return `<div class=\"scar-gallery\">${s.scarLoop.map(x=>"
new_gallery = "  const scarCols=Math.min(2,s.scarLoop.length);\n  return `<div class=\"scar-gallery scar-cols-${scarCols}\">${s.scarLoop.map(x=>"
if old_gallery not in html:
    raise SystemExit("v2.43 TV fit: scar gallery return anchor not found")
html = html.replace(old_gallery, new_gallery, 1)

page.write_text(html, encoding="utf-8")
print("Applied v2.43 TV vertical fit, compact clue numbers, and scar gallery sizing.")
