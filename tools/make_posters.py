"""Render Sarkari Posting job posters (1080x1350 PNG) from jobs.json.

Usage: python3 make_posters.py jobs.json out_dir
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
:root{--navy:#0B2545;--navy2:#13315C;--saffron:#F26B1D;--gold:#FFC145;--cream:#FFF8EE;--ink:#1B1B1B;--muted:#5A6270;--green:#138A36}
body{width:1080px;height:1350px;font-family:Pop,Dev,sans-serif;background:var(--cream);color:var(--ink);overflow:hidden}
.top{background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 100%);color:#fff;padding:44px 60px 40px;position:relative;overflow:hidden}
.top:after{content:"";position:absolute;right:-120px;top:-120px;width:380px;height:380px;border-radius:50%;background:rgba(255,193,69,.12)}
.brand{display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:800;font-size:34px;letter-spacing:1px}
.logo span{color:var(--gold)}
.alert{font-family:Pop,Dev;font-weight:700;font-size:26px;background:var(--saffron);padding:6px 20px;border-radius:40px}
.cat{margin-top:34px;display:inline-block;font-weight:700;font-size:22px;letter-spacing:3px;color:var(--gold);border:2px solid var(--gold);padding:6px 18px;border-radius:8px}
.org{margin-top:20px;font-weight:800;font-size:56px;line-height:1.1}
.thi{margin-top:12px;font-family:Pop,Dev;font-weight:700;font-size:36px;color:#FFE3C7;line-height:1.35}
.vac{display:flex;align-items:center;gap:36px;margin:-1px 0 0;background:var(--saffron);color:#fff;padding:26px 60px}
.vac .n{font-weight:800;font-size:110px;line-height:1}
.vac .l{font-family:Pop,Dev;font-weight:800;font-size:40px;line-height:1.2}
.vac .l small{display:block;font-family:Pop;font-weight:500;font-size:24px;opacity:.95}
.posts{padding:26px 60px 0;font-weight:700;font-size:28px;color:var(--navy)}
.grid{padding:20px 60px 0;display:grid;grid-template-columns:1fr;gap:16px}
.row{display:flex;background:#fff;border-radius:16px;box-shadow:0 2px 0 rgba(11,37,69,.08);border-left:10px solid var(--navy);padding:16px 24px;align-items:center;gap:22px}
.row .k{width:210px;flex:none;font-family:Pop,Dev;font-weight:800;font-size:28px;color:var(--navy);line-height:1.15}
.row .k small{display:block;font-family:Pop;font-weight:500;font-size:18px;color:var(--muted)}
.row .v{font-family:Pop,Dev;font-weight:700;font-size:28px;line-height:1.3}
.row .v small{display:block;font-family:Pop;font-weight:500;font-size:20px;color:var(--muted)}
.dates{display:flex;gap:16px;padding:20px 60px 0}
.d{flex:1;border-radius:16px;padding:18px 24px;color:#fff}
.d.s{background:var(--green)}
.d.e{background:#C62828}
.d .k{font-family:Pop,Dev;font-weight:700;font-size:24px}
.d .k small{font-family:Pop;font-weight:500;font-size:18px;opacity:.9}
.d .v{font-weight:800;font-size:44px;line-height:1.15}
.apply{margin:20px 60px 0;background:var(--navy);color:#fff;border-radius:16px;padding:16px 24px;display:flex;justify-content:space-between;align-items:center}
.apply .k{font-family:Pop,Dev;font-weight:700;font-size:26px}
.apply .v{font-weight:700;font-size:30px;color:var(--gold)}
.foot{position:absolute;left:0;right:0;bottom:0;padding:16px 60px;background:#0B2545;color:#cfd6e2;font-family:Pop,Dev;font-size:20px;display:flex;justify-content:space-between}
.foot b{color:#fff;font-family:Pop}
"""

ROW = '<div class="row"><div class="k">{khi}<small>{ken}</small></div><div class="v">{vhi}<small>{ven}</small></div></div>'


def page(j):
    e = {k: html.escape(str(v)) for k, v in j.items()}
    rows = "".join([
        ROW.format(khi="योग्यता", ken="Qualification", vhi=e["qual_hi"], ven=e["qual_en"]),
        ROW.format(khi="आयु सीमा", ken="Age Limit", vhi=e["age_hi"], ven=e["age_en"]),
        ROW.format(khi="आवेदन शुल्क", ken="Application Fee", vhi=e["fee_hi"], ven=e["fee_en"]),
    ])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS.replace('FONTS', FONTS.as_uri())}</style></head><body>
<div class="top">
  <div class="brand"><div class="logo">SARKARI <span>POSTING</span></div><div class="alert">नई भर्ती</div></div>
  <div class="cat">{e['category']}</div>
  <div class="org">{e['org_en']}</div>
  <div class="thi">{e['title_hi']}</div>
</div>
<div class="vac"><div class="n">{e['vacancies']}</div><div class="l">कुल पद<small>Total Vacancies</small></div></div>
<div class="posts">{e['posts_en']}</div>
<div class="grid">{rows}</div>
<div class="dates">
  <div class="d s"><div class="k">आवेदन शुरू <small>Start</small></div><div class="v">{e['start']}</div></div>
  <div class="d e"><div class="k">अंतिम तिथि <small>Last Date</small></div><div class="v">{e['last']}</div></div>
</div>
<div class="apply"><div class="k">आधिकारिक वेबसाइट / Apply:</div><div class="v">{e['site']}</div></div>
<div class="foot"><span>आवेदन से पहले आधिकारिक अधिसूचना ज़रूर पढ़ें</span><span>Follow <b>Sarkari Posting</b></span></div>
</body></html>"""


def main(src, out):
    out = pathlib.Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    jobs = json.loads(pathlib.Path(src).read_text(encoding="utf-8"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/google/chrome/chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for j in jobs:
            hp = out / f"{j['id']}.html"
            hp.write_text(page(j), encoding="utf-8")
            pg.goto(hp.as_uri()); pg.wait_for_timeout(400)
            over = pg.evaluate("document.querySelector('.apply').getBoundingClientRect().bottom")
            if over > 1290:
                print(f"WARNING {j['id']}: content reaches {over:.0f}px (overlaps footer)")
            pg.screenshot(path=str(out / f"Sarkari-Posting-{j['id']}.png"))
            print("ok", j["id"])
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
