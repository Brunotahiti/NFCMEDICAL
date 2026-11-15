#!/usr/bin/env python3
"""Maquettes des écrans de l'application iPhone « Tahiti Parc NFC » (reprennent la mise en page SwiftUI).
Usage : python3 maquettes.py <dossier html>, puis node rendu.js <dossier html> <dossier des captures>."""
import sys, os
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PH = 'file://' + os.path.join(ROOT, 'photos') + '/'
I = {  # icônes au trait (24 × 24)
 'house': '<path d="M4 11.5 12 4l8 7.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z"/>',
 'grid': '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
 'wave': '<path d="M8 8.5a5 5 0 0 1 0 7M11.5 6a8.5 8.5 0 0 1 0 12M15 3.5a12 12 0 0 1 0 17"/>',
 'cal': '<rect x="4" y="5.5" width="16" height="14.5" rx="2.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
 'dots': '<circle cx="12" cy="12" r="9"/><circle cx="8" cy="12" r=".8" fill="currentColor"/><circle cx="12" cy="12" r=".8" fill="currentColor"/><circle cx="16" cy="12" r=".8" fill="currentColor"/>',
 'doc': '<path d="M7 3.5h7l4 4V20a.5.5 0 0 1-.5.5h-10.5A.5.5 0 0 1 6.5 20V4a.5.5 0 0 1 .5-.5zM14 3.5V8h4M9.5 12h5M9.5 15.5h5"/>',
 'chev': '<path d="m9 6 6 6-6 6"/>', 'back': '<path d="m15 5-7 7 7 7"/>',
 'check': '<path d="m5 12.5 4.5 4.5L19 7.5"/>', 'ret': '<path d="M9 7 4.5 11.5 9 16M5 11.5h9a5 5 0 0 1 0 10h-2"/>',
 'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>', 'warn': '<path d="M12 4 2.8 19.5h18.4Z"/><path d="M12 10v4.5M12 17.2v.1"/>',
 'drop': '<path d="M12 3.5s6 6.7 6 10.7a6 6 0 0 1-12 0c0-4 6-10.7 6-10.7z"/>', 'tool': '<path d="M14.5 6.5a4 4 0 0 0 5 5L11 20a2.1 2.1 0 0 1-3-3l8.5-8.5zM14.5 6.5l3-3"/>',
 'camera': '<path d="M4 8.5h3l1.6-2.5h6.8L17 8.5h3v10.5H4z"/><circle cx="12" cy="13.5" r="3.4"/>', 'pin': '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
 'phone': '<path d="M6.5 4h3l1.5 4-2 1.5a10 10 0 0 0 5.5 5.5l1.5-2 4 1.5v3A2 2 0 0 1 18 19.5 15.5 15.5 0 0 1 4.5 6 2 2 0 0 1 6.5 4z"/>',
 'tray': '<path d="M4 13.5 6.5 5h11l2.5 8.5V19H4zM4 13.5h4.5a3.5 3.5 0 0 0 7 0H20"/>', 'map': '<path d="M9 4.5 3.5 6.5v13L9 17.5l6 2 5.5-2v-13L15 6.5 9 4.5zM9 4.5v13M15 6.5v13"/>',
 'cross': '<path d="M9.5 4h5v5.5H20v5h-5.5V20h-5v-5.5H4v-5h5.5z"/>', 'key': '<circle cx="8" cy="15" r="4"/><path d="m11 12 8-8M16 7l2 2"/>',
 'book': '<path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5zM5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3"/>', 'lock': '<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/>',
 'plus': '<path d="M12 5v14M5 12h14"/>', 'cal+': '<rect x="4" y="5.5" width="16" height="14.5" rx="2.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4M12 12.5v5M9.5 15h5"/>',
 'scan': '<path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5a1.5 1.5 0 0 1-1.5 1.5H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16"/><path d="M8 12h8"/>',
 'search': '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/>', 'share': '<path d="M12 3.5v11M8 7.5l4-4 4 4M6 11v8.5h12V11"/>', 'link': '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 'pencil': '<path d="M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4"/>', 'folder': '<path d="M3.5 6.5h6l2 2h9v10.5h-17z"/>',
}
def ic(k, c='currentColor', s=20, w=1.9): return f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round">{I[k]}</svg>'

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:390px;height:844px;overflow:hidden;font-family:Inter,-apple-system,"Helvetica Neue",Arial,sans-serif;color:#0D2730;background:#EDF6F8;font-size:15px;-webkit-font-smoothing:antialiased;position:relative}
.sb{height:47px;display:flex;justify-content:space-between;align-items:center;padding:14px 30px 0 34px;font-weight:600;font-size:16px}
.sb .r{display:flex;gap:6px;align-items:center}.sb .bat{width:25px;height:12px;border:1.5px solid currentColor;border-radius:4px;position:relative;opacity:.9}.sb .bat::after{content:"";position:absolute;inset:1.5px;right:5px;background:currentColor;border-radius:1.5px}
.dark .sb{color:#fff}
.nav{height:44px;display:flex;align-items:center;justify-content:center;position:relative;font-weight:600;font-size:17px}
.nav .l{position:absolute;left:12px;color:#0A7C88;display:flex;align-items:center;gap:2px;font-weight:400}
.nav .rt{position:absolute;right:16px;color:#0A7C88;font-weight:600}
.big{font-size:34px;font-weight:700;letter-spacing:-.6px;padding:2px 20px 8px}
.content{padding:0 16px}
.card{background:#fff;border-radius:18px;padding:16px;margin-bottom:14px}
.hero{border-radius:24px;padding:18px;color:#fff;background:linear-gradient(135deg,#0B5361,#0E8F93);margin-bottom:16px}
.muted{color:#5B7078}.small{font-size:13px}.cap{font-size:12px}
.row{display:flex;align-items:center;gap:12px}
.list{background:#fff;border-radius:12px;overflow:hidden;margin:0 16px 22px}
.li{display:flex;align-items:center;gap:12px;padding:11px 16px;min-height:44px;position:relative}
.li+.li::before{content:"";position:absolute;left:16px;right:0;top:0;height:.5px;background:#C8D3D6}
.li.ind+.li.ind::before{left:66px}
.sh{font-size:13px;color:#6B7F86;text-transform:uppercase;padding:0 32px 7px;letter-spacing:.2px}
.sf{font-size:12.5px;color:#6B7F86;padding:-6px 32px 0;margin:-16px 32px 22px;line-height:1.35}
.tag{font-size:11px;font-weight:700;padding:3px 8px;border-radius:99px;white-space:nowrap}
.ok{color:#1A7F54;background:rgba(26,127,84,.13)}.wa{color:#A65F00;background:rgba(166,95,0,.13)}.cr{color:#B8352B;background:rgba(184,53,43,.13)}.in{color:#3154C4;background:rgba(49,84,196,.13)}
.thumb{width:48px;height:48px;border-radius:11px;object-fit:cover;background:#EDF6F8;flex:none}
.tabbar{position:absolute;left:0;right:0;bottom:0;height:83px;background:rgba(249,251,251,.94);border-top:.5px solid #C8D3D6;display:flex;justify-content:space-around;padding-top:7px}
.tab{display:flex;flex-direction:column;align-items:center;gap:2px;font-size:10px;font-weight:500;color:#8A9A9F;width:70px}
.tab.on{color:#0A7C88}
.home{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);width:134px;height:5px;border-radius:3px;background:#0D2730}
.dark .home{background:#fff}
.btn{display:flex;align-items:center;justify-content:center;gap:8px;height:50px;border-radius:14px;font-weight:600}
.act{display:flex;align-items:center;gap:10px;padding:12px;border-radius:12px;font-weight:600;margin-top:8px}
.seg{display:flex;background:#E3E8EA;border-radius:9px;padding:2px;margin:0 16px 16px}
.seg span{flex:1;text-align:center;font-size:13px;font-weight:500;padding:6px 0;border-radius:7px}
.seg span.on{background:#fff;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.kv{display:flex;justify-content:space-between;gap:12px;padding:5px 0;font-size:14px}.kv span:first-child{color:#5B7078}.kv span:last-child{font-weight:500;text-align:right}
.sheet{position:absolute;left:0;right:0;bottom:0;background:#F2F2F7;border-radius:12px 12px 0 0}
.dim{position:absolute;inset:0;background:rgba(0,0,0,.35)}
.field{background:#fff;border-radius:10px;padding:12px 14px;margin:0 16px 10px;font-size:16px}
"""
SB = '<div class="sb"><span>9:41</span><span class="r"><svg width="18" height="12" viewBox="0 0 18 12"><rect x="0" y="8" width="3" height="4" rx="1" fill="currentColor"/><rect x="5" y="5.5" width="3" height="6.5" rx="1" fill="currentColor"/><rect x="10" y="3" width="3" height="9" rx="1" fill="currentColor"/><rect x="15" y="0" width="3" height="12" rx="1" fill="currentColor"/></svg><span class="bat"></span></span></div>'
def tabbar(on, staff=True):
    tabs = [('house', 'Accueil'), ('grid', 'Parc') if staff else ('cal', 'Locations'), ('wave', 'Scanner'), ('cal', 'Locations') if staff else ('doc', 'Facturation'), ('dots', 'Plus')]
    return '<div class="tabbar">' + ''.join(f'<div class="tab{" on" if t == on else ""}">{ic(i, s=25, w=1.8)}<span>{t}</span></div>' for i, t in tabs) + '</div>'
def page(name, body, dark=False, bg=None):
    st = f' style="background:{bg}"' if bg else ''
    open(os.path.join(OUT, name + '.html'), 'w').write(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head><body class="{"dark" if dark else ""}"{st}>{SB}{body}<div class="home"></div></body></html>')
def tag(t, c): return f'<span class="tag {c}">{t}</span>'
def li(left, title, sub='', right='', chev=True, cls='ind'):
    return (f'<div class="li {cls}">{left}<div style="flex:1;min-width:0"><div style="font-weight:600;font-size:15px">{title}</div>'
            + (f'<div class="muted cap" style="margin-top:2px">{sub}</div>' if sub else '') + f'</div>{right}' + (ic('chev', '#B4C0C4', 16, 2.4) if chev else '') + '</div>')
def tile(k, c): return f'<span style="width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:{c}22;flex:none">{ic(k, c, 19, 2)}</span>'
def img(n): return f'<img class="thumb" src="{PH}{n}.jpg">'
LOGO = ('<div style="display:flex;flex-direction:column;align-items:center;gap:14px"><div style="width:96px;height:96px;border-radius:24px;background:rgba(255,255,255,.14);display:grid;place-items:center">'
        + ic('wave', '#62CFC4', 50, 2.2) + '</div><div style="font-size:26px;font-weight:800"><span style="color:#62CFC4">Tahiti </span>Parc NFC</div></div>')

# 1. Connexion
page('i_login', '<div style="padding:70px 28px 0;color:#fff;text-align:center">' + LOGO
     + '<div style="margin:18px 0 30px;color:rgba(255,255,255,.8);font-size:15px">Gestion du parc de matériel médical en location</div>'
     + '<div style="background:#fff;border-radius:14px;height:52px;margin-bottom:12px;color:#0D2730;text-align:left;padding:15px 16px">lagon</div>'
     + '<div style="background:#fff;border-radius:14px;height:52px;margin-bottom:18px;color:#0D2730;text-align:left;padding:15px 16px;letter-spacing:3px">••••••••••••</div>'
     + '<div class="btn" style="background:#62CFC4;color:#0B5361">Se connecter</div>'
     + '<div style="margin-top:26px;font-size:13px;color:rgba(255,255,255,.75)">' + ic('lock', 'currentColor', 15) + ' Aucune ordonnance n\'est stockée en ligne.<br>Les comptes sont créés par l\'administrateur du parc.</div></div>',
     dark=True, bg='linear-gradient(160deg,#0B5361,#0E8F93)')

# 2. Accueil grossiste
states = [('cal', 'En location', 13, '#3154C4'), ('check', 'Disponible', 6, '#1A7F54'), ('drop', 'Désinfection', 3, '#A65F00'), ('tool', 'Maintenance', 2, '#B8352B')]
page('i_home_g', '<div class="nav">Accueil</div><div class="content">'
     + '<div class="hero"><div class="row" style="justify-content:space-between"><div><div style="font-size:22px;font-weight:700">Bonjour Teiki</div><div style="font-size:13px;opacity:.75">Équipe du parc · 15 novembre 2026</div></div>' + ic('wave', '#62CFC4', 34, 2.4) + '</div>'
     + '<div style="display:flex;align-items:baseline;gap:8px;margin-top:12px"><b style="font-size:42px">54 %</b><span style="opacity:.8">du parc en location</span></div>'
     + '<div style="height:5px;border-radius:3px;background:rgba(255,255,255,.25);margin:8px 0 12px"><div style="width:54%;height:100%;background:#62CFC4;border-radius:3px"></div></div>'
     + '<div class="row" style="justify-content:space-between"><div><b>24</b><div class="cap" style="opacity:.7">équipements</div></div><div style="text-align:right"><b>61 929 F</b><div class="cap" style="opacity:.7">par mois (estimé)</div></div></div></div>'
     + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px">' + ''.join(f'<div class="card" style="margin:0;padding:14px">{ic(k, c, 22)}<div style="font-size:26px;font-weight:700;margin-top:6px">{n}</div><div class="muted small">{t}</div></div>' for k, t, n, c in states) + '</div>'
     + '<div class="row" style="justify-content:space-between;margin-bottom:10px"><div class="row" style="gap:8px"><b style="font-size:20px">Demandes des pharmacies</b><span class="tag" style="background:#B8352B;color:#fff">3</span></div><span style="color:#0A7C88;font-weight:600;font-size:14px">Tout voir</span></div>'
     + '<div class="card" style="padding:4px 0">' + li(tile('cal+', '#1A7F54'), 'Location · Lit X5', 'Pharmacie du Lagon · Hinano Teriitahi (Arue)', tag('Nouvelle', 'wa'), False)
     + li(tile('warn', '#B8352B'), 'Problème · Porte sérum', 'Pharmacie du Lagon · Lucie Bernard · PSR-0104', tag('Nouvelle', 'wa'), False) + '</div></div>' + tabbar('Accueil'))

# 3. Accueil pharmacie
kinds = [('cal+', 'Location', 'Demander du matériel', '#1A7F54'), ('ret', 'Reprise', 'Faire reprendre un équipement', '#3154C4'), ('clock', 'Prolongation', 'Prolonger une location', '#A65F00'), ('warn', 'Problème', 'Signaler un souci sur un matériel', '#B8352B')]
page('i_home_p', '<div class="nav">Accueil</div><div class="content">'
     + '<div class="hero" style="padding:16px 18px"><div style="font-size:22px;font-weight:700">Bonjour Pharmacie</div><div style="font-size:13px;opacity:.75">Pharmacie du Lagon · 15 novembre 2026</div>'
     + '<div style="display:flex;align-items:baseline;gap:8px;margin-top:10px"><b style="font-size:40px">7</b><span style="opacity:.8">locations en cours</span></div><div><b>2</b> <span class="cap" style="opacity:.75">ordonnances à vérifier</span></div></div>'
     + '<div class="row" style="justify-content:space-between;margin-bottom:10px"><b style="font-size:20px">Nouvelle demande</b><span style="color:#0A7C88;font-weight:600;font-size:14px">Catalogue</span></div>'
     + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px">' + ''.join(f'<div class="card" style="margin:0;padding:12px;min-height:116px">{tile(k, c)}<div style="font-weight:700;margin-top:6px">{t}</div><div class="muted cap">{d}</div></div>' for k, t, d, c in kinds) + '</div>'
     + '<div class="row" style="justify-content:space-between;margin-bottom:8px"><b style="font-size:17px">Mes demandes en cours</b><span style="color:#0A7C88;font-weight:600;font-size:14px">Tout voir</span></div>'
     + '<div class="card" style="padding:4px 0">' + li(tile('cal+', '#1A7F54'), 'Location · Lit X5', 'Hinano Teriitahi (Arue) · passage le 16/11/2026', tag('Planifiée', 'in'), False) + '</div></div>' + tabbar('Accueil', False))

# 4. Scanner
page('i_scan', '<div class="nav">Scanner</div><div class="content" style="text-align:center">'
     + '<div style="margin:40px auto 24px;width:250px;height:250px;border-radius:50%;border:10px solid rgba(98,207,196,.35);display:grid;place-items:center"><div style="width:210px;height:210px;border-radius:50%;background:linear-gradient(135deg,#0B5361,#0E8F93);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#fff">'
     + ic('wave', '#62CFC4', 66, 2.2) + '<b style="font-size:17px">Scanner une puce</b></div></div>'
     + '<p class="muted" style="padding:0 18px;line-height:1.45">Approchez le haut de l\'iPhone de l\'étiquette du matériel. Le passage est enregistré avec votre position.</p>'
     + '<div class="card" style="text-align:left;margin-top:26px"><b style="font-size:17px">Saisie manuelle</b><div class="row" style="margin-top:10px"><div style="flex:1;border-radius:9px;background:#EDF6F8;padding:10px 12px;color:#8A9A9F">Référence (ex. LIT-0001)</div><span class="btn" style="height:38px;padding:0 14px;background:#0A7C88;color:#fff;border-radius:9px">Ouvrir</span></div></div></div>' + tabbar('Scanner'))

# 5. Fenêtre NFC du système
page('i_nfc', '<div class="nav">Scanner</div><div class="dim"></div><div class="sheet" style="background:#fff;margin:0 8px 10px;border-radius:38px;height:390px;text-align:center;padding-top:30px">'
     + '<div style="font-size:24px;font-weight:600;color:#8A8A8E">Prêt à scanner</div>'
     + '<div style="margin:34px auto 26px;width:120px;height:120px;border-radius:50%;border:5px solid #0A84FF;display:grid;place-items:center">' + ic('phone', '#0A84FF', 52, 2) + '</div>'
     + '<div style="font-size:17px;padding:0 40px;line-height:1.35">Approchez le haut de l\'iPhone de l\'étiquette NFC du matériel.</div>'
     + '<div style="margin:30px 24px 0;background:#E5E5EA;border-radius:14px;height:54px;display:grid;place-items:center;font-size:18px;font-weight:600">Annuler</div></div>')

# 6. Fiche équipement (location)
page('i_fiche', '<div class="nav"><span class="l">' + ic('back', '#0A7C88', 22, 2.4) + 'Accueil</span>LIT-0101</div><div class="content">'
     + '<div class="card"><div class="row"><img class="thumb" style="width:84px;height:84px;border-radius:18px" src="' + PH + 'lit.jpg"><div><div style="font-size:20px;font-weight:700">Lit Mantovani</div><div class="muted small">Thuasne · lit</div><div style="color:#0A7C88;font:600 12px monospace;margin:3px 0">LIT-0101</div>' + tag('En location', 'in') + '</div></div>'
     + '<div style="height:.5px;background:#D5DFE1;margin:12px 0 8px"></div><div class="kv"><span>Tarif</span><span>1 700 F / semaine</span></div><div class="kv"><span>Prochain contrôle</span><span>18/01/2027</span></div></div>'
     + '<div class="card"><b style="font-size:17px">' + ic('cal', '#0D2730', 18) + ' Location en cours</b><div class="row" style="margin:12px 0"><span style="width:42px;height:42px;border-radius:50%;background:#3154C4;color:#fff;display:grid;place-items:center;font-weight:700">JM</span><div style="flex:1"><b>Jeanne Morel</b><div class="muted cap">PK 12 côté mer, Punaauia</div></div><span style="width:38px;height:38px;border-radius:50%;background:rgba(26,127,84,.15);display:grid;place-items:center">' + ic('phone', '#1A7F54', 18) + '</span></div>'
     + '<div class="kv"><span>Pharmacie</span><span>Pharmacie du Lagon</span></div><div class="kv"><span>Début</span><span>08/10/2026 · depuis 5 sem.</span></div><div class="kv"><span>Fin prévue</span><span>07/12/2026 · reste 3 sem.</span></div>'
     + '<div style="height:5px;border-radius:3px;background:#E3E8EA;margin-top:8px"><div style="width:62%;height:100%;border-radius:3px;background:#0A7C88"></div></div></div>'
     + '<div class="card"><b style="font-size:17px">' + ic('clock', '#0D2730', 18) + ' Actions</b>'
     + '<div class="act" style="color:#0A7C88;background:rgba(10,124,136,.1)">' + ic('cal+', '#0A7C88', 20) + 'Prolonger la location</div>'
     + '<div class="act" style="color:#3154C4;background:rgba(49,84,196,.1)">' + ic('ret', '#3154C4', 20) + 'Retour du matériel</div>'
     + '<div class="act" style="color:#B8352B;background:rgba(184,53,43,.1)">' + ic('warn', '#B8352B', 20) + 'Signaler une panne</div></div></div>' + tabbar('Accueil'))

# 7. Photo horodatée
page('i_photo', '<div class="nav"><span class="l" style="font-weight:400">Annuler</span>Photo · LIT-0101<span class="rt">Envoyer</span></div>'
     + '<div class="sh" style="margin-top:14px">Type de photo</div><div class="seg"><span class="on">Livraison</span><span>Retour</span><span>État</span><span>Panne</span></div>'
     + '<div class="list" style="padding:12px"><div style="position:relative;border-radius:10px;overflow:hidden"><img src="' + PH + 'lit.jpg" style="width:100%;height:250px;object-fit:cover;display:block">'
     + '<div style="position:absolute;left:0;right:0;bottom:0;background:rgba(0,0,0,.55);color:#fff;font-size:11px;font-weight:600;padding:8px 10px">LIT-0101 · Livraison · 15/11/2026 09:12 · -17.53520, -149.56940 (±6 m)</div></div>'
     + '<div style="color:#0A7C88;padding:12px 4px 2px">Reprendre la photo</div></div>'
     + '<div class="sf" style="margin-top:-12px">La date, l\'heure et la position sont incrustées sur la photo.</div>')

# 8. Ordonnance
page('i_ordo', '<div class="nav"><span class="l">' + ic('back', '#0A7C88', 22, 2.4) + 'LIT-0101</span>Ordonnance</div><div class="content" style="padding-top:8px">'
     + '<div class="card"><b style="font-size:17px">' + ic('doc', '#0D2730', 18) + ' Ordonnance</b>'
     + '<div class="row" style="align-items:flex-start;gap:10px;background:rgba(10,124,136,.08);border-radius:12px;padding:10px;margin:10px 0">' + ic('lock', '#0A7C88', 20) + '<span class="cap">Aucune ordonnance n\'est stockée en ligne. Les ordonnances restent sur le serveur de votre pharmacie : l\'application les y enregistre et les y relit.</span></div>'
     + '<div class="row" style="align-items:flex-start">' + ic('check', '#1A7F54', 22, 2.6) + '<div><b class="small">Vérifiée par Pharmacie du Lagon le 15/11/2026</b><div class="muted cap">Ordonnance du 15/11/2026, valable jusqu\'au 15/05/2027 · n° ORD-2026-118</div></div></div>'
     + '<div class="row" style="margin-top:12px"><div class="btn" style="flex:1;height:42px;background:rgba(10,124,136,.12);color:#0A7C88;font-size:14px">' + ic('scan', '#0A7C88', 18) + 'Scanner / voir</div><div class="btn" style="flex:1;height:42px;background:#0A7C88;color:#fff;font-size:14px">' + ic('check', '#fff', 18, 2.4) + 'Nouvelle</div></div></div>'
     + '<div class="sh" style="padding-left:16px;margin-top:14px">Enregistrer une ordonnance</div><div class="list" style="margin:0 0 16px">' + li(ic('scan', '#0A7C88', 22), '<span style="color:#0A7C88;font-weight:400">Scanner l\'ordonnance</span>', chev=False, cls='') + li(ic('share', '#0A7C88', 22), '<span style="color:#0A7C88;font-weight:400">Importer un fichier (photo, PDF, HEIC…)</span>', chev=False, cls='') + '</div>'
     + '<div class="sh" style="padding-left:16px">Consulter</div><div class="list" style="margin:0">' + li(ic('folder', '#0A7C88', 22), '<span style="color:#0A7C88;font-weight:400">Voir l\'ordonnance sur le serveur de la pharmacie</span>', chev=False, cls='') + '</div></div>')

# 9. Demande de location
page('i_req_loc', '<div class="nav"><span class="l" style="font-weight:400">Annuler</span>Demande de location<span class="rt">Envoyer</span></div><div style="height:12px"></div>'
     + '<div class="sh">Matériel</div><div class="list">' + li('', '<span style="font-weight:400">Produit</span>', right='<span class="muted">Lit X5</span>', cls='') + li('', '<span style="font-weight:400">Tarif</span>', right='<span class="muted">1 900 F / semaine</span>', chev=False, cls='') + '</div>'
     + '<div class="sh">Bénéficiaire</div><div class="list">' + li('', '<span style="font-weight:400">Bénéficiaire</span>', right='<span class="muted">Hinano Teriitahi · Arue</span>', cls='') + li(ic('plus', '#0A7C88', 20), '<span style="color:#0A7C88;font-weight:400">Nouveau bénéficiaire</span>', chev=False, cls='') + '</div>'
     + '<div class="sh">Durée et date</div><div class="list" style="padding:10px 0 2px"><div class="seg" style="margin:0 16px 8px"><span>1 sem.</span><span>2 sem.</span><span>4 sem.</span><span class="on">3 mois</span></div>' + li('', '<span style="font-weight:400">Livraison souhaitée</span>', right='<span style="background:#E3E8EA;border-radius:7px;padding:5px 10px">16 nov. 2026</span>', chev=False, cls='') + '</div>'
     + '<div class="sh">Précisions (facultatif)</div><div class="list"><div class="li">Appeler la fille du bénéficiaire avant de passer. Portail vert.</div></div>'
     + '<div class="sf">Aucune information médicale : ni pathologie, ni ordonnance. L\'ordonnance reste dans votre pharmacie.</div>')

# 10. Demande côté grossiste
page('i_req_g', '<div class="nav">Location<span class="rt">Fermer</span></div><div style="height:10px"></div>'
     + '<div class="list"><div class="li">' + ic('cal+', '#1A7F54', 20) + '<b style="flex:1">Location · Lit X5</b>' + tag('Nouvelle', 'wa') + '</div>'
     + ''.join(f'<div class="li"><span style="flex:1">{a}</span><span class="muted" style="text-align:right">{b}</span></div>' for a, b in [('Pharmacie', 'Pharmacie du Lagon'), ('Bénéficiaire', 'Hinano Teriitahi · Arue'), ('Téléphone', '<span style="color:#0A7C88">87 99 88 77</span>'), ('Durée', '13 semaines'), ('Souhaitée le', '16/11/2026')]) + '</div>'
     + '<div class="sh">Traitement</div><div class="list"><div class="li"><span style="flex:1">Date de passage</span><span style="background:#E3E8EA;border-radius:7px;padding:5px 10px">16 nov. 2026</span></div><div class="li muted">Message à la pharmacie…</div><div class="li" style="color:#0A7C88">' + ic('cal', '#0A7C88', 20) + 'Planifier le passage</div></div>'
     + '<div class="sh">Livrer · 2 disponibles</div><div class="list">' + li(img('lit'), 'Lit X5', 'LIT-0108', tag('Livrer', 'ok'), False) + li(img('lit'), 'Lit X5', 'LIT-0112', tag('Livrer', 'ok'), False) + '</div>'
     + '<div class="list"><div class="li" style="color:#FF3B30;justify-content:center">Refuser la demande</div></div>')

# 11. Locations › Planning
plan = [('Aujourd\'hui · 2', [('ret', 'Fin de location · Paea', 'Concentrateur O2 · OXY-0121 · Lucie Bernard', '')]), ('Demain · 3', [('cal+', 'Livraison · Arue', 'Lit X5 · Hinano Teriitahi · Pharmacie du Lagon', tag('À planifier', 'wa')), ('ret', 'Reprise · Paea', 'Porte sérum · PSR-0104 · Lucie Bernard', ''), ('cal+', 'Livraison · Taravao', 'Rollator 4 roues · Henri Girard', '')])]
page('i_plan', '<div class="nav"></div><div class="big">Locations</div><div class="seg"><span>En cours</span><span>Demandes 4</span><span class="on">Planning</span><span>Terminées</span></div>'
     + ''.join(f'<div class="sh">{h}</div><div class="list">' + ''.join(li(ic(k, '#0A7C88', 22), t, s, r, False, '') for k, t, s, r in rows) + '</div>' for h, rows in plan) + tabbar('Locations'))

# 12. Plus
page('i_more', '<div class="nav"></div><div class="big">Plus</div>'
     + '<div class="list"><div class="li"><span style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#0B5361,#0E8F93);color:#fff;display:grid;place-items:center;font-weight:700">TT</span><div><b>Teiki Teriierooiterai</b><div class="muted small">Équipe du parc</div></div></div>' + li(ic('key', '#0A7C88', 20), '<span style="color:#0A7C88;font-weight:400">Changer de mot de passe</span>', chev=False, cls='') + '</div>'
     + '<div class="sh">Gestion</div><div class="list">' + ''.join(li(ic(k, '#0A7C88', 20), f'<span style="font-weight:400">{t}</span>', right=r, cls='') for k, t, r in [('tray', 'Demandes des pharmacies', '<span class="tag" style="background:#B8352B;color:#fff">2</span>'), ('map', 'Planning des tournées', ''), ('cross', 'Suivi des pharmacies', ''), ('grid', 'Catalogue et disponibilités', ''), ('doc', 'Facturation', ''), ('tool', 'Entretien et contrôles', '')]) + '</div>'
     + '<div class="sh">Guides d\'utilisation</div><div class="list">' + ''.join(li(ic('book', '#0A7C88', 20), f'<span style="color:#0A7C88;font-weight:400">{t}</span>', chev=False, cls='') for t in ['Guide du technicien', 'Guide du grossiste', 'Guide de l\'application iPhone']) + '</div>' + tabbar('Plus'))

# 13. Programmer une étiquette
page('i_tag', '<div class="nav"><span class="l">' + ic('back', '#0A7C88', 22, 2.4) + 'Parc</span>LIT-0112</div><div class="content" style="padding-top:8px">'
     + '<div class="card"><b style="font-size:17px">' + ic('wave', '#0D2730', 18) + ' Puce NFC</b><div class="kv" style="margin:8px 0"><span>Lien</span><span>Aucune puce associée</span></div>'
     + '<div class="act" style="color:#0A7C88;background:rgba(10,124,136,.1)">' + ic('pencil', '#0A7C88', 20) + 'Programmer une puce vierge</div>'
     + '<div class="act" style="color:#3154C4;background:rgba(49,84,196,.1)">' + ic('link', '#3154C4', 20) + 'Associer une puce déjà programmée</div></div></div>'
     + '<div class="dim"></div><div class="sheet" style="background:#fff;margin:0 8px 10px;border-radius:38px;height:360px;text-align:center;padding-top:30px">'
     + '<div style="font-size:24px;font-weight:600;color:#8A8A8E">Prêt à scanner</div><div style="margin:30px auto 22px;width:110px;height:110px;border-radius:50%;border:5px solid #0A84FF;display:grid;place-items:center">' + ic('phone', '#0A84FF', 48, 2) + '</div>'
     + '<div style="font-size:17px;padding:0 40px">Approchez l\'iPhone de la puce à programmer.</div><div style="margin:26px 24px 0;background:#E5E5EA;border-radius:14px;height:54px;display:grid;place-items:center;font-size:18px;font-weight:600">Annuler</div></div>')

# 14. Fiche matériel côté pharmacie : demandes
page('i_fiche_p', '<div class="nav"><span class="l">' + ic('back', '#0A7C88', 22, 2.4) + 'Locations</span>TNS-0115</div><div class="content">'
     + '<div class="card"><div class="row"><img class="thumb" style="width:70px;height:70px;border-radius:16px" src="' + PH + 'tens.jpg"><div><div style="font-size:19px;font-weight:700">Tens Eco 2</div><div class="muted small">Appareils électroniques</div>' + tag('En location', 'in') + '</div></div></div>'
     + '<div class="card"><b style="font-size:17px">' + ic('tray', '#0D2730', 18) + ' Demandes en cours</b><div style="margin-top:6px">' + li(tile('clock', '#A65F00'), 'Prolongation · Tens Eco 2', 'André Lefèvre (Mahina) · + 4 semaines', tag('Nouvelle', 'wa'), False, '') + '</div></div>'
     + '<div class="card"><b style="font-size:17px">' + ic('share', '#0D2730', 18) + ' Une demande au parc</b>'
     + '<div class="act" style="color:#3154C4;background:rgba(49,84,196,.1)">' + ic('ret', '#3154C4', 20) + 'Demander la reprise</div>'
     + '<div class="act" style="color:#B8352B;background:rgba(184,53,43,.1)">' + ic('warn', '#B8352B', 20) + 'Signaler un problème</div></div></div>' + tabbar('Locations', False))
print('maquettes :', len([f for f in os.listdir(OUT) if f.endswith('.html')]))
