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
BOXI = {'tip': '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3Z"/>', 'warn': '<path d="M12 4 2.8 19.5h18.4Z"/><path d="M12 10v4.5M12 17.2v.1"/>', 'key': '<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5M12 14.5v2.5"/>'}
def _box(c, t, x): return f'<div class="box {c}"><span class="bi"><svg viewBox="0 0 24 24">{BOXI[c]}</svg></span><div><b>{t}</b><p>{x}</p></div></div>'
def tip(t, x): return _box('tip', t, x)
def warn(t, x): return _box('warn', t, x)
def key(t, x): return _box('key', t, x)
def split(text, fig, rev=False, wide=False): return f'<div class="split{" rev" if rev else ""}{" wide" if wide else ""}"><div class="txt">{text}</div><div class="fig">{fig}</div></div>'
URL = 'manaprocess.cloud/materiel/'
def desk(n, cap='', small=False):
    return (f'<figure class="desk{" sm" if small else ""}"><div class="win"><div class="bar"><i></i><i></i><i></i><span>🔒 {URL}</span></div><img src="{img(n)}" alt=""></div>'
            + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>')
def win(n, cap=''):
    return f'<figure class="crop win1"><img src="{img(n)}" alt="">' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'
def annot(n, marks, cap=''):
    m = ''.join(f'<i class="mk2" style="left:{x}%;top:{y}%">{k+1}</i>' for k, (x, y) in enumerate(marks))
    return (f'<figure class="desk"><div class="win"><div class="bar"><i></i><i></i><i></i><span>🔒 {URL}</span></div><div class="ann"><img src="{img(n)}" alt="">{m}</div></div>'
            + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>')
def legend(*items): return '<div class="legend">' + ''.join(f'<div class="lg"><i>{k+1}</i><div><b>{t}</b><span>{d}</span></div></div>' for k, (t, d) in enumerate(items)) + '</div>'
def faq(*qa): return '<div class="faq">' + ''.join(f'<div class="qa"><b>{q}</b><p>{a}</p></div>' for q, a in qa) + '</div>'

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@400;500;600;700;800&display=swap');
:root{--hero:#0B5361;--hero2:#0E8F93;--deep:#073C47;--accent:#0A7C88;--brand:#62CFC4;--ink:#10262E;--muted:#5B7078;--bg:#EEF6F7;--bg2:#F6FAFB;--line:#D9E4E6;
  --warn:#9A5A00;--warnsoft:#FDF1DD;--ok:#17734D;--oksoft:#E3F4EB;--crit:#B8352B;--critsoft:#FBE4E1;--coral:#EF5B3C}
*{box-sizing:border-box}html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font-family:Inter,"Segoe UI",Arial,sans-serif;color:var(--ink);font-size:10.2pt;line-height:1.55;font-feature-settings:"ss01","cv11"}
h1,h2,h3{font-family:Sora,"Segoe UI",Arial,sans-serif;margin:0;letter-spacing:-.015em}
p{margin:0 0 2.4mm}
b{font-weight:600}
body{counter-reset:fig}
/* Chapitres */
.chap{break-before:page;margin-bottom:5mm}
.chead{display:grid;grid-template-columns:auto 1fr;gap:0 6mm;align-items:end;padding:1mm 0 5mm;margin-bottom:6mm;border-bottom:.5mm solid var(--line);position:relative}
.chead::after{content:"";position:absolute;left:0;bottom:-.5mm;width:38mm;height:1.2mm;border-radius:1mm;background:linear-gradient(90deg,var(--accent),var(--brand))}
.chead .n{grid-row:1/3;font-family:Sora,sans-serif;font-size:44pt;font-weight:800;line-height:.9;color:transparent;-webkit-text-stroke:.5mm var(--accent);letter-spacing:-.04em}
.chead .kk{font-family:Sora,sans-serif;font-size:8pt;font-weight:600;letter-spacing:.24em;text-transform:uppercase;color:var(--accent)}
.chead h2{font-size:21pt;font-weight:700;color:var(--deep);line-height:1.15;margin-top:1mm}
.chead .lead{grid-column:2;font-size:10.2pt;color:var(--muted);margin-top:1.6mm}
.mk{font-size:1px;color:#fff;line-height:1;position:absolute;font-family:Arial,sans-serif;font-feature-settings:normal}
h3{font-size:12.4pt;font-weight:700;color:var(--deep);margin:5.5mm 0 2.4mm;display:flex;align-items:center;gap:2.6mm;break-after:avoid}
h3::before{content:"";width:1.3mm;height:4.6mm;border-radius:1mm;background:linear-gradient(180deg,var(--brand),var(--accent));flex:none}
/* Mise en page */
.split{display:grid;grid-template-columns:1fr 60mm;gap:8mm;align-items:start;margin:2mm 0 4mm;break-inside:avoid}
.split.rev{grid-template-columns:60mm 1fr}.split.rev .fig{order:-1}
.split.wide{grid-template-columns:1fr 82mm}.split.wide.rev{grid-template-columns:82mm 1fr}
/* Figures */
figure{counter-increment:fig}
figcaption{font-size:8.2pt;color:var(--muted);text-align:center;margin-top:2.2mm;line-height:1.4}
figcaption::before{content:"Figure " counter(fig) "  ·  ";font-weight:700;color:var(--accent);letter-spacing:.02em}
.desk{margin:3mm 0 5mm;break-inside:avoid}.desk.sm{margin:2mm 22mm 5mm}
.desk .win{border-radius:3.2mm;overflow:hidden;border:.35mm solid #BFD0D4;background:#fff;outline:1.6mm solid var(--bg);outline-offset:0}
.desk .bar{height:6.4mm;background:linear-gradient(180deg,#F1F6F7,#E3ECEE);display:flex;align-items:center;gap:1.5mm;padding:0 3.2mm;border-bottom:.3mm solid #D3DEE1}
.desk .bar i{width:2.2mm;height:2.2mm;border-radius:50%;background:#F26B5B}.desk .bar i:nth-child(2){background:#F5BE4F}.desk .bar i:nth-child(3){background:#5FCB6B}
.desk .bar span{margin:0 auto;width:78mm;background:#fff;border:.25mm solid #D5E0E3;border-radius:2mm;height:4mm;font-size:6.6pt;color:#5B7078;display:flex;align-items:center;justify-content:center;padding:0 2.4mm}
.desk img{display:block;width:100%}
.ann{position:relative}
.mk2{position:absolute;transform:translate(-50%,-50%);width:6.4mm;height:6.4mm;border-radius:50%;background:var(--coral);color:#fff;border:.6mm solid #fff;font:700 8.6pt/5.2mm Sora,sans-serif;text-align:center;font-style:normal}
.legend{display:grid;grid-template-columns:1fr 1fr;gap:2.6mm 6mm;margin:1mm 0 4mm}
.lg{display:flex;gap:3mm;align-items:flex-start;break-inside:avoid}
.lg i{flex:none;width:6mm;height:6mm;border-radius:50%;background:var(--coral);color:#fff;font:700 8.4pt/6mm Sora,sans-serif;text-align:center;font-style:normal;margin-top:.4mm}
.lg b{display:block;font-family:Sora,sans-serif;font-size:9.6pt;color:var(--deep)}.lg span{font-size:9pt;color:var(--muted);line-height:1.4;display:block}
.win1 img{border-radius:4mm;border:.35mm solid #C9D7DA}
.phone{margin:0;break-inside:avoid}
.phone .bezel{background:linear-gradient(145deg,#1A2E35,#071418);border-radius:7.5mm;padding:1.7mm;border:.35mm solid #31474F}
.phone img{display:block;width:100%;border-radius:5.8mm}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:9mm;padding:0 12mm;margin:3mm 0 5mm;break-inside:avoid}
.crop{margin:3mm auto;break-inside:avoid;max-width:118mm}.crop img{display:block;width:100%;border-radius:4mm;border:.35mm solid #C9D7DA}
.split .crop img{max-width:100%}
/* Étapes */
.steps{list-style:none;padding:0;margin:2mm 0 3.5mm;counter-reset:s}
.steps li{counter-increment:s;position:relative;padding:.3mm 0 3mm 11mm;min-height:7mm}
.steps li::before{content:counter(s);position:absolute;left:0;top:0;width:6.8mm;height:6.8mm;border-radius:2mm;background:linear-gradient(135deg,var(--hero2),var(--hero));color:#fff;font:700 9pt/6.8mm Sora,sans-serif;text-align:center}
.steps li:not(:last-child)::after{content:"";position:absolute;left:3.25mm;top:7.6mm;bottom:.6mm;width:.35mm;background:var(--line)}
.bul{padding:0;margin:1mm 0 3.4mm;list-style:none}.bul li{margin-bottom:1.6mm;padding-left:5.4mm;position:relative}
.bul li::before{content:"";position:absolute;left:.6mm;top:2.1mm;width:1.8mm;height:1.8mm;border-radius:.5mm;background:var(--brand);transform:rotate(45deg)}
/* Encadrés */
.box{display:flex;gap:3.4mm;border-radius:3.5mm;padding:3.4mm 4.4mm;margin:3.4mm 0;break-inside:avoid;font-size:9.5pt;border:.35mm solid}
.box .bi{flex:none;width:7.4mm;height:7.4mm;border-radius:50%;display:grid;place-items:center;margin-top:.2mm}
.box .bi svg{width:4.4mm;height:4.4mm;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.box>div>b:first-child{display:block;font-family:Sora,sans-serif;font-size:9.8pt;margin-bottom:.6mm}.box p{margin:0;line-height:1.5}
.tip{background:var(--bg2);border-color:#CFE3E6}.tip .bi{background:var(--accent)}.tip>div>b:first-child{color:var(--accent)}
.warn{background:var(--warnsoft);border-color:#F2D7A8}.warn .bi{background:#C27A0E}.warn>div>b:first-child{color:var(--warn)}
.key{background:var(--oksoft);border-color:#BFE3CF}.key .bi{background:var(--ok)}.key>div>b:first-child{color:var(--ok)}
.ui{display:inline-block;font-weight:600;color:var(--hero);background:#fff;border:.3mm solid #C6D8DC;border-bottom-width:.6mm;border-radius:1.6mm;padding:0 1.7mm;font-size:9.1pt;white-space:nowrap;line-height:1.5}
.tag{display:inline-block;font-weight:700;font-size:8.4pt;border-radius:10mm;padding:.1mm 2.4mm}
.t-w{background:var(--warnsoft);color:var(--warn)}.t-c{background:var(--critsoft);color:var(--crit)}.t-o{background:var(--oksoft);color:var(--ok)}
/* Tableaux */
table.t{width:100%;border-collapse:separate;border-spacing:0;margin:2.4mm 0 4.4mm;font-size:9.2pt;break-inside:avoid;border:.35mm solid var(--line);border-radius:3mm;overflow:hidden}
table.t th{text-align:left;background:var(--deep);color:#fff;font-weight:600;padding:2.2mm 3.2mm;font-size:8.8pt;letter-spacing:.02em}
table.t td{padding:2.2mm 3.2mm;border-top:.3mm solid var(--line);vertical-align:top}
table.t tr:nth-child(even) td{background:var(--bg2)}
table.t td:first-child{font-weight:500}
.faq .qa{padding:3.2mm 0 3.2mm 9mm;border-bottom:.3mm solid var(--line);break-inside:avoid;position:relative}
.faq .qa::before{content:"?";position:absolute;left:0;top:3.2mm;width:6mm;height:6mm;border-radius:50%;background:var(--bg);color:var(--accent);font:700 9pt/6mm Sora,sans-serif;text-align:center}
.faq .qa b{font-family:Sora,sans-serif;color:var(--deep);display:block;margin-bottom:1mm}.faq p{margin:0;color:#34494F}
/* Sommaire */
.tochead{display:grid;grid-template-columns:1fr auto;align-items:end;border-bottom:.5mm solid var(--line);padding-bottom:4mm;margin-bottom:5mm;position:relative}
.tochead::after{content:"";position:absolute;left:0;bottom:-.5mm;width:38mm;height:1.2mm;border-radius:1mm;background:linear-gradient(90deg,var(--accent),var(--brand))}
.toch{font-family:Sora,sans-serif;font-size:26pt;font-weight:800;color:var(--deep);letter-spacing:-.03em}
.tochead small{font-size:9pt;color:var(--muted);text-align:right}
.toc{margin-top:3mm}
.toc .row{display:grid;grid-template-columns:11mm 1fr 12mm;align-items:baseline;padding:1.7mm 0;border-bottom:.3mm dashed #CFDCDF}
.toc .row .n{font-family:Sora,sans-serif;font-weight:700;color:var(--accent);font-size:10pt}
.toc .row .t{font-weight:600;font-size:10.4pt;color:var(--deep)}.toc .row .d{display:block;color:var(--muted);font-size:8.8pt;font-weight:400;margin-top:.3mm}
.toc .row .pg{font-family:Sora,sans-serif;font-weight:700;color:var(--hero);text-align:right}
.intro{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
.intro .c{background:var(--bg2);border:.35mm solid var(--line);border-radius:4mm;padding:3mm 4.5mm;font-size:9pt;line-height:1.45}.intro .c b{font-family:Sora,sans-serif;color:var(--deep);display:block;margin-bottom:1mm;font-size:10pt}
/* Prise en main */
.quick{break-before:page}
.qgrid{display:grid;grid-template-columns:1fr 1fr;gap:5mm;margin-top:2mm}
.qc{border:.35mm solid var(--line);border-radius:4.5mm;padding:6mm 6mm 7mm;min-height:52mm;background:#fff;break-inside:avoid;position:relative;overflow:hidden}
.qc::before{content:"";position:absolute;left:0;top:0;right:0;height:1.4mm;background:linear-gradient(90deg,var(--accent),var(--brand))}
.qc .qn{font-family:Sora,sans-serif;font-size:24pt;font-weight:800;color:var(--brand);line-height:1}
.qc b{display:block;font-family:Sora,sans-serif;font-size:11.4pt;color:var(--deep);margin:2mm 0 1.4mm}
.qc p{margin:0;font-size:10pt;color:#34494F;line-height:1.55}
.qshot{margin-top:7mm}.qshot.ph2{display:grid;grid-template-columns:44mm 44mm;justify-content:center;gap:10mm}
.contact{margin-top:6mm;border-radius:4mm;padding:5mm 6mm;background:linear-gradient(120deg,var(--deep),var(--hero2));color:#fff;break-inside:avoid}
.contact b{font-family:Sora,sans-serif;font-size:11pt;color:var(--brand)}
.roles{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin:3mm 0 4mm}
.roles .r{background:var(--bg2);border:.35mm solid var(--line);border-radius:4mm;padding:4mm;break-inside:avoid;font-size:9.4pt}.roles .r b{display:block;font-family:Sora,sans-serif;color:var(--deep);margin-bottom:1mm;font-size:10.6pt}
.roles .r .dv{display:inline-block;font-size:7.8pt;font-weight:700;color:#fff;background:var(--accent);border-radius:10mm;padding:.3mm 2.4mm;margin-bottom:2mm;letter-spacing:.02em}
.flow{display:flex;align-items:stretch;gap:0;margin:4mm 0 5mm;break-inside:avoid}
.flow .fs{flex:1;background:var(--bg2);border:.35mm solid var(--line);border-radius:3mm;padding:3mm 2mm;text-align:center;position:relative;margin-right:4mm}
.flow .fs:last-child{margin-right:0}
.flow .fs:not(:last-child)::after{content:"›";position:absolute;right:-3.6mm;top:50%;transform:translateY(-50%);color:var(--accent);font:700 12pt Sora,sans-serif}
.flow .fs b{display:block;font-family:Sora,sans-serif;font-size:8.8pt;color:var(--deep)}.flow .fs span{font-size:7.8pt;color:var(--muted)}
.flow .fs:nth-child(3){background:linear-gradient(120deg,var(--hero),var(--hero2));border-color:var(--hero)}.flow .fs:nth-child(3) b{color:#fff}.flow .fs:nth-child(3) span{color:#CDEAEE}
table.memo td{padding:3mm;font-size:10pt}table.memo td:first-child{width:42mm}
"""

COVER_CSS = r"""
@page{size:A4;margin:0}
.cover{width:210mm;height:297mm;position:relative;overflow:hidden;background:#fff;color:var(--ink)}
.cv-top{position:absolute;left:0;right:0;top:0;height:192mm;background:radial-gradient(120% 90% at 100% 0%,#14A3A3 0%,rgba(20,163,163,0) 55%),linear-gradient(160deg,#062F38 0%,#0B5361 55%,#0E7F86 100%);color:#fff;overflow:hidden}
.cv-arcs{position:absolute;right:-30mm;top:-25mm;width:170mm;height:170mm;opacity:.16}
.cv-grid{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.10) .35mm,transparent .4mm);background-size:6mm 6mm;opacity:.6}
.cv-head{position:absolute;left:20mm;right:20mm;top:18mm;display:flex;align-items:center;gap:4mm}
.cv-head img{width:15mm;height:15mm;border-radius:3.6mm}
.cv-brand{font-family:Sora,sans-serif;font-size:15pt;font-weight:700;line-height:1.1}.cv-brand span{color:#62CFC4}
.cv-brand small{display:block;font-family:Inter,sans-serif;font-size:8.6pt;font-weight:400;color:#BFE3E7}
.cv-ed{margin-left:auto;text-align:right;font-size:8.6pt;color:#BFE3E7;line-height:1.4}.cv-ed b{display:block;color:#fff;font-family:Sora,sans-serif;font-size:9.4pt}
.cv-title{position:absolute;left:20mm;right:20mm;top:52mm}
.cv-k{display:inline-flex;align-items:center;gap:2.4mm;font-family:Sora,sans-serif;letter-spacing:.28em;text-transform:uppercase;font-size:8.6pt;color:#62CFC4;font-weight:700}
.cv-k::before{content:"";width:10mm;height:.6mm;background:#62CFC4;border-radius:1mm}
.cover h1{font-size:44pt;line-height:1.02;margin:5mm 0 5mm;font-weight:800;letter-spacing:-.035em}
.cv-sub{font-size:12.4pt;color:#D9F0F2;max-width:118mm;line-height:1.5}
.cv-chips{margin-top:7mm;display:flex;gap:2.4mm;flex-wrap:wrap}
.cv-chips span{background:rgba(255,255,255,.12);border:.3mm solid rgba(255,255,255,.32);border-radius:20mm;padding:1.4mm 4mm;font-size:9pt;font-weight:500}
.cv-dev{position:absolute;right:16mm;top:136mm;display:flex;gap:5mm;align-items:flex-end}
.lap{display:flex;flex-direction:column;align-items:center}
.lap .scr{background:#0B1A1F;border-radius:3.6mm 3.6mm 1mm 1mm;padding:2.6mm 2.6mm 3.4mm;border:.4mm solid #31474F}
.lap .scr img{display:block;border-radius:.8mm}
.lap .base{height:4.6mm;background:linear-gradient(180deg,#D9E3E6,#A9BABF);border-radius:0 0 6mm 6mm;position:relative}
.lap .base::after{content:"";position:absolute;left:50%;top:0;transform:translateX(-50%);width:26mm;height:1.6mm;background:#8FA3A9;border-radius:0 0 2mm 2mm}
.ph{background:linear-gradient(145deg,#1A2E35,#071418);border-radius:7mm;padding:1.6mm;border:.4mm solid #31474F}
.ph img{display:block;border-radius:5.6mm}
.cv-learn{position:absolute;left:20mm;right:20mm;bottom:30mm}
.cv-learn h4{font-family:Sora,sans-serif;font-size:8.6pt;letter-spacing:.24em;text-transform:uppercase;color:var(--accent);margin:0 0 4mm;font-weight:700}
.cv-cols{display:grid;grid-template-columns:repeat(4,1fr);gap:5mm}
.cv-cols div{border-top:.8mm solid var(--brand);padding-top:2.6mm;font-size:8.8pt;color:var(--muted);line-height:1.4}
.cv-cols b{display:block;font-family:Sora,sans-serif;font-size:10pt;color:var(--deep);margin-bottom:1mm}
.cv-foot{position:absolute;left:20mm;right:20mm;bottom:12mm;display:flex;justify-content:space-between;font-size:8.4pt;color:var(--muted);border-top:.3mm solid var(--line);padding-top:3mm}
.back{width:210mm;height:297mm;position:relative;overflow:hidden;background:linear-gradient(160deg,#062F38 0%,#0B5361 55%,#0E7F86 100%);color:#fff}
.back .in{position:absolute;left:24mm;right:24mm;top:96mm;text-align:center}
.back img{width:24mm;height:24mm;border-radius:6mm}
.back h2{font-family:Sora,sans-serif;font-size:22pt;margin:7mm 0 3mm;font-weight:800}
.back p{color:#D9F0F2;font-size:11pt;line-height:1.6;margin:0}
.back .box2{margin:10mm auto 0;max-width:120mm;border:.3mm solid rgba(255,255,255,.3);border-radius:5mm;padding:6mm;background:rgba(255,255,255,.07);font-size:10.4pt;line-height:1.7}
.back .box2 b{color:#62CFC4;font-family:Sora,sans-serif}
.back .ft{position:absolute;left:0;right:0;bottom:14mm;text-align:center;font-size:8.6pt;color:#9CC9CF}
"""

ARCS = '<svg class="cv-arcs" viewBox="0 0 100 100" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round"><path d="M30 70a28 28 0 0 1 0-40"/><path d="M42 82a45 45 0 0 1 0-64"/><path d="M54 94a62 62 0 0 1 0-88"/><path d="M66 106a79 79 0 0 1 0-112"/></svg>'

def cover(kicker, title, sub, audience, shots, learn=(), chips=()):
    dev = ''.join((f'<div class="lap"><div class="scr"><img src="{img(n)}" style="width:{w}mm" alt=""></div><div class="base" style="width:{w + 22}mm"></div></div>' if n[0] in 'gp'
                   else f'<div class="ph"><img src="{img(n)}" style="width:{w}mm" alt=""></div>') for n, w in shots)
    cols = ''.join(f'<div><b>{t}</b>{d}</div>' for t, d in learn[:4])
    ch = ''.join(f'<span>{c}</span>' for c in ((audience,) + tuple(chips)))
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}{COVER_CSS}</style></head><body>
<div class="cover"><div class="cv-top"><div class="cv-grid"></div>{ARCS}
<div class="cv-head"><img src="file://{ICON}" alt=""><div class="cv-brand">Mana<span>Process</span><small>Gestion du parc matériel · Parc NFC</small></div><div class="cv-ed"><b>Édition {DATE}</b>manaprocess.cloud/materiel</div></div>
<div class="cv-title"><div class="cv-k">{kicker}</div><h1>{title}</h1><div class="cv-sub">{sub}</div><div class="cv-chips">{ch}</div></div></div>
<div class="cv-dev">{dev}</div>
<div class="cv-learn"><h4>Dans ce guide</h4><div class="cv-cols">{cols}</div></div>
<div class="cv-foot"><span>MédiParc NFC · Guide d'utilisation</span><span>{CONTACT}</span></div></div></body></html>'''

def backcover(label):
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}{COVER_CSS}</style></head><body>
<div class="back"><div class="cv-grid"></div>{ARCS}<div class="in"><img src="file://{ICON}" alt=""><h2>Besoin d'aide ?</h2>
<p>L'équipe ManaProcess vous accompagne pour la mise en service, la formation et l'utilisation au quotidien.</p>
<div class="box2"><b>Assistance</b><br>{CONTACT}<br>Du lundi au vendredi, de 8 h à 16 h (heure de Tahiti)<br><br><b>Portail</b><br>https://manaprocess.cloud/materiel/</div></div>
<div class="ft">{label} · Édition {DATE} · © ManaProcess</div></div></body></html>'''

def body(chapters, intro_html, pages=None, quick=None, label='', shots=()):
    toc = ''.join(f'<div class="row"><span class="n">{i+1:02d}</span><span class="t">{c[0]}<span class="d">{c[1]}</span></span><span class="pg">{(pages or {}).get(i+1, "")}</span></div>' for i, c in enumerate(chapters))
    chs = ''.join(f'<section class="chap"><div class="chead"><div class="n">{i+1:02d}</div><div><div class="kk">Chapitre {i+1}</div><h2>{c[0]}</h2></div><div class="lead">{c[1]}</div><span class="mk">§CHAP{i+1:02d}§</span></div>{c[2]}</section>' for i, c in enumerate(chapters))
    qk = ''
    if quick:
        qk = ('<section class="quick"><div class="tochead"><div class="toch">Prise en main rapide</div><small>L\'essentiel en 4 étapes</small></div><div class="qgrid">'
              + ''.join(f'<div class="qc"><div class="qn">{k+1:02d}</div><b>{t}</b><p>{d}</p></div>' for k, (t, d) in enumerate(quick)) + '</div>'
              + (('<div class="qshot">' + desk(shots[0][0], 'Votre écran d\'accueil', small=True) + '</div>') if shots and shots[0][0][0] in 'gp'
                 else ('<div class="qshot ph2">' + ''.join(phone(n, c) for n, c in ((shots[0][0], 'La tournée'), (shots[1][0], 'La fiche d\'un matériel'))) + '</div>') if shots else '')
              + '</section>')
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>@page{{size:A4;margin:22mm 17mm 20mm}}{CSS}</style></head><body>
<div class="tochead"><div class="toch">Sommaire</div><small>{label}</small></div>{intro_html}<div class="toc">{toc}</div>{qk}{chs}</body></html>'''

def render(cover_html, body_fn, chapters, intro, footer_label, out, quick=None, shots=()):
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, 'c.html'), 'w').write(cover_html)
    open(os.path.join(tmp, 'k.html'), 'w').write(backcover(footer_label))
    js = os.path.join(tmp, 'r.js')
    st = 'font-family:Helvetica,Arial,sans-serif;-webkit-print-color-adjust:exact;'
    header = (f'<div style="{st}width:100%;margin:0 17mm;font-size:7.4pt;color:#5B7078;display:flex;align-items:center;justify-content:space-between;border-bottom:.3mm solid #D9E4E6;padding-bottom:2.2mm">'
              f'<span><b style="color:#0B5361">Mana</b><b style="color:#0E8F93">Process</b>&nbsp;&nbsp;·&nbsp;&nbsp;{footer_label.split(" · ")[-1]}</span><span>Guide d\'utilisation · Édition {DATE}</span></div>')
    footer = (f'<div style="{st}width:100%;margin:0 17mm;font-size:7.4pt;color:#5B7078;display:flex;align-items:center;justify-content:space-between">'
              '<span>MédiParc NFC · manaprocess.cloud/materiel</span>'
              '<span style="background:#0B5361;color:#fff;font-weight:700;border-radius:8px;padding:2px 9px"><span class="pageNumber"></span></span></div>')
    open(js, 'w').write("""const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const [kind,src,dst,head,foot]=process.argv.slice(2);
const p=await b.newPage();await p.goto('file://'+src,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
const o={path:dst,format:'A4',printBackground:true,preferCSSPageSize:true};
if(kind==='body')Object.assign(o,{displayHeaderFooter:true,headerTemplate:head,footerTemplate:foot,margin:{top:'22mm',bottom:'20mm',left:'17mm',right:'17mm'}});
await p.pdf(o);await b.close();})();""")
    def run(kind, src, pdf):
        subprocess.run(['node', js, kind, os.path.join(tmp, src), pdf, header, footer], check=True, cwd=tmp)
    run('cover', 'c.html', os.path.join(tmp, 'cover.pdf'))
    run('cover', 'k.html', os.path.join(tmp, 'back.pdf'))
    open(os.path.join(tmp, 'b.html'), 'w').write(body_fn(chapters, intro, None, quick, footer_label, shots))
    run('body', 'b.html', os.path.join(tmp, 'body.pdf'))
    import pypdf
    r = pypdf.PdfReader(os.path.join(tmp, 'body.pdf')); pages = {}
    for i, pg in enumerate(r.pages):
        for m in re.findall(r'§CHAP(\d\d)§', pg.extract_text() or ''): pages.setdefault(int(m), i + 1)
    open(os.path.join(tmp, 'b.html'), 'w').write(body_fn(chapters, intro, pages, quick, footer_label, shots))
    run('body', 'b.html', os.path.join(tmp, 'body.pdf'))
    w = pypdf.PdfWriter()
    for f in ('cover.pdf', 'body.pdf', 'back.pdf'):
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
    render(cover(*c['cover'], learn=c.get('quick', ()), chips=c.get('chips', ())), body, c['chapters'], c['intro'], c['footer'], os.path.join(OUT, c['file']), c.get('quick'), c['cover'][4])
