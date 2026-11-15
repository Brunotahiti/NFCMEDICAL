// Captures d'écran des trois guides.
// Serveur de démonstration neuf : DATA_DIR=<dossier vide> ADMIN_PASSWORD=Provisoire2026 COOKIE_SECURE=0 PORT=3456 node server/server.js
// Usage : node capture.js <dossier des captures> <photo de lit.jpg> <photo d'ordonnance.jpg>
const { chromium } = require('playwright');
const B = 'http://localhost:3456/materiel/';
const O = process.argv[2].replace(/\/?$/, '/'), LIT = process.argv[3], ORDO = process.argv[4];
const errs = [];

(async () => {
  const b = await chromium.launch();
  const mk = async (desk) => {
    const c = await b.newContext(desk
      ? { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5, locale: 'fr-FR', timezoneId: 'Pacific/Tahiti', geolocation: { latitude: -17.5352, longitude: -149.5694, accuracy: 12 }, permissions: ['geolocation'] }
      : { viewport: { width: 430, height: 932 }, deviceScaleFactor: 2, locale: 'fr-FR', timezoneId: 'Pacific/Tahiti', geolocation: { latitude: -17.5352, longitude: -149.5694, accuracy: 6 }, permissions: ['geolocation'] });
    const p = await c.newPage();
    p.on('pageerror', e => errs.push(e.message));
    await p.addInitScript(() => {
      document.addEventListener('DOMContentLoaded', () => { const st = document.createElement('style'); st.textContent = '.toast{display:none!important}'; document.head.appendChild(st); });
      /* Dossier « serveur de la pharmacie » simulé (File System Access). */
      window.__files = {};
      const fh = n => ({ kind: 'file', name: n, getFile: async () => new File([window.__files[n]], n, { type: 'application/pdf', lastModified: Date.now() }) });
      const dir = { name: 'Ordonnances', queryPermission: async () => 'granted', requestPermission: async () => 'granted',
        values: function () { const ks = Object.keys(window.__files); let i = 0; return { next: async () => i < ks.length ? { done: false, value: fh(ks[i++]) } : { done: true } }; },
        getFileHandle: async (n, o) => { if (!(o && o.create) && !(n in window.__files)) throw new DOMException('x', 'NotFoundError'); return { createWritable: async () => ({ write: async bl => { window.__files[n] = bl; }, close: async () => {} }) }; } };
      window.showDirectoryPicker = async () => dir;
      /* Web NFC simulé (Chrome Android) pour illustrer la lecture et l'écriture. */
      window.__nfc = []; window.NDEFReader = class { constructor() { window.__nfc.push(this); } scan(o) { return Promise.resolve(); }
        write(m, o) { return new Promise((res, rej) => { window.__writeDone = res; if (o && o.signal) o.signal.addEventListener('abort', () => rej(new DOMException('a', 'AbortError'))); }); } };
      window.__read = u => { const r = window.__nfc[window.__nfc.length - 1]; r.onreading({ message: { records: [{ recordType: 'url', data: new TextEncoder().encode(u) }] } }); };
    });
    return p;
  };
  const wait = (p, ms) => p.waitForTimeout(ms || 450);
  const shot = async (p, n, ms) => { await wait(p, ms); await p.screenshot({ path: O + n + '.jpg', type: 'jpeg', quality: 84 }); };
  const el = async (p, sel, n) => { const l = p.locator(sel).first(); await l.scrollIntoViewIfNeeded(); await wait(p, 350); await l.screenshot({ path: O + n + '.jpg', type: 'jpeg', quality: 86 }); };
  const sheetShot = async (p, n) => { await wait(p, 500); await p.locator('#sheet').screenshot({ path: O + n + '.jpg', type: 'jpeg', quality: 86 }); };
  const esc = async p => { await p.keyboard.press('Escape'); await wait(p, 350); };
  const secOf = t => `section:has(.sec-h h2:has-text("${t}"))`;
  const api = (p, path, body) => p.evaluate(async ([path, body]) => {
    const r = await fetch('/materiel/api/' + path, { method: body ? 'POST' : 'GET', headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
    return r.json(); }, [path, body]);
  const login = async (p, l, p1, p2, pre) => {
    await p.goto(B); await wait(p, 700); if (pre) await shot(p, pre + 'login');
    await p.fill('#lg-login', l); await p.fill('#lg-pass', p1); await p.click('#f-login button[type=submit]'); await wait(p, 800);
    if (await p.$('#pw-cur')) { if (pre) await shot(p, pre + 'pwd'); await p.fill('#pw-cur', p1); await p.fill('#pw-new', p2); await p.fill('#pw-new2', p2); await p.click('#f-pwd button[type=submit]'); await wait(p, 1400); }
  };
  const photo = async (p, kind) => {
    await p.click('[data-act=take-photo]'); await wait(p, 300); await p.click('[data-pkind=' + kind + ']'); await wait(p, 200);
    const [fc] = await Promise.all([p.waitForEvent('filechooser'), p.click('[data-act=photo-shoot]')]); await fc.setFiles(LIT); await wait(p, 2600);
  };
  const scrollMain = (p, y) => p.evaluate(y => document.querySelector('main').scrollTo(0, y), y);
  const today = new Date(Date.now() - 10 * 3600e3).toISOString().slice(0, 10);

  // ---------- Grossiste : mise en place ----------
  const g = await mk(true);
  await login(g, 'admin', 'Provisoire2026', 'AdminParc2026', 'g_');
  const pwL = (await api(g, 'users', { name: 'Pharmacie du Lagon', login: 'lagon', role: 'pharmacie', pharmacy: 1 })).password;
  const pwT = (await api(g, 'users', { name: 'Teiki Teriierooiterai', login: 'teiki', role: 'equipe' })).password;
  await api(g, 'pharmacies/1/email', { email: 'officine@lagon.pf' });
  await api(g, 'mail/settings', { staff_email: 'parc@manaprocess.pf' });
  await g.goto(B + 'LIT-0101'); await wait(g, 1500);
  await photo(g, 'livraison'); await photo(g, 'etat');
  await esc(g);

  // ---------- Pharmacie (ordinateur) ----------
  const p = await mk(true);
  await login(p, 'lagon', pwL, 'Lagon2026parc', 'p_');
  const st = await api(p, 'state');
  const mine = st.equipment.filter(e => e.status === 'loc').map(e => e.ref);
  await shot(p, 'p_home');
  await scrollMain(p, 560); await shot(p, 'p_home2');
  await p.click('.tabs .scanbtn'); await sheetShot(p, 'p_plus'); await esc(p);
  await p.click('[data-act=catalog]'); await sheetShot(p, 'p_cat'); await esc(p);
  // demande de location avec nouveau bénéficiaire
  await scrollMain(p, 0); await p.click('[data-rqnew=location]'); await wait(p, 400);
  await p.selectOption('#rq-prod', 'Lit X5');
  await p.click('[data-act=rq-newpat]'); await wait(p, 300);
  await p.fill('#pa-name', 'Hinano Teriitahi'); await p.click('[data-sel=commune] [data-opt=Arue]'); await p.fill('#pa-addr', 'Servitude Tama, PK 6, côté mer'); await p.fill('#pa-tel', '87 99 88 77');
  await sheetShot(p, 'p_newpat');
  await p.click('#f-pat button[type=submit]'); await wait(p, 1200);
  await p.click('[data-sel=rqdays] [data-opt="90"]');
  await p.fill('#rq-note', 'Appeler la fille du bénéficiaire avant de passer. Portail vert.');
  await sheetShot(p, 'p_req_loc');
  await p.click('#f-req button[type=submit]'); await wait(p, 1200);
  // demande d'un fauteuil
  await p.click('[data-rqnew=location]'); await wait(p, 400);
  await p.selectOption('#rq-prod', { index: 6 }); await p.selectOption('#rq-pat', { index: 2 }); await p.click('[data-sel=rqdays] [data-opt="28"]');
  await p.click('#f-req button[type=submit]'); await wait(p, 1200);
  // reprise, prolongation et problème depuis la fiche
  await p.goto(B + mine[1]); await wait(p, 1600);
  await shot(p, 'p_fiche_actions');
  await p.click('#detail [data-rqnew=prolongation]'); await wait(p, 300); await p.click('[data-sel=rqdays] [data-opt="28"]'); await sheetShot(p, 'p_req_prol');
  await p.click('#f-req2 button[type=submit]'); await wait(p, 1200); await esc(p);
  await p.goto(B + mine[2]); await wait(p, 1500);
  await p.click('#detail [data-rqnew=reprise]'); await wait(p, 300); await sheetShot(p, 'p_req_rep');
  await p.click('#f-req2 button[type=submit]'); await wait(p, 1200); await esc(p);
  await p.goto(B + mine[3]); await wait(p, 1500);
  await p.click('#detail [data-rqnew=probleme]'); await wait(p, 300); await p.click('[data-sel=rqreason] [data-opt=bruit]'); await p.fill('#rq-note', 'Fait un bruit anormal depuis deux jours.');
  await sheetShot(p, 'p_req_pb');
  await p.click('#f-req2 button[type=submit]'); await wait(p, 1200); await esc(p);
  await p.goto(B); await wait(p, 1400);
  await p.click('.tabs [data-tab=loc]'); await wait(p, 300); await p.click('[data-ltab=dem]'); await shot(p, 'p_dem');
  await p.click('main [data-req]'); await sheetShot(p, 'p_req_detail'); await esc(p);
  await p.click('[data-ltab=cur]'); await shot(p, 'p_loc');
  // fiche et ordonnance
  await p.goto(B + 'LIT-0101'); await wait(p, 1800);
  await shot(p, 'p_fiche');
  await el(p, '#detail ' + secOf('Ordonnance'), 'p_ordo');
  await el(p, '#detail ' + secOf('Photos du matériel'), 'p_photos');
  const [fc] = await Promise.all([p.waitForEvent('filechooser'), p.click('[data-act=scan-presc]')]); await fc.setFiles(ORDO); await wait(p, 1600);
  await sheetShot(p, 'p_scan');
  await p.click('[data-act=scan-save-dir]'); await wait(p, 1300);
  await p.fill('#pr-date', today); await p.click('[data-pvalid="6"]'); await p.check('#pr-ok'); await sheetShot(p, 'p_presc');
  await p.click('#f-presc button[type=submit]'); await wait(p, 1500);
  await el(p, '#detail ' + secOf('Ordonnance'), 'p_ordo_ok');
  await p.click('[data-act=view-presc]'); await shot(p, 'p_view', 1000); await esc(p);
  await el(p, '#detail ' + secOf('Historique'), 'p_hist');
  await p.click('[data-act=back]'); await wait(p, 400);
  await p.click('.tabs [data-tab=fact]'); await shot(p, 'p_fact', 1200);
  await p.click('.tabs [data-act=more]'); await sheetShot(p, 'p_more');
  await p.click('.menu [data-act=my-mail]'); await sheetShot(p, 'p_mail'); await esc(p);

  // ---------- Grossiste (ordinateur) ----------
  await g.goto(B); await wait(g, 1500);
  await shot(g, 'g_home');
  await scrollMain(g, 480); await shot(g, 'g_home2');
  await g.click('.tabs [data-tab=loc]'); await wait(g, 300); await g.click('[data-ltab=dem]'); await shot(g, 'g_dem');
  await g.click('main [data-req]:has-text("Lit X5")'); await sheetShot(g, 'g_req_loc');
  await g.evaluate(() => { document.querySelector('#sheet').scrollTo(0, 99999); }); await sheetShot(g, 'g_req_loc2');
  await g.fill('#rq-ans', 'Livraison prévue le matin, entre 8 h et 10 h.');
  await g.click('[data-rqdo=plan]'); await wait(g, 1300);
  await g.click('main [data-req]:has-text("Problème")'); await sheetShot(g, 'g_req_pb'); await esc(g);
  await g.click('[data-ltab=plan]'); await shot(g, 'g_plan');
  await g.click('.tabs [data-act=more]'); await wait(g, 300); await g.click('.menu [data-act=ph-list]'); await sheetShot(g, 'g_phlist');
  await g.click('[data-phs="1"]'); await sheetShot(g, 'g_ph'); await esc(g);
  await g.click('.tabs [data-tab=parc]'); await shot(g, 'g_parc');
  await g.click('[data-mode=plan]'); await shot(g, 'g_map'); await g.click('[data-mode=stats]'); await shot(g, 'g_stats'); await g.click('[data-mode=grid]');
  await g.click('.st[data-filter=dispo]'); await wait(g, 300); await g.click('#parc-list .card'); await wait(g, 1000); await shot(g, 'g_fiche_dispo');
  await g.click('[data-act=assign]'); await sheetShot(g, 'g_assign'); await esc(g); await esc(g);
  await g.goto(B); await wait(g, 1300);
  await g.click('.tabs [data-tab=loc]'); await shot(g, 'g_loc');
  await g.click('[data-ltab=renew]'); await shot(g, 'g_renew');
  await g.click('.tabs [data-tab=ent]'); await shot(g, 'g_ent');
  await g.click('.tabs [data-tab=rap]'); await shot(g, 'g_rap');
  await g.click('.chip[data-rtab=fact]'); await shot(g, 'g_fact', 1100);
  await g.click('.chip[data-rtab=exp]'); await shot(g, 'g_exp');
  await g.click('.tabs .scanbtn'); await sheetShot(g, 'g_quick'); await esc(g);
  await g.click('.tabs [data-act=more]'); await sheetShot(g, 'g_more');
  await g.click('.menu [data-act=settings]'); await shot(g, 'g_settings', 800);
  await g.click('#settings [data-tag]'); await sheetShot(g, 'g_tag'); await esc(g);
  await g.click('[data-act=close-settings]'); await wait(g, 300);
  await g.click('.tabs [data-act=more]'); await wait(g, 300); await g.click('.menu [data-act=accounts]'); await shot(g, 'g_accounts', 1400);
  await g.click('[data-act=new-user]'); await g.fill('#u-name', 'Pharmacie Moana'); await g.fill('#u-login', 'moana'); await g.click('[data-sel=pharm] .chip:has-text("Moana")'); await sheetShot(g, 'g_newuser');
  await g.click('#f-user button[type=submit]'); await wait(g, 900);
  await g.evaluate(() => { const c = document.querySelector('.pwbox code'); if (c) c.textContent = 'https://manaprocess.cloud/materiel/'; }); await sheetShot(g, 'g_newuser_pw'); await esc(g);
  await el(g, '#settings ' + secOf('E-mails de rappel'), 'g_mail');
  await g.click('[data-act=close-settings]');

  // ---------- Technicien (téléphone) ----------
  const t = await mk(false);
  await login(t, 'teiki', pwT, 'Technicien2026', 't_');
  await shot(t, 't_home');
  await t.click('.tabs [data-tab=loc]'); await wait(t, 300); await t.click('[data-ltab=plan]'); await shot(t, 't_plan');
  await t.click('main [data-req]:has-text("Lit X5")'); await wait(t, 500); await t.evaluate(() => document.querySelector('#sheet').scrollTo(0, 99999)); await shot(t, 't_req');
  await t.click('#sheet [data-rqdo=done][data-eq]'); await wait(t, 1300);
  await t.click('[data-ltab=dem]'); await wait(t, 300);
  await t.click('main [data-req]:has-text("Reprise")'); await wait(t, 500); await t.evaluate(() => document.querySelector('#sheet').scrollTo(0, 99999)); await shot(t, 't_req_rep'); await esc(t);
  await t.click('.tabs .scanbtn'); await shot(t, 't_quick');
  await t.click('.menu [data-act=scan]'); await shot(t, 't_scan', 700);
  await t.evaluate(() => window.__read('https://manaprocess.cloud/materiel/LIT-0101')); await wait(t, 2600);
  await t.evaluate(() => document.querySelector('.dscroll').scrollTo(0, 0)); await shot(t, 't_fiche');
  await el(t, '#detail .kv', 't_kv');
  await photo(t, 'livraison');
  await el(t, '#detail ' + secOf('Photos du matériel'), 't_photos');
  await t.click('[data-act=program]'); await shot(t, 't_write', 700); await t.evaluate(() => window.__writeDone && window.__writeDone()); await wait(t, 1500);
  await t.click('[data-act=back]'); await wait(t, 400);
  await t.click('.tabs [data-tab=ent]'); await shot(t, 't_ent');
  await t.click('#sec-des .row'); await wait(t, 1000); await t.evaluate(() => document.querySelector('.dscroll').scrollTo(0, 0)); await shot(t, 't_desinf'); await t.click('[data-act=back]'); await wait(t, 400);
  await t.click('#sec-mnt .row'); await wait(t, 1000); await t.evaluate(() => document.querySelector('.dscroll').scrollTo(0, 0)); await shot(t, 't_maint'); await t.click('[data-act=back]'); await wait(t, 400);
  await t.click('[data-cdays="30"]'); await wait(t, 400); await t.click('#sec-ctl .row:nth-child(2)'); await wait(t, 1000);
  await el(t, '#detail .kv', 't_check');
  console.log('erreurs JS :', errs.length ? errs : 'aucune');
  await b.close();
})().catch(e => { console.error(e); console.log('erreurs JS :', errs); process.exit(1); });
