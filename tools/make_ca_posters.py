"""Render Sarkari Posting CURRENT AFFAIRS posters (1080x1350 PNG).

Usage: python3 make_ca_posters.py ca.json out_dir
Each item: id, tag, date, head_hi, head_en, points:[{hi,en}] (3), fact_hi, fact_en
"""
import json, sys, html, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE / "fonts"

CSS = """
@font-face{font-family:Dev;font-weight:400;src:url(FONTS/noto-sans-devanagari-devanagari-400-normal.woff2)}
@font-face{font-family:Dev;font-weight:700;src:url(FONTS/noto-sans-devanagari-devanagari-700-normal.woff2)}
@font-face{font-family:Dev;font-weight:800;src:url(FONTS/noto-sans-devanagari-devanagari-800-normal.woff2)}
@font-face{font-family:Pop;font-weight:500;src:url(FONTS/poppins-latin-500-normal.woff2)}
@font-face{font-family:Pop;font-weight:700;src:url(FONTS/poppins-latin-700-normal.woff2)}
@font-face{font-family:Pop;font-weight:800;src:url(FONTS/poppins-latin-800-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#14213D;--teal:#0F766E;--teal2:#115E59;--mint:#E6F4F1;--gold:#FFC145;--paper:#FBFAF6;--muted:#5A6270;--line:#D7E3E0}
body{width:1080px;height:1350px;font-family:Pop,Dev,sans-serif;background:var(--paper);color:var(--ink);overflow:hidden;display:flex;flex-direction:column}
.top{background:linear-gradient(135deg,var(--teal2),var(--teal));color:#fff;padding:40px 60px 36px;position:relative;overflow:hidden}
.top:after{content:"";position:absolute;right:-90px;bottom:-140px;width:360px;height:360px;border-radius:50%;border:40px solid rgba(255,255,255,.08)}
.brand{display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:800;font-size:32px;letter-spacing:1px}.logo span{color:var(--gold)}
.ca{font-family:Pop,Dev;font-weight:700;font-size:24px;background:#fff;color:var(--teal2);padding:6px 18px;border-radius:40px}
.meta{margin-top:30px;display:flex;gap:14px;align-items:center}
.tag{font-weight:700;font-size:21px;letter-spacing:3px;color:var(--gold);border:2px solid var(--gold);padding:5px 16px;border-radius:8px}
.date{font-weight:500;font-size:22px;opacity:.9}
.hhi{margin-top:22px;font-family:Pop,Dev;font-weight:800;font-size:50px;line-height:1.28}
.hen{margin-top:12px;font-weight:700;font-size:28px;line-height:1.3;color:#CDEDE7}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px;padding:30px 60px 24px}
.lbl{font-family:Pop,Dev;font-weight:800;font-size:28px;color:var(--teal2)}
.pt{display:flex;gap:20px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:24px 26px}
.n{flex:none;width:48px;height:48px;border-radius:50%;background:var(--teal);color:#fff;font-weight:800;font-size:24px;display:flex;align-items:center;justify-content:center;margin-top:2px}
.ph{font-family:Pop,Dev;font-weight:700;font-size:31px;line-height:1.38}
.pe{font-weight:500;font-size:21px;color:var(--muted);line-height:1.4;margin-top:5px}
.fact{margin:0 60px 34px;background:#FFF4D6;border-left:10px solid var(--gold);border-radius:16px;padding:22px 26px}
.fact .k{font-family:Pop,Dev;font-weight:800;font-size:24px;color:#8A5A00}
.fact .v{font-family:Pop,Dev;font-weight:700;font-size:29px;line-height:1.38;margin-top:6px}
.fact .e{font-weight:500;font-size:20px;color:var(--muted);margin-top:4px}
.foot{flex:none;padding:16px 60px;background:var(--ink);color:#cfd6e2;font-family:Pop,Dev;font-size:20px;display:flex;justify-content:space-between}
.foot b{color:#fff;font-family:Pop}
"""


def page(j):
    e = lambda s: html.escape(str(s))
    pts = "".join(
        f'<div class="pt"><div class="n">{i+1}</div><div><div class="ph">{e(p["hi"])}</div><div class="pe">{e(p["en"])}</div></div></div>'
        for i, p in enumerate(j["points"]))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS.replace('FONTS', FONTS.as_uri())}</style></head><body>
<div class="top">
  <div class="brand"><div class="logo">SARKARI <span>POSTING</span></div><div class="ca">करंट अफेयर्स</div></div>
  <div class="meta"><div class="tag">{e(j['tag'])}</div><div class="date">{e(j['date'])}</div></div>
  <div class="hhi">{e(j['head_hi'])}</div>
  <div class="hen">{e(j['head_en'])}</div>
</div>
<div class="body"><div class="lbl">मुख्य बिंदु / Key Points</div>{pts}</div>
<div class="fact"><div class="k">परीक्षा के लिए याद रखें</div><div class="v">{e(j['fact_hi'])}</div><div class="e">{e(j['fact_en'])}</div></div>
<div class="foot"><span>रोज़ के करंट अफेयर्स के लिए पेज फॉलो करें</span><span>Follow <b>Sarkari Posting</b></span></div>
</body></html>"""


def main(src, out):
    out = pathlib.Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    items = json.loads(pathlib.Path(src).read_text(encoding="utf-8"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/google/chrome/chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for j in items:
            hp = out / f"{j['id']}.html"
            hp.write_text(page(j), encoding="utf-8")
            pg.goto(hp.as_uri()); pg.wait_for_timeout(400)
            bottom = pg.evaluate("document.querySelector('.foot').getBoundingClientRect().bottom")
            if bottom > 1351:
                print(f"WARNING {j['id']}: content reaches {bottom:.0f}px (overlaps footer)")
            pg.screenshot(path=str(out / f"Sarkari-Posting-CA-{j['id']}.png"))
            hp.unlink()
            print("ok", j["id"], int(bottom))
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
