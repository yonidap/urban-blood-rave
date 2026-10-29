from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

BUILD = "v2.48"
MARKER = "// v2.48 build freshness controller"

if MARKER not in html:
    css = r'''
    #ubrBuildBadge{display:none;position:fixed;right:10px;bottom:8px;z-index:20000;font:9px/1 monospace;letter-spacing:.12em;color:rgba(255,255,255,.45);pointer-events:none}
    body.ubr-debug-build #ubrBuildBadge{display:block}
'''
    if "</style>" not in html:
        raise SystemExit("v2.48 runtime hotfix: </style> not found")
    html = html.replace("</style>", css + "\n</style>", 1)

    badge = f'<div id="ubrBuildBadge">{BUILD}</div>\n'
    if "<script>" not in html:
        raise SystemExit("v2.48 runtime hotfix: <script> anchor not found")
    html = html.replace("<script>", badge + "<script>", 1)

    anchor = "let socket;\n"
    if anchor not in html:
        raise SystemExit("v2.48 runtime hotfix: socket anchor not found")
    js = f'''\n// v2.48 build freshness controller\nconst UBR_BUILD='{BUILD}';\ndocument.documentElement.dataset.ubrBuild=UBR_BUILD;\nif(new URLSearchParams(location.search).has('debug'))document.body.classList.add('ubr-debug-build');\nasync function checkBuildFreshness(){{\n  try{{\n    const r=await fetch('/static/build.txt?t='+Date.now(),{{cache:'no-store'}});\n    if(!r.ok)return;\n    const live=(await r.text()).trim();\n    if(live && live!==UBR_BUILD) location.reload();\n  }}catch(_){{}}\n}}\nsetInterval(checkBuildFreshness,12000);\nsetTimeout(checkBuildFreshness,2500);\n'''
    html = html.replace(anchor, anchor + js + "\n", 1)

page.write_text(html, encoding="utf-8")
print(f"Applied {BUILD} screen runtime freshness controller.")
