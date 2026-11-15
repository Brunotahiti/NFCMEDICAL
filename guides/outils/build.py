#!/usr/bin/env python3
"""Génère les guides PDF (pharmacie, grossiste, technicien) et leurs pages en images pour la liseuse du portail.
Usage : python3 build.py <dossier des captures> <dossier de sortie>
Les captures sont produites par capture.js (voir README du dossier)."""
import sys, os, subprocess, json, tempfile, re
SHOTS = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2])
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ICON = os.path.join(ROOT, 'icons', 'icon-512.png')
CONTACT = 'ManaProcess · 87 28 98 34 · direction@manaprocess.com'
DATE = 'Novembre 2026'

def img(n): return 'file://' + os.path.join(SHOTS, n + '.jpg')
def phone(n, cap=''):
    return f'<figure class="phone"><div class="bezel"><img src="{img(n)}" alt=""></div>' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'
def crop(n, cap=''):
    return f'<figure class="crop"><img src="{img(n)}" alt="">' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'
def duo(a, ca, b, cb): return f'<div class="duo">{phone(a, ca)}{phone(b, cb)}</div>'
def steps(*xs): return '<ol class="steps">' + ''.join(f'<li>{x}</li>' for x in xs) + '</ol>'
def bullets(*xs): return '<ul class="bul">' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul>'
def tip(t, x): return f'<div class="box tip"><b>{t}</b><p>{x}</p></div>'
def warn(t, x): return f'<div class="box warn"><b>{t}</b><p>{x}</p></div>'
def key(t, x): return f'<div class="box key"><b>{t}</b><p>{x}</p></div>'
def split(text, fig, rev=False, wide=False): return f'<div class="split{" rev" if rev else ""}{" wide" if wide else ""}"><div class="txt">{text}</div><div class="fig">{fig}</div></div>'
URL = 'manaprocess.cloud/materiel/'
def desk(n, cap='', small=False):
    return (f'<figure class="desk{" sm" if small else ""}"><div class="win"><div class="bar"><i></i><i></i><i></i><span>🔒 {URL}</span></div><img src="{img(n)}" alt=""></div>'
            + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>')
def win(n, cap=''):
    return f'<figure class="crop win1"><img src="{img(n)}" alt="">' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'
def faq(*qa): return '<div class="faq">' + ''.join(f'<div class="qa"><b>{q}</b><p>{a}</p></div>' for q, a in qa) + '</div>'

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@500;600;700&display=swap');
:root{--hero:#0B5361;--hero2:#0E8F93;--accent:#0A7C88;--brand:#62CFC4;--ink:#0D2730;--muted:#5B7078;--bg:#EDF6F8;--line:#D5DFE1;
  --warn:#A65F00;--warnsoft:#FBEBD0;--ok:#1A7F54;--oksoft:#DCF2E6;--crit:#B8352B;--critsoft:#FADFDC}
*{box-sizing:border-box}html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font-family:Inter,"Segoe UI",Arial,sans-serif;color:var(--ink);font-size:10.4pt;line-height:1.5}
h1,h2,h3{font-family:Sora,"Segoe UI",Arial,sans-serif;margin:0;letter-spacing:-.01em}
p{margin:0 0 2.2mm}
.chap{break-before:page;margin-bottom:5mm}
.chap.first{break-before:auto}
.chead{display:flex;align-items:center;gap:5mm;padding:5mm 6mm;border-radius:5mm;background:linear-gradient(120deg,var(--hero),var(--hero2));color:#fff;margin-bottom:5mm}
.chead .n{font-family:Sora,sans-serif;font-size:22pt;font-weight:700;color:var(--brand);min-width:13mm}
.chead h2{font-size:17pt;font-weight:600}
.chead .lead{font-size:9.6pt;color:#CDEAEE;margin-top:1mm}
.mk{font-size:1px;color:#fff;line-height:1}
.chead .mk{color:var(--hero)}
h3{font-size:12pt;color:var(--hero);margin:4.5mm 0 2mm;display:flex;align-items:center;gap:2.5mm}
h3::before{content:"";width:2.4mm;height:2.4mm;border-radius:50%;background:var(--brand);flex:none}
.split{display:grid;grid-template-columns:1fr 60mm;gap:7mm;align-items:start;margin:2mm 0 4mm;break-inside:avoid}
.split.rev{grid-template-columns:60mm 1fr}.split.rev .fig{order:-1}
.split.wide{grid-template-columns:1fr 82mm}.split.wide.rev{grid-template-columns:82mm 1fr}
.desk{margin:3mm 0 4mm;break-inside:avoid}.desk.sm{margin:2mm 22mm 4mm}
.desk .win{border-radius:3mm;overflow:hidden;border:.3mm solid #C3D2D6;background:#fff}
.desk .bar{height:6.2mm;background:#E6EEF0;display:flex;align-items:center;gap:1.5mm;padding:0 3mm;border-bottom:.3mm solid #D3DEE1}
.desk .bar i{width:2.2mm;height:2.2mm;border-radius:50%;background:#F26B5B}.desk .bar i:nth-child(2){background:#F5BE4F}.desk .bar i:nth-child(3){background:#5FCB6B}
.desk .bar span{margin-left:5mm;width:70mm;background:#fff;border-radius:2mm;height:3.8mm;font-size:6.6pt;color:#5B7078;display:flex;align-items:center;padding:0 2.4mm}
.desk img{display:block;width:100%}
.win1 img{border-radius:4mm}
.roles{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin:3mm 0 4mm}
.roles .r{background:var(--bg);border-radius:4mm;padding:4mm;break-inside:avoid}.roles .r b{display:block;font-family:Sora,sans-serif;color:var(--hero);margin-bottom:1mm}
.roles .r .dv{display:inline-block;font-size:8pt;font-weight:600;color:var(--accent);background:#fff;border-radius:10mm;padding:.3mm 2.4mm;margin-bottom:1.6mm}
.phone{margin:0;break-inside:avoid}
.phone .bezel{background:#0E1E24;border-radius:7mm;padding:1.6mm}
.phone img{display:block;width:100%;border-radius:5.6mm}
figcaption{font-size:8.4pt;color:var(--muted);text-align:center;margin-top:2mm;line-height:1.35}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:9mm;padding:0 12mm;margin:3mm 0 4mm;break-inside:avoid}
.crop{margin:3mm auto;break-inside:avoid;max-width:118mm}.crop img{display:block;width:100%;border-radius:4mm;border:.3mm solid var(--line)}
.split .crop img{max-width:100%}
.steps{list-style:none;padding:0;margin:2mm 0 3mm;counter-reset:s}
.steps li{counter-increment:s;position:relative;padding:0 0 2.6mm 10mm;min-height:7mm}
.steps li::before{content:counter(s);position:absolute;left:0;top:-.2mm;width:6.6mm;height:6.6mm;border-radius:50%;background:var(--accent);color:#fff;font:700 9pt/6.6mm Sora,sans-serif;text-align:center}
.bul{padding:0 0 0 5mm;margin:1mm 0 3mm}.bul li{margin-bottom:1.4mm}.bul li::marker{color:var(--accent)}
.box{border-radius:3.5mm;padding:3mm 4mm;margin:3mm 0;break-inside:avoid;font-size:9.6pt}
.box>b{display:block;font-family:Sora,sans-serif;font-size:9.8pt;margin-bottom:.8mm}.box p{margin:0}
.tip{background:var(--bg);border-left:1.2mm solid var(--accent)}.tip b{color:var(--accent)}
.warn{background:var(--warnsoft);border-left:1.2mm solid var(--warn)}.warn b{color:var(--warn)}
.key{background:var(--oksoft);border-left:1.2mm solid var(--ok)}.key b{color:var(--ok)}
.ui{display:inline-block;font-weight:600;color:var(--hero);background:var(--bg);border:.25mm solid var(--line);border-radius:1.6mm;padding:0 1.6mm;font-size:9.4pt;white-space:nowrap}
.tag{display:inline-block;font-weight:700;font-size:8.6pt;border-radius:10mm;padding:0 2.2mm}
.t-w{background:var(--warnsoft);color:var(--warn)}.t-c{background:var(--critsoft);color:var(--crit)}.t-o{background:var(--oksoft);color:var(--ok)}
table.t{width:100%;border-collapse:collapse;margin:2mm 0 4mm;font-size:9.4pt;break-inside:avoid}
table.t th{text-align:left;background:var(--hero);color:#fff;font-weight:600;padding:2mm 3mm}
table.t td{padding:2mm 3mm;border-bottom:.3mm solid var(--line);vertical-align:top}
table.t tr:nth-child(even) td{background:#F6FAFB}
.faq .qa{padding:3mm 0;border-bottom:.3mm solid var(--line);break-inside:avoid}.faq .qa b{font-family:Sora,sans-serif;color:var(--hero);display:block;margin-bottom:1mm}.faq p{margin:0}
.toc{margin-top:4mm}.toc .row{display:flex;align-items:baseline;gap:3mm;padding:2.6mm 0;border-bottom:.3mm solid var(--line)}
.toc .row .n{font-family:Sora,sans-serif;font-weight:700;color:var(--accent);width:9mm}
.toc .row .t{flex:1;font-weight:600}.toc .row .d{flex:1;color:var(--muted);font-size:9pt}.toc .row .pg{font-family:Sora,sans-serif;font-weight:600;color:var(--hero);width:10mm;text-align:right}
.toch{font-family:Sora,sans-serif;font-size:20pt;font-weight:700;color:var(--hero);margin-bottom:2mm}
.intro{display:grid;grid-template-columns:1fr 1fr;gap:5mm;margin-top:7mm}
.intro .c{background:var(--bg);border-radius:4mm;padding:4mm 5mm}.intro .c b{font-family:Sora,sans-serif;color:var(--hero);display:block;margin-bottom:1mm}
.contact{margin-top:6mm;border-radius:4mm;padding:4mm 5mm;background:linear-gradient(120deg,var(--hero),var(--hero2));color:#fff;break-inside:avoid}
.flow{display:flex;align-items:stretch;gap:0;margin:4mm 0 5mm;break-inside:avoid}
.flow .fs{flex:1;background:var(--bg);border-radius:3mm;padding:3mm 2mm;text-align:center;position:relative;margin-right:4mm}
.flow .fs:last-child{margin-right:0}
.flow .fs:not(:last-child)::after{content:"›";position:absolute;right:-3.6mm;top:50%;transform:translateY(-50%);color:var(--accent);font:700 12pt Sora,sans-serif}
.flow .fs b{display:block;font-family:Sora,sans-serif;font-size:8.8pt;color:var(--hero)}.flow .fs span{font-size:7.8pt;color:var(--muted)}
.flow .fs:nth-child(3){background:linear-gradient(120deg,var(--hero),var(--hero2))}.flow .fs:nth-child(3) b{color:#fff}.flow .fs:nth-child(3) span{color:#CDEAEE}
table.memo td{padding:3mm;font-size:10pt}table.memo td:first-child{width:42mm}
.contact b{font-family:Sora,sans-serif;font-size:11pt;color:var(--brand)}
"""

COVER_CSS = r"""
@page{size:A4;margin:0}
.cover{width:210mm;height:297mm;position:relative;overflow:hidden;background:linear-gradient(160deg,#083F4B 0%,#0B5361 38%,#0E8F93 100%);color:#fff}
.cover .glow{position:absolute;right:-40mm;top:-30mm;width:150mm;height:150mm;border-radius:50%;background:radial-gradient(circle,rgba(127,233,242,.35),rgba(127,233,242,0) 70%)}
.cover .wave{position:absolute;left:0;right:0;bottom:0;height:85mm}
.cover .top{position:absolute;left:20mm;top:22mm;display:flex;align-items:center;gap:5mm}
.cover .top img{width:22mm;height:22mm;border-radius:5mm}
.cover .brand{font-family:Sora,sans-serif;font-size:19pt;font-weight:700}.cover .brand span{color:#62CFC4}
.cover .brand small{display:block;font-family:Inter,sans-serif;font-size:9.5pt;font-weight:400;color:#CDEAEE}
.cover .title{position:absolute;left:20mm;right:20mm;top:70mm}
.cover .kicker{font-family:Sora,sans-serif;letter-spacing:.25em;text-transform:uppercase;font-size:10pt;color:#62CFC4;font-weight:600}
.cover h1{font-size:34pt;line-height:1.08;margin:4mm 0 5mm;font-weight:700}
.cover .sub{font-size:13pt;color:#DDF1F3;max-width:140mm;line-height:1.45}
.cover .pill{display:inline-block;margin-top:8mm;background:rgba(255,255,255,.14);border:.3mm solid rgba(255,255,255,.35);border-radius:20mm;padding:2mm 5mm;font-size:10pt}
.cover .phones{position:absolute;right:18mm;bottom:22mm;display:flex;gap:5mm;align-items:flex-end}
.cover .phones .bezel{background:#071A1F;border-radius:6mm;padding:1.4mm}
.cover .phones img{display:block;border-radius:4.8mm}
.cover .phones .dwin{background:#F4F8F9;border-radius:3mm;overflow:hidden;border:.4mm solid rgba(255,255,255,.5)}
.cover .phones .dwin img{border-radius:0}
.cover .dbar{height:5mm;display:flex;align-items:center;gap:1.3mm;padding:0 2.6mm;background:#E6EEF0}
.cover .dbar i{width:1.9mm;height:1.9mm;border-radius:50%;background:#F26B5B}.cover .dbar i:nth-child(2){background:#F5BE4F}.cover .dbar i:nth-child(3){background:#5FCB6B}
.cover .foot{position:absolute;left:20mm;bottom:14mm;font-size:9pt;color:#CDEAEE}
"""

def cover(kicker, title, sub, audience, shots):
    ph = ''.join((f'<div class="dwin"><div class="dbar"><i></i><i></i><i></i></div><img src="{img(s)}" style="width:{w}mm" alt=""></div>' if s[0] in 'gp' and not s.startswith('p_m')
                  else f'<div class="bezel"><img src="{img(s)}" style="width:{w}mm" alt=""></div>') for s, w in shots)
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}{COVER_CSS}</style></head><body>
<div class="cover"><div class="glow"></div>
<svg class="wave" viewBox="0 0 210 85" preserveAspectRatio="none"><path d="M0 40C40 28 80 30 120 42S185 56 210 44V85H0Z" fill="rgba(95,214,207,.18)"/><path d="M0 58C45 48 90 52 130 62S190 70 210 62V85H0Z" fill="rgba(95,214,207,.22)"/></svg>
<div class="top"><img src="file://{ICON}" alt=""><div class="brand">Mana<span>Process</span><small>Gestion du parc matériel · Parc NFC</small></div></div>
<div class="title"><div class="kicker">{kicker}</div><h1>{title}</h1><div class="sub">{sub}</div><div class="pill">{audience}</div></div>
<div class="phones">{ph}</div>
<div class="foot">Version {DATE} · https://manaprocess.cloud/materiel/</div></div></body></html>'''

def body(chapters, intro_html, pages=None):
    toc = ''.join(f'<div class="row"><span class="n">{i+1:02d}</span><span class="t">{c[0]}</span><span class="d">{c[1]}</span><span class="pg">{(pages or {}).get(i+1, "")}</span></div>' for i, c in enumerate(chapters))
    chs = ''.join(f'<section class="chap"><div class="chead"><div class="n">{i+1:02d}</div><div><h2>{c[0]}</h2><div class="lead">{c[1]}</div></div><span class="mk">§CHAP{i+1:02d}§</span></div>{c[2]}</section>' for i, c in enumerate(chapters))
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>@page{{size:A4;margin:16mm 16mm 18mm}}{CSS}</style></head><body>
<div class="toch">Sommaire</div>{intro_html}<div class="toc">{toc}</div>{chs}</body></html>'''

def render(cover_html, body_fn, chapters, intro, footer_label, out):
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, 'c.html'), 'w').write(cover_html)
    js = os.path.join(tmp, 'r.js')
    footer = ('<div style="width:100%;font-family:Arial,sans-serif;font-size:7.5pt;color:#5B7078;padding:0 16mm;display:flex;justify-content:space-between">'
              f'<span>{footer_label}</span><span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    open(js, 'w').write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const [kind,src,dst,foot]=process.argv.slice(2);
const p=await b.newPage();await p.goto('file://'+src,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
const o={path:dst,format:'A4',printBackground:true,preferCSSPageSize:true};
if(kind==='body')Object.assign(o,{displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:foot,margin:{top:'16mm',bottom:'18mm',left:'16mm',right:'16mm'}});
await p.pdf(o);await b.close();})();""")
    def run(kind, html, pdf):
        open(os.path.join(tmp, 'b.html'), 'w').write(html)
        subprocess.run(['node', js, kind, os.path.join(tmp, 'b.html' if kind == 'body' else 'c.html'), pdf, footer], check=True, cwd=tmp)
    run('cover', None, os.path.join(tmp, 'cover.pdf')) if False else subprocess.run(['node', js, 'cover', os.path.join(tmp, 'c.html'), os.path.join(tmp, 'cover.pdf'), footer], check=True, cwd=tmp)
    run('body', body_fn(chapters, intro), os.path.join(tmp, 'body.pdf'))
    import pypdf
    r = pypdf.PdfReader(os.path.join(tmp, 'body.pdf')); pages = {}
    for i, pg in enumerate(r.pages):
        for m in re.findall(r'§CHAP(\d\d)§', pg.extract_text() or ''): pages.setdefault(int(m), i + 1)
    run('body', body_fn(chapters, intro, pages), os.path.join(tmp, 'body.pdf'))
    w = pypdf.PdfWriter()
    for f in ('cover.pdf', 'body.pdf'):
        for pg in pypdf.PdfReader(os.path.join(tmp, f)).pages: w.add_page(pg)
    w.add_metadata({'/Title': footer_label, '/Author': 'ManaProcess', '/Subject': 'Guide d\'utilisation MédiParc NFC'})
    w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    with open(out, 'wb') as fh: w.write(fh)
    pages_dir = os.path.join(OUT, 'pages', c_key(out)); os.makedirs(pages_dir, exist_ok=True)
    for f in os.listdir(pages_dir): os.remove(os.path.join(pages_dir, f))
    subprocess.run(['pdftoppm', '-r', '150', '-jpeg', '-jpegopt', 'quality=82', out, os.path.join(pages_dir, 'p')], check=True)
    for f in sorted(os.listdir(pages_dir)):
        n = int(re.sub(r'\D', '', f)); os.rename(os.path.join(pages_dir, f), os.path.join(pages_dir, '%02d.jpg' % n))
    toc = [{'n': i + 1, 'title': re.sub('<[^>]+>', ' ', c[0]), 'page': pages.get(i + 1, 0) + 1} for i, c in enumerate(chapters)]
    json.dump({'title': footer_label, 'pages': len(w.pages), 'toc': toc}, open(os.path.join(pages_dir, 'index.json'), 'w'), ensure_ascii=False)
    print(out, len(w.pages), 'pages', os.path.getsize(out) // 1024, 'Ko', 'chapitres trouvés :', len(pages), '/', len(chapters))

def c_key(out): return os.path.basename(out).replace('guide-', '').replace('.pdf', '')
sys.path.insert(0, os.path.dirname(__file__))
from contenu import pharmacie, administrateur, technicien
os.makedirs(OUT, exist_ok=True)
for g in (pharmacie, administrateur, technicien):
    c = g(globals())
    render(cover(*c['cover']), body, c['chapters'], c['intro'], c['footer'], os.path.join(OUT, c['file']))
