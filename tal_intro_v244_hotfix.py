from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

MARKER = "// v2.44 Tal intro trim"
if MARKER in html:
    print("v2.44 Tal intro trim already applied.")
    raise SystemExit(0)

old = """    const p=video.play();if(p&&typeof p.catch==='function')p.catch(()=>{});\n    if(typeof video.requestVideoFrameCallback==='function')video.requestVideoFrameCallback(frameLoop);else requestAnimationFrame(rafLoop);"""
new = """    // v2.44 Tal intro trim\n    const beginPlayback=()=>{\n      const p=video.play();if(p&&typeof p.catch==='function')p.catch(()=>{});\n      if(typeof video.requestVideoFrameCallback==='function')video.requestVideoFrameCallback(frameLoop);else requestAnimationFrame(rafLoop);\n    };\n    const isTal=/\\/tal\\.mp4(?:[?#]|$)/i.test(video.currentSrc||video.src||'');\n    if(isTal && video.currentTime<1.28){\n      video.pause();\n      video.addEventListener('seeked',beginPlayback,{once:true});\n      try{video.currentTime=Math.min(1.38,Math.max(0,(Number.isFinite(video.duration)?video.duration-.08:1.38)))}catch(_){beginPlayback()}\n      return;\n    }\n    beginPlayback();"""

if old not in html:
    raise SystemExit("v2.44 Tal intro trim: playback anchor not found")
html = html.replace(old, new, 1)
page.write_text(html, encoding="utf-8")
print("Applied v2.44 Tal intro trim: reveal playback starts at ~1.38 s.")
