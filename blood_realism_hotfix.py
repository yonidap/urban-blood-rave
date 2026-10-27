from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

if "/* v2.33 realistic wet blood pass */" in html:
    print("v2.33 blood realism pass already applied.")
    raise SystemExit(0)
if "/* v2.31 cinematic blood-wash transitions */" not in html:
    raise SystemExit("v2.33 blood realism pass: v2.31 blood transition baseline not found")

new_blood_css = r'''/* v2.33 realistic wet blood pass */
    .blood-transition{position:fixed;inset:0;z-index:10000;overflow:hidden;pointer-events:none;visibility:hidden;isolation:isolate}
    .blood-transition.cover,.blood-transition.reveal{visibility:visible}
    .blood-sheet-svg{position:absolute;left:-3vw;top:-145vh;width:106vw;height:145vh;will-change:transform;backface-visibility:hidden;overflow:visible}
    .blood-transition.cover .blood-sheet-svg{animation:bloodCover .92s cubic-bezier(.40,.01,.16,1) forwards}
    .blood-transition.reveal .blood-sheet-svg{transform:translateY(126vh);animation:bloodReveal .70s cubic-bezier(.58,.02,.90,.56) forwards}
    .blood-grain{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 17% 38%,rgba(255,190,198,.035),transparent 19%),radial-gradient(ellipse at 69% 48%,rgba(255,190,198,.025),transparent 24%),repeating-linear-gradient(103deg,transparent 0 17px,rgba(255,255,255,.018) 17px 18px,transparent 18px 39px);mix-blend-mode:screen}
    .blood-transition.cover .blood-grain{animation:bloodGrainIn .92s ease forwards}
    .blood-transition.reveal .blood-grain{animation:bloodGrainOut .46s ease forwards}
    body.blood-washing #screen{filter:saturate(.88) brightness(.94);transition:filter .12s linear}
    .blood-satellite{transform-box:fill-box;transform-origin:center;opacity:0}
    .blood-transition.cover .blood-drop-a{animation:bloodDropA .62s .19s cubic-bezier(.31,.02,.51,1) both}
    .blood-transition.cover .blood-drop-b{animation:bloodDropB .68s .12s cubic-bezier(.31,.02,.51,1) both}
    .blood-transition.cover .blood-drop-c{animation:bloodDropC .58s .27s cubic-bezier(.31,.02,.51,1) both}
    @keyframes bloodCover{0%{transform:translateY(0)}31%{transform:translateY(42vh)}56%{transform:translateY(78vh)}74%{transform:translateY(101vh)}88%{transform:translateY(115vh)}100%{transform:translateY(126vh)}}
    @keyframes bloodReveal{0%{transform:translateY(126vh)}18%{transform:translateY(138vh)}100%{transform:translateY(274vh)}}
    @keyframes bloodGrainIn{0%,34%{opacity:0}58%{opacity:.11}82%{opacity:.055}100%{opacity:.035}}
    @keyframes bloodGrainOut{0%{opacity:.055}100%{opacity:0}}
    @keyframes bloodDropA{0%{opacity:0;transform:translateY(-8px) scale(.72)}28%{opacity:.9}100%{opacity:.94;transform:translateY(86px) scale(1.04)}}
    @keyframes bloodDropB{0%{opacity:0;transform:translateY(-6px) scale(.78)}24%{opacity:.84}100%{opacity:.92;transform:translateY(118px) scale(1.08)}}
    @keyframes bloodDropC{0%{opacity:0;transform:translateY(-5px) scale(.75)}30%{opacity:.82}100%{opacity:.9;transform:translateY(72px) scale(1.02)}}
'''

