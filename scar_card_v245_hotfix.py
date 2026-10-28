from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

MARKER = "/* v2.45 scar card overflow fix */"
if MARKER in html:
    print("v2.45 scar card hotfix already applied.")
    raise SystemExit(0)

css = r'''
    /* v2.45 scar card overflow fix */
    .scar-person{
      grid-template-columns:minmax(126px,145px) minmax(0,1fr)!important;
      gap:14px!important;
      padding:12px 14px!important;
      overflow:hidden;
    }
    .scar-thumb{width:145px!important;height:112px!important;max-width:100%!important;min-width:0!important}
    .scar-thumb canvas{max-width:145px!important;max-height:112px!important}
    .scar-mini-copy{min-width:0!important;overflow:hidden}
    .scar-person .scar-mini-name{
      font-size:clamp(22px,1.55vw,29px)!important;
      line-height:1.05!important;
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
      max-width:100%;
    }
    @media(max-width:1200px){
      .scar-person{grid-template-columns:minmax(112px,132px) minmax(0,1fr)!important;gap:12px!important}
      .scar-thumb{width:132px!important;height:102px!important}
      .scar-thumb canvas{max-width:132px!important;max-height:102px!important}
      .scar-person .scar-mini-name{font-size:clamp(20px,1.45vw,26px)!important}
    }
'''
if "</style>" not in html:
    raise SystemExit("v2.45 scar card: </style> not found")
html = html.replace("</style>", css + "\n</style>", 1)
page.write_text(html, encoding="utf-8")
print("Applied v2.45 scar card text overflow fix.")