pattern = r"/\* v2\.31 cinematic blood-wash transitions \*/.*?(?=\n\s*/\* Correctly targets #screen;)"
html, n = re.subn(pattern, new_blood_css, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit("v2.33 blood realism pass: could not replace blood CSS block")

new_svg = r'''<svg class="blood-sheet-svg" viewBox="0 0 1000 1450" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <linearGradient id="bloodBase" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#100003"/><stop offset="52%" stop-color="#1d0107"/><stop offset="82%" stop-color="#35040d"/><stop offset="100%" stop-color="#210006"/></linearGradient>
      <linearGradient id="bloodBody" x1="0" y1="0" x2=".24" y2="1"><stop offset="0%" stop-color="#240006" stop-opacity=".94"/><stop offset="42%" stop-color="#480711" stop-opacity=".91"/><stop offset="71%" stop-color="#6b0c1b" stop-opacity=".88"/><stop offset="89%" stop-color="#4c0713" stop-opacity=".93"/><stop offset="100%" stop-color="#270006" stop-opacity=".98"/></linearGradient>
      <linearGradient id="bloodEdgeLight" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#d15d6b" stop-opacity=".03"/><stop offset="14%" stop-color="#ffb0ba" stop-opacity=".18"/><stop offset="25%" stop-color="#d15d6b" stop-opacity=".025"/><stop offset="47%" stop-color="#f58b98" stop-opacity=".11"/><stop offset="61%" stop-color="#d15d6b" stop-opacity=".02"/><stop offset="82%" stop-color="#ffb8c1" stop-opacity=".14"/><stop offset="100%" stop-color="#d15d6b" stop-opacity=".02"/></linearGradient>
      <linearGradient id="bloodVerticalSheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#fff" stop-opacity="0"/><stop offset="10%" stop-color="#ffe4e7" stop-opacity=".025"/><stop offset="16%" stop-color="#fff" stop-opacity="0"/><stop offset="37%" stop-color="#ffd5da" stop-opacity=".035"/><stop offset="44%" stop-color="#fff" stop-opacity="0"/><stop offset="69%" stop-color="#ffdbe0" stop-opacity=".026"/><stop offset="76%" stop-color="#fff" stop-opacity="0"/><stop offset="91%" stop-color="#ffe2e5" stop-opacity=".028"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/></linearGradient>
      <filter id="bloodSurface" x="-7%" y="-5%" width="114%" height="114%">
        <feTurbulence type="fractalNoise" baseFrequency="0.006 0.017" numOctaves="3" seed="33" result="noise"/>
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="17" xChannelSelector="R" yChannelSelector="G" result="displaced"/>
        <feGaussianBlur in="SourceAlpha" stdDeviation="2.2" result="softAlpha"/>
        <feSpecularLighting in="softAlpha" surfaceScale="3.2" specularConstant=".30" specularExponent="22" lighting-color="#ffd9df" result="specular"><feDistantLight azimuth="228" elevation="52"/></feSpecularLighting>
        <feComposite in="specular" in2="SourceAlpha" operator="in" result="specularIn"/><feBlend in="displaced" in2="specularIn" mode="screen"/>
      </filter>
      <filter id="bloodSoft" x="-8%" y="-8%" width="116%" height="116%"><feGaussianBlur stdDeviation="5.5"/></filter>
    </defs>
    <path d="M0 0H1000V1160 C969 1178 950 1147 921 1190 C894 1230 867 1170 835 1201 C805 1230 785 1284 750 1214 C721 1160 699 1243 660 1201 C626 1165 605 1310 568 1218 C538 1161 512 1263 476 1208 C443 1163 421 1326 386 1217 C352 1158 326 1273 289 1200 C255 1144 230 1297 197 1211 C166 1152 139 1256 105 1197 C76 1148 44 1229 0 1191Z" fill="url(#bloodBase)"/>
    <path d="M0 0H1000V1180 C971 1200 948 1156 918 1213 C891 1262 865 1182 831 1223 C798 1260 783 1335 747 1238 C717 1172 693 1270 655 1220 C620 1173 601 1360 563 1240 C530 1170 507 1301 470 1228 C438 1171 416 1375 380 1245 C347 1171 318 1304 284 1222 C251 1158 226 1350 191 1240 C162 1171 133 1290 99 1217 C70 1157 43 1266 0 1212Z" fill="url(#bloodBody)" filter="url(#bloodSurface)"/>
    <g opacity=".28" fill="#110003" filter="url(#bloodSoft)"><ellipse cx="148" cy="910" rx="118" ry="245"/><ellipse cx="465" cy="780" rx="142" ry="300"/><ellipse cx="806" cy="925" rx="122" ry="250"/></g>
    <g opacity=".34" fill="none" stroke-linecap="round"><path d="M118 270 C104 520 132 792 111 1056" stroke="#8b1b29" stroke-opacity=".13" stroke-width="12"/><path d="M338 170 C357 450 318 780 347 1098" stroke="#b83b49" stroke-opacity=".085" stroke-width="8"/><path d="M612 210 C581 505 635 805 603 1110" stroke="#9b2433" stroke-opacity=".11" stroke-width="11"/><path d="M866 145 C895 430 842 755 877 1080" stroke="#bd3d4b" stroke-opacity=".075" stroke-width="7"/></g>
    <path d="M0 0H1000V1180 C971 1200 948 1156 918 1213 C891 1262 865 1182 831 1223 C798 1260 783 1335 747 1238 C717 1172 693 1270 655 1220 C620 1173 601 1360 563 1240 C530 1170 507 1301 470 1228 C438 1171 416 1375 380 1245 C347 1171 318 1304 284 1222 C251 1158 226 1350 191 1240 C162 1171 133 1290 99 1217 C70 1157 43 1266 0 1212Z" fill="url(#bloodVerticalSheen)" opacity=".92"/>
    <path d="M0 1212 C43 1266 70 1157 99 1217 C133 1290 162 1171 191 1240 C226 1350 251 1158 284 1222 C318 1304 347 1171 380 1245 C416 1375 438 1171 470 1228 C507 1301 530 1170 563 1240 C601 1360 620 1173 655 1220 C693 1270 717 1172 747 1238 C783 1335 798 1260 831 1223 C865 1182 891 1262 918 1213 C948 1156 971 1200 1000 1180" fill="none" stroke="#090002" stroke-opacity=".48" stroke-width="20" filter="url(#bloodSoft)"/>
    <path d="M0 1212 C43 1266 70 1157 99 1217 C133 1290 162 1171 191 1240 C226 1350 251 1158 284 1222 C318 1304 347 1171 380 1245 C416 1375 438 1171 470 1228 C507 1301 530 1170 563 1240 C601 1360 620 1173 655 1220 C693 1270 717 1172 747 1238 C783 1335 798 1260 831 1223 C865 1182 891 1262 918 1213 C948 1156 971 1200 1000 1180" fill="none" stroke="url(#bloodEdgeLight)" stroke-width="5.5" stroke-linecap="round" opacity=".72"/>
    <g fill="#4a0712" filter="url(#bloodSurface)"><ellipse class="blood-satellite blood-drop-a" cx="224" cy="1260" rx="10" ry="17"/><ellipse class="blood-satellite blood-drop-b" cx="696" cy="1248" rx="8" ry="13"/><path class="blood-satellite blood-drop-c" d="M888 1232 C899 1246 902 1268 895 1281 C889 1292 878 1288 876 1275 C874 1260 879 1243 888 1232Z"/></g>
  </svg>'''
html, n = re.subn(r'<svg class="blood-sheet-svg".*?</svg>', new_svg, html, count=1, flags=re.S)
if n != 1:
    raise SystemExit("v2.33 blood realism pass: could not replace blood SVG")

html = html.replace("// v2.31 cinematic blood-wash transition controller", "// v2.33 realistic wet blood-wash transition controller", 1)
html = html.replace("  bloodOverlay.classList.remove('cover','reveal');\n}", "  bloodOverlay.classList.remove('cover','reveal');\n  document.body.classList.remove('blood-washing');\n}", 1)
html = html.replace("  clearTransitionClasses();\n  void bloodOverlay.offsetWidth;\n  bloodOverlay.classList.add('cover');", "  clearTransitionClasses();\n  document.body.classList.add('blood-washing');\n  void bloodOverlay.offsetWidth;\n  bloodOverlay.classList.add('cover');", 1)
html = html.replace("},700);", "},890);", 1)
html = html.replace("},150);\n    transitionCleanup=setTimeout", "},125);\n    transitionCleanup=setTimeout", 1)
old_cleanup = """    transitionCleanup=setTimeout(()=>{\n      if(seq!==transitionSeq)return;\n      bloodOverlay.classList.remove('reveal');\n    },680);"""
new_cleanup = """    transitionCleanup=setTimeout(()=>{\n      if(seq!==transitionSeq)return;\n      bloodOverlay.classList.remove('reveal');\n      document.body.classList.remove('blood-washing');\n    },735);"""
if old_cleanup not in html:
    raise SystemExit("v2.33 blood realism pass: cleanup block not found")
html = html.replace(old_cleanup, new_cleanup, 1)

page.write_text(html, encoding="utf-8")
print("Applied v2.33 blood realism pass: darker depth, transparency, wet highlights and satellite droplets.")
