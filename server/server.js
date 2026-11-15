'use strict';
/*
 * MédiParc NFC : serveur de l'application (comptes, base partagée, facturation).
 * Aucune dépendance externe : Node 22+ (http, crypto, zlib et SQLite intégrés).
 *
 * Variables d'environnement :
 *   PORT (3000), BASE_PATH (/materiel), DATA_DIR (./data), SITE_DIR (deploy/site/materiel),
 *   PUBLIC_URL (https://manaprocess.cloud/materiel/), TZ (Pacific/Tahiti),
 *   ADMIN_PASSWORD (mot de passe provisoire du compte « admin », utilisé au premier démarrage),
 *   COOKIE_SECURE (« 0 » pour tester en http local).
 */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const zlib = require('node:zlib');
const { DatabaseSync } = require('node:sqlite');
const mailer = require('./mailer');

const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.PORT) || 3000;
const BASE = (process.env.BASE_PATH || '/materiel').replace(/\/+$/, '');
const DATA = process.env.DATA_DIR || path.join(ROOT, 'data');
const SITE = process.env.SITE_DIR || path.join(ROOT, 'deploy', 'site', 'materiel');
const PUBLIC_URL = process.env.PUBLIC_URL || 'https://manaprocess.cloud/materiel/';
const TZ = process.env.TZ || 'Pacific/Tahiti';
const SECURE = process.env.COOKIE_SECURE !== '0';
const SESSION_DAYS = 30;

fs.mkdirSync(path.join(DATA, 'backups'), { recursive: true });
const db = new DatabaseSync(path.join(DATA, 'mediparc.db'));
db.exec('PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;');

/* ---------- Dates (heure de Tahiti) ---------- */
function today() { return new Date().toLocaleDateString('sv-SE', { timeZone: TZ }); }
function nowStamp() { return new Date().toLocaleString('sv-SE', { timeZone: TZ }).slice(0, 16); }
function addDays(d, n) { const t = new Date(d + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + n); return t.toISOString().slice(0, 10); }
function diffDays(a, b) { return Math.round((Date.parse(b + 'T12:00:00Z') - Date.parse(a + 'T12:00:00Z')) / 864e5); }
function isDate(s) { return typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(Date.parse(s + 'T12:00:00Z')); }

/* ---------- Schéma ---------- */
db.exec(`
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pharmacies(id INTEGER PRIMARY KEY, name TEXT NOT NULL, commune TEXT NOT NULL DEFAULT '', created_at TEXT);
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY, login TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('admin','equipe','pharmacie')),
  pharmacy_id INTEGER REFERENCES pharmacies(id), pass_hash TEXT NOT NULL,
  must_change INTEGER NOT NULL DEFAULT 1, active INTEGER NOT NULL DEFAULT 1, created_at TEXT, last_login TEXT);
CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires_at INTEGER NOT NULL, created_at TEXT);
CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY, name TEXT NOT NULL, address TEXT NOT NULL DEFAULT '', commune TEXT NOT NULL DEFAULT '', care TEXT NOT NULL DEFAULT '', lat REAL, lon REAL, created_at TEXT);
CREATE TABLE IF NOT EXISTS equipment(
  id INTEGER PRIMARY KEY, ref TEXT NOT NULL UNIQUE, name TEXT NOT NULL, brand TEXT NOT NULL DEFAULT '', kind TEXT NOT NULL DEFAULT 'lit', photo TEXT,
  catalog TEXT NOT NULL DEFAULT '', week_price INTEGER NOT NULL DEFAULT 0, buy_price INTEGER NOT NULL DEFAULT 0, buy_estimated INTEGER NOT NULL DEFAULT 0,
  prior_days INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'dispo' CHECK(status IN ('dispo','loc','desinf','maint')),
  status_since TEXT NOT NULL, next_check TEXT NOT NULL, link TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS rentals(
  id INTEGER PRIMARY KEY, equipment_id INTEGER NOT NULL REFERENCES equipment(id), patient_id INTEGER NOT NULL REFERENCES patients(id),
  pharmacy_id INTEGER NOT NULL REFERENCES pharmacies(id), start_date TEXT NOT NULL, planned_end TEXT NOT NULL, end_date TEXT,
  week_price INTEGER NOT NULL, created_by TEXT NOT NULL DEFAULT '');
CREATE INDEX IF NOT EXISTS rentals_eq ON rentals(equipment_id, end_date);
CREATE INDEX IF NOT EXISTS rentals_ph ON rentals(pharmacy_id, end_date);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, equipment_id INTEGER NOT NULL REFERENCES equipment(id), rental_id INTEGER REFERENCES rentals(id), at TEXT NOT NULL, text TEXT NOT NULL, user_name TEXT NOT NULL DEFAULT '');
CREATE INDEX IF NOT EXISTS events_eq ON events(equipment_id, at);
CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY, equipment_id INTEGER NOT NULL REFERENCES equipment(id), rental_id INTEGER REFERENCES rentals(id), at TEXT NOT NULL,
  user_id INTEGER, user_name TEXT NOT NULL DEFAULT '', lat REAL, lon REAL, accuracy REAL, source TEXT NOT NULL DEFAULT 'nfc');
CREATE INDEX IF NOT EXISTS scans_eq ON scans(equipment_id, at);
CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY, rental_id INTEGER NOT NULL REFERENCES rentals(id), kind TEXT NOT NULL DEFAULT 'ordonnance',
  filename TEXT NOT NULL, mime TEXT NOT NULL, size INTEGER NOT NULL, file TEXT NOT NULL, at TEXT NOT NULL, user_name TEXT NOT NULL DEFAULT '');
CREATE INDEX IF NOT EXISTS documents_r ON documents(rental_id);
`);
db.exec(`CREATE TABLE IF NOT EXISTS prescriptions(rental_id INTEGER PRIMARY KEY REFERENCES rentals(id), presc_date TEXT NOT NULL, ref TEXT NOT NULL DEFAULT '',
  at TEXT NOT NULL, user_name TEXT NOT NULL DEFAULT '');`);
/* Dépôt de fichiers d'ordonnance : désactivé par défaut (serveur non certifié HDS). La pharmacie conserve
   l'ordonnance et en déclare seulement la vérification. Activer (DOCUMENTS_ENABLED=1) uniquement sur un hébergement certifié HDS. */
const DOCUMENTS_ENABLED = process.env.DOCUMENTS_ENABLED === '1';
/* Fin de validité de l'ordonnance : sert au rappel « nouvelle ordonnance à prévoir ». */
if (!db.prepare('PRAGMA table_info(prescriptions)').all().some(c => c.name === 'valid_until')) db.exec('ALTER TABLE prescriptions ADD COLUMN valid_until TEXT');
const DOCS = path.join(DATA, 'documents');
/* Photos horodatées du matériel (état à la livraison, au retour, panne). Pas de donnée médicale : stockées sur le serveur. */
db.exec(`CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, equipment_id INTEGER NOT NULL REFERENCES equipment(id), rental_id INTEGER REFERENCES rentals(id),
  at TEXT NOT NULL, user_id INTEGER, user_name TEXT NOT NULL DEFAULT '', kind TEXT NOT NULL DEFAULT 'etat', lat REAL, lon REAL, accuracy REAL, file TEXT NOT NULL, size INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS photos_eq ON photos(equipment_id, at);`);
const PHOTOS = path.join(DATA, 'photos');
fs.mkdirSync(PHOTOS, { recursive: true });
if (!db.prepare('PRAGMA table_info(events)').all().some(c => c.name === 'photo_id')) db.exec('ALTER TABLE events ADD COLUMN photo_id INTEGER');
if (!db.prepare('PRAGMA table_info(pharmacies)').all().some(c => c.name === 'email')) db.exec("ALTER TABLE pharmacies ADD COLUMN email TEXT NOT NULL DEFAULT ''");
db.exec(`CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, rental_id INTEGER NOT NULL REFERENCES rentals(id), kind TEXT NOT NULL, ckey TEXT NOT NULL,
  sent_at TEXT NOT NULL, UNIQUE(rental_id, kind, ckey));`);
const PHOTO_KINDS = { livraison: 'livraison', retour: 'retour', etat: 'état', panne: 'panne' };
for (const [col, def] of [['phone', "TEXT NOT NULL DEFAULT ''"], ['anonymized', 'INTEGER NOT NULL DEFAULT 0']])
  if (!db.prepare('PRAGMA table_info(patients)').all().some(c => c.name === col)) db.exec('ALTER TABLE patients ADD COLUMN ' + col + ' ' + def);
fs.mkdirSync(DOCS, { recursive: true });

/* ---------- Chiffrement des données personnelles (AES-256-GCM) ----------
   Nom, adresse et téléphone des bénéficiaires sont chiffrés dans la base. La clé (32 octets en base64) vient de DATA_KEY,
   conservée hors de la base ; à défaut, une clé est créée dans le dossier des données (à éviter en production). */
function loadKey() {
  if (process.env.DATA_KEY) {
    const b = Buffer.from(process.env.DATA_KEY, 'base64');
    if (b.length !== 32) throw new Error('DATA_KEY doit contenir 32 octets encodés en base64.');
    return b;
  }
  const f = path.join(DATA, 'data.key');
  if (!fs.existsSync(f)) { fs.writeFileSync(f, crypto.randomBytes(32).toString('base64'), { mode: 0o600 }); console.warn('Clé de chiffrement créée dans ' + f + ' : définissez DATA_KEY en production.'); }
  return Buffer.from(fs.readFileSync(f, 'utf8').trim(), 'base64');
}
const KEY = loadKey();
function enc(t) {
  if (t == null || t === '') return '';
  const iv = crypto.randomBytes(12), c = crypto.createCipheriv('aes-256-gcm', KEY, iv);
  const ct = Buffer.concat([c.update(String(t), 'utf8'), c.final()]);
  return 'v1:' + Buffer.concat([iv, c.getAuthTag(), ct]).toString('base64');
}
function dec(v) {
  if (!v || !String(v).startsWith('v1:')) return v || '';
  const b = Buffer.from(String(v).slice(3), 'base64'), d = crypto.createDecipheriv('aes-256-gcm', KEY, b.subarray(0, 12));
  d.setAuthTag(b.subarray(12, 28));
  return Buffer.concat([d.update(b.subarray(28)), d.final()]).toString('utf8');
}
const q = (sql) => db.prepare(sql);
function tx(fn) { db.exec('BEGIN'); try { const r = fn(); db.exec('COMMIT'); return r; } catch (e) { db.exec('ROLLBACK'); throw e; } }
function setting(k, def) { const r = q('SELECT value FROM settings WHERE key=?').get(k); return r ? r.value : def; }
function setSetting(k, v) { q('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value').run(k, String(v)); }

/* ---------- Mots de passe et sessions ---------- */
function hashPassword(pw) {
  const salt = crypto.randomBytes(16);
  const h = crypto.scryptSync(pw, salt, 64, { N: 16384, r: 8, p: 1 });
  return 'scrypt$' + salt.toString('hex') + '$' + h.toString('hex');
}
function checkPassword(pw, stored) {
  const [alg, salt, hash] = String(stored).split('$');
  if (alg !== 'scrypt' || !salt || !hash) return false;
  const h = crypto.scryptSync(String(pw), Buffer.from(salt, 'hex'), 64, { N: 16384, r: 8, p: 1 });
  return crypto.timingSafeEqual(h, Buffer.from(hash, 'hex'));
}
function tempPassword() {
  const a = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
  let s = ''; const b = crypto.randomBytes(14);
  for (let i = 0; i < 14; i++) s += a[b[i] % a.length];
  return s.slice(0, 4) + '-' + s.slice(4, 9) + '-' + s.slice(9);
}
function sha(t) { return crypto.createHash('sha256').update(t).digest('hex'); }
function passwordProblem(pw) {
  if (typeof pw !== 'string' || pw.length < 10) return 'Le mot de passe doit contenir au moins 10 caractères.';
  if (!/[A-Za-z]/.test(pw) || !/[0-9]/.test(pw)) return 'Le mot de passe doit contenir des lettres et des chiffres.';
  return null;
}

/* ---------- Données de démonstration (premier démarrage) ---------- */
const COMMUNES = {
  'Papeete': [-17.535, -149.569], 'Pirae': [-17.533, -149.547], 'Arue': [-17.522, -149.527], 'Mahina': [-17.508, -149.482],
  'Papenoo': [-17.505, -149.42], 'Hitiaa O Te Ra': [-17.6, -149.3], 'Taravao': [-17.737, -149.303], 'Taiarapu-Est': [-17.75, -149.24],
  'Taiarapu-Ouest': [-17.795, -149.32], 'Teva I Uta': [-17.766, -149.42], 'Papara': [-17.752, -149.512], 'Paea': [-17.718, -149.588],
  'Punaauia': [-17.635, -149.607], 'Faa\'a': [-17.553, -149.606]
};
const RAW = [
 ['LIT-0101','lit','lit','Lit Mantovani','Thuasne','Accessoires dès 1 290 XPF','loc','p1',-38,22,64,1700,120000,410,1],
 ['LIT-0102','lit-bas','lit','Lit X5','Herdegen','Dès 133 000 XPF (prix LPPR)','loc','p2',-6,50,200,1900,133000,520,0],
 ['LIT-0103','lit-allura','lit','Lit Allura','Burmeier','Dès 160 474 XPF','dispo',null,-3,null,75,2100,160474,330,0],
 ['PSR-0104','porte-serum','pompe','Porte sérum à roulettes à 4 crochets','Herdegen','Dès 13 178 XPF','loc','p3',-12,0,150,300,13178,290,0],
 ['LEV-0105','leve','leve','Lève-personne Birdie','Invacare','Dès 4 015 XPF','loc','p5',-64,30,6,2300,95000,180,1],
 ['LEV-0106','leve','leve','Lève-personne Birdie Evo Compact','Invacare','Sur demande','dispo',null,-15,null,12,2400,110000,95,1],
 ['LEV-0107',null,'leve','Lève-personne verticalisateur Isa Compact','Invacare','Dès 67 555 XPF','maint',null,-4,null,-9,2600,67555,240,0],
 ['DEA-0108','deamb-fixe','deamb','Déambulateur fixe/articulé Maxigo','Herdegen','Dès 8 946 XPF','loc','p4',-21,9,140,500,8946,150,0],
 ['DEA-0109','deamb-fixe','deamb','Déambulateur fixe Movigo','Herdegen','Dès 8 946 XPF','dispo',null,-9,null,120,450,8946,60,0],
 ['ROL-0110',null,'deamb','Rollator 2 roues Simply','Herdegen','8 946 XPF','desinf',null,0,null,88,500,8946,175,0],
 ['ROL-0111',null,'deamb','Delta Rollator 3 roues','Herdegen','8 946 XPF','dispo',null,-20,null,95,550,8946,40,0],
 ['ROL-0112','rollator-4','deamb','Rollator 4 roues 286i','Vermeiren','8 946 XPF','loc','p1',-38,22,-3,600,8946,130,0],
 ['ROL-0113','rollator-4b','deamb','Rollator 4 roues Simply','Herdegen','Dès 8 946 XPF','dispo',null,-9,null,110,600,8946,20,0],
 ['FRM-0114','fauteuil','fauteuil','Fauteuil roulant dossier fixe Albatros','Herdegen','Dès 63 725 XPF','loc','p4',-21,9,160,1100,63725,460,0],
 ['TNS-0115','tens','pompe','Tens Eco 2','Appareils électroniques','Dès 2 028 XPF','loc','p2',-6,22,300,400,12000,260,1],
 ['TNS-0116','tens','pompe','Tensi+ électrostimulateur TENS','Appareils électroniques','Dès 995 XPF','dispo',null,-30,null,280,400,9000,70,1],
 ['AER-0117','aerosol','oxy','Aérosols ST23 et ST24','Aérosol et oxygène','Dès 1 913 XPF','loc','p3',-12,16,40,700,18000,200,1],
 ['AER-0118','aerosol','oxy','Aérosol Atomisor','Aérosol et oxygène','Dès 1 913 XPF','desinf',null,-1,null,45,700,18000,310,1],
 ['AER-0119','aerosol','oxy','Aérosol LS 290','Aérosol et oxygène','Dès 1 916 XPF','dispo',null,-5,null,70,700,18000,85,1],
 ['AER-0120','aerosol','oxy','Aérosol AMSA','Aérosol et oxygène','Dès 2 485 XPF','dispo',null,-12,null,55,800,22000,45,1],
 ['OXY-0121','oxy','oxy','Concentrateur d\'O2 Platinum 9','Invacare','Dès 229 990 XPF','loc','p3',-12,0,18,2750,229990,505,0],
 ['ASP-0122','aspirateur','oxy','Aspirateur SV3','Aérosol et oxygène','Dès 155 XPF','loc','p5',-20,40,25,900,45000,270,1],
 ['TLT-0123','tire-lait','pompe','Tire-lait Medela Symphony +','Medela','Dès 1 004 XPF','loc','p2',-10,18,210,1000,180000,610,1],
 ['TLT-0124','tire-lait','pompe','Tire-lait Kitett Fisio Pro','Kitett','Dès 114 990 XPF','desinf',null,-2,null,190,1000,114990,380,0]
];
function seedDemo() {
  const T = today(), at = (d, h) => addDays(T, d) + ' ' + (h || '09:00');
  tx(() => {
    const ph = [['Pharmacie du Lagon', 'Punaauia'], ['Pharmacie Moana', 'Papeete'], ['Pharmacie de la Presqu\'île', 'Taravao']]
      .map(([n, c]) => Number(q('INSERT INTO pharmacies(name,commune,created_at) VALUES(?,?,?)').run(n, c, nowStamp()).lastInsertRowid));
    const pts = [
      ['Jeanne Morel', 'PK 15 côté mer, Punaauia', 'Punaauia', '87 10 20 30', -17.635, -149.607],
      ['André Lefèvre', 'PK 10,5 côté montagne, Mahina', 'Mahina', '87 11 22 33', -17.508, -149.482],
      ['Lucie Bernard', 'PK 22 côté mer, Paea', 'Paea', '89 12 34 56', -17.718, -149.588],
      ['Henri Girard', 'Centre-ville, Taravao', 'Taravao', '87 13 24 35', -17.737, -149.303],
      ['Résidence Les Tilleuls', 'PK 36 côté montagne, Papara', 'Papara', '40 54 32 10', -17.752, -149.512]
    ].map(([n, a, c, t, la, lo]) => Number(q('INSERT INTO patients(name,address,commune,phone,lat,lon,created_at) VALUES(?,?,?,?,?,?,?)').run(enc(n), enc(a), c, enc(t), la, lo, nowStamp()).lastInsertRowid));
    const P = { p1: pts[0], p2: pts[1], p3: pts[2], p4: pts[3], p5: pts[4] };
    const FA = { p1: ph[0], p2: ph[1], p3: ph[0], p4: ph[2], p5: ph[1] };
    const fname = id => q('SELECT name FROM pharmacies WHERE id=?').get(id).name;
    const base = setting('link_base', PUBLIC_URL);
    const ids = [];
    for (const r of RAW) {
      const [ref, photo, kind, name, brand, cat, st, pt, since, end, chk, px, buy, days, est] = r;
      const id = Number(q(`INSERT INTO equipment(ref,name,brand,kind,photo,catalog,week_price,buy_price,buy_estimated,prior_days,status,status_since,next_check,link)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(ref, name, brand, kind, photo, cat, px, buy, est, days, st, addDays(T, since), addDays(T, chk), base + ref).lastInsertRowid);
      ids.push({ id, since, st });
      const ev = (d, text, rid) => q('INSERT INTO events(equipment_id,rental_id,at,text,user_name) VALUES(?,?,?,?,?)').run(id, rid || null, at(d), text, 'Démonstration');
      if (st === 'loc') {
        const fa = ref === 'TNS-0115' ? ph[0] : FA[pt];
        const rid = Number(q('INSERT INTO rentals(equipment_id,patient_id,pharmacy_id,start_date,planned_end,week_price,created_by) VALUES(?,?,?,?,?,?,?)')
          .run(id, P[pt], fa, addDays(T, since), addDays(T, end), px, 'Démonstration').lastInsertRowid);
        ev(since - 1, 'Désinfection validée');
        ev(since, 'Livré chez {p} par la ' + fname(fa), rid);
      } else if (st === 'dispo') ev(since, 'Désinfection validée, remis en stock');
      else if (st === 'desinf') ev(since, 'Retour de location, en attente de désinfection');
      else ev(since, 'Panne signalée : batterie à remplacer');
    }
    /* Locations terminées (historique), sans chevauchement avec l'état actuel. */
    for (let i = 0; i < 28; i++) {
      const e = ids[(i * 5) % ids.length], pk = 'p' + (i % 5 + 1), fa = ph[i % 3];
      const dur = [14, 28, 21, 42, 7][i % 5], endOff = -(3 + i * 6), startOff = endOff - dur;
      if (endOff > e.since - 1) continue;
      const px = q('SELECT week_price FROM equipment WHERE id=?').get(e.id).week_price;
      const rid = Number(q('INSERT INTO rentals(equipment_id,patient_id,pharmacy_id,start_date,planned_end,end_date,week_price,created_by) VALUES(?,?,?,?,?,?,?,?)')
        .run(e.id, P[pk], fa, addDays(T, startOff), addDays(T, endOff), addDays(T, endOff), px, 'Démonstration').lastInsertRowid);
      q('INSERT INTO events(equipment_id,rental_id,at,text,user_name) VALUES(?,?,?,?,?)').run(e.id, rid, at(startOff), 'Livré chez {p} par la ' + fname(fa), 'Démonstration');
      q('INSERT INTO events(equipment_id,rental_id,at,text,user_name) VALUES(?,?,?,?,?)').run(e.id, rid, at(endOff, '16:00'), 'Retour de location ({p})', 'Démonstration');
    }
    setSetting('seeded', today());
  });
}
if (!setting('link_base')) setSetting('link_base', PUBLIC_URL);
/* Migration : aucune information médicale (champ « prise en charge » vidé), données personnelles chiffrées,
   noms retirés du texte de l'historique (remplacés par {p}, complété à l'affichage). */
if (setting('privacy_v1') !== '1') tx(() => {
  for (const p of q('SELECT * FROM patients').all()) {
    const name = dec(p.name);
    for (const ev of q('SELECT ev.id, ev.text FROM events ev JOIN rentals r ON r.id=ev.rental_id WHERE r.patient_id=?').all(p.id))
      if (name && ev.text.includes(name)) q('UPDATE events SET text=? WHERE id=?').run(ev.text.split(name).join('{p}'), ev.id);
    q("UPDATE patients SET name=?, address=?, phone=?, care='' WHERE id=?").run(enc(name), enc(dec(p.address)), enc(dec(p.phone)), p.id);
  }
  setSetting('privacy_v1', '1');
  setSetting('privacy_cleanup', '1');
});
/* Après la migration : la base est compactée (plus aucune trace des anciennes valeurs en clair)
   et les sauvegardes antérieures, non chiffrées, sont supprimées. */
if (setting('privacy_cleanup') === '1') {
  try {
    db.exec('VACUUM');
    const dir = path.join(DATA, 'backups');
    for (const n of fs.readdirSync(dir)) if (/^mediparc-.*\.db$/.test(n)) fs.unlinkSync(path.join(dir, n));
    setSetting('privacy_cleanup', '0');
  } catch (e) { console.error('Nettoyage après migration impossible :', e.message); }
}
if (!setting('seeded') && q('SELECT COUNT(*) n FROM equipment').get().n === 0) seedDemo();
if (setting('demo_presc') !== '1') {
  const open = q('SELECT * FROM rentals WHERE end_date IS NULL ORDER BY id').all();
  if (open.length && open.every(r => r.created_by === 'Démonstration') && q('SELECT COUNT(*) n FROM prescriptions').get().n === 0) tx(() => {
    const T = today();
    /* [décalage de la date d'ordonnance, validité en jours] : expirée, bientôt expirée, plus courte que la location, valide. */
    const plan = [[-60, 50], [-80, 90], [-20, 30], [-30, 180], [-15, 365], [-40, 120], [-10, 90], [-25, 365], [-5, 60], [-35, 365]];
    open.slice(0, plan.length).forEach((r, i) => {
      const d = addDays(T, plan[i][0]), v = addDays(d, plan[i][1]);
      q('INSERT INTO prescriptions(rental_id,presc_date,valid_until,ref,at,user_name) VALUES(?,?,?,?,?,?)').run(r.id, d, v, 'ORD-DEMO-' + (100 + i), addDays(T, plan[i][0]) + ' 10:00', 'Démonstration');
    });
  });
  setSetting('demo_presc', '1');
}
if (q('SELECT COUNT(*) n FROM users').get().n === 0) {
  let pw = process.env.ADMIN_PASSWORD;
  if (!pw) { pw = tempPassword(); console.log('Compte admin créé. Mot de passe provisoire : ' + pw); }
  q('INSERT INTO users(login,name,role,pass_hash,must_change,created_at) VALUES(?,?,?,?,1,?)').run('admin', 'Administrateur', 'admin', hashPassword(pw), nowStamp());
  console.log('Compte « admin » créé (changement de mot de passe demandé à la première connexion).');
}

/* ---------- Sauvegardes quotidiennes ---------- */
function backup() {
  try {
    const dir = path.join(DATA, 'backups'), f = path.join(dir, 'mediparc-' + today() + '.db');
    if (!fs.existsSync(f)) db.exec("VACUUM INTO '" + f.replace(/'/g, "''") + "'");
    fs.readdirSync(dir).filter(n => /^mediparc-\d{4}-\d{2}-\d{2}\.db$/.test(n)).sort().slice(0, -14).forEach(n => fs.unlinkSync(path.join(dir, n)));
  } catch (e) { console.error('Sauvegarde impossible :', e.message); }
}
backup(); setInterval(backup, 6 * 3600e3).unref();
/* Conservation : 3 ans après la fin de la dernière location, le bénéficiaire est anonymisé ; les positions de scan
   et numéros d'ordonnance de plus de 3 ans sont effacés. Les montants et dates de location restent (comptabilité). */
const RETENTION_DAYS = 3 * 365 + 1;
function purge() {
  try {
    const limit = addDays(today(), -RETENTION_DAYS);
    tx(() => {
      const old = q(`SELECT p.id FROM patients p WHERE p.anonymized=0
        AND NOT EXISTS (SELECT 1 FROM rentals r WHERE r.patient_id=p.id AND (r.end_date IS NULL OR r.end_date >= ?))
        AND (EXISTS (SELECT 1 FROM rentals r WHERE r.patient_id=p.id) OR p.created_at < ?)`).all(limit, limit);
      for (const p of old) q("UPDATE patients SET name=?, address='', phone='', lat=NULL, lon=NULL, anonymized=1 WHERE id=?").run(enc('Bénéficiaire anonymisé'), p.id);
      q('DELETE FROM scans WHERE at < ?').run(limit);
      for (const x of q('SELECT p.id, p.file FROM photos p JOIN rentals r ON r.id=p.rental_id WHERE r.end_date IS NOT NULL AND r.end_date < ?').all(limit)) {
        q('DELETE FROM photos WHERE id=?').run(x.id); q('UPDATE events SET photo_id=NULL WHERE photo_id=?').run(x.id); try { fs.unlinkSync(path.join(PHOTOS, x.file)); } catch (e) {}
      }
      q("UPDATE prescriptions SET ref='' WHERE rental_id IN (SELECT id FROM rentals WHERE end_date IS NOT NULL AND end_date < ?)").run(limit);
      if (old.length) console.log(old.length + ' bénéficiaire(s) anonymisé(s) (conservation 3 ans).');
    });
  } catch (e) { console.error('Purge impossible :', e.message); }
}
purge(); setInterval(purge, 24 * 3600e3).unref();
setInterval(() => q('DELETE FROM sessions WHERE expires_at<?').run(Date.now()), 3600e3).unref();

/* ---------- Rappels par e-mail aux pharmacies ----------
   Un e-mail par jour et par pharmacie, seulement s'il y a du nouveau. Chaque rappel n'est envoyé qu'une fois par étape
   (clé = date de validité de l'ordonnance) : une nouvelle ordonnance relance le cycle. Le patient n'y figure que par ses
   initiales et sa commune ; le lien ouvre la fiche dans le portail (connexion obligatoire). */
const MAIL_KINDS = { missing: 'Ordonnance à confirmer', soon14: 'Nouvelle ordonnance à prévoir', soon3: 'Ordonnance bientôt expirée', expired: 'Ordonnance expirée', beforeEnd: 'Ordonnance plus courte que la location' };
function initialsOf(n) { return String(n || '').split(/[\s-]+/).filter(w => /^\p{Lu}/u.test(w)).slice(0, 3).map(w => w[0] + '.').join(' ') || '—'; }
function emailsOf(s) { return String(s || '').split(/[,;\s]+/).map(x => x.trim()).filter(x => /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(x)); }
function pendingReminders(pharmacyId) {
  const T = today();
  const rows = q(`SELECT r.id, r.patient_id, r.start_date, r.planned_end, e.ref, e.name eq, p.commune, p.name pname, pr.valid_until, pr.presc_date
    FROM rentals r JOIN equipment e ON e.id=r.equipment_id JOIN patients p ON p.id=r.patient_id LEFT JOIN prescriptions pr ON pr.rental_id=r.id
    WHERE r.end_date IS NULL AND r.pharmacy_id=? ORDER BY e.ref`).all(pharmacyId);
  const out = [];
  for (const r of rows) {
    let kind = null, key = '', when = '';
    if (!r.valid_until) {
      if (!r.presc_date && diffDays(r.start_date, T) >= 2) { kind = 'missing'; key = r.start_date; when = 'location démarrée le ' + r.start_date.split('-').reverse().join('/'); }
    } else {
      const left = diffDays(T, r.valid_until), v = r.valid_until.split('-').reverse().join('/');
      if (left < 0) { kind = 'expired'; key = r.valid_until; when = 'expirée depuis le ' + v; }
      else if (left <= 3) { kind = 'soon3'; key = r.valid_until; when = 'expire le ' + v; }
      else if (left <= 14) { kind = 'soon14'; key = r.valid_until; when = 'expire le ' + v; }
      else if (r.valid_until < r.planned_end) { kind = 'beforeEnd'; key = r.valid_until + '|' + r.planned_end; when = 'valable jusqu\'au ' + v + ', location prévue jusqu\'au ' + r.planned_end.split('-').reverse().join('/'); }
    }
    if (!kind) continue;
    if (q('SELECT 1 FROM notifications WHERE rental_id=? AND kind=? AND ckey=?').get(r.id, kind, key)) continue;
    out.push({ rental_id: r.id, kind, key, ref: r.ref, eq: r.eq, who: initialsOf(dec(r.pname)) + ' (' + r.commune + ')', when });
  }
  return out;
}
function reminderMail(ph, items) {
  const base = setting('link_base', PUBLIC_URL).replace(/[#=]$/, '').replace(/\/?$/, '/');
  const h = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const crit = items.filter(i => i.kind === 'expired').length;
  const subject = (crit ? crit + ' ordonnance' + (crit > 1 ? 's' : '') + ' expirée' + (crit > 1 ? 's' : '') + ' · ' : '') + 'Rappels ordonnances · ' + ph.name;
  const rows = items.map(i => '<tr><td style="padding:10px 12px;border-bottom:1px solid #e3ecee"><b style="color:' + (i.kind === 'expired' ? '#b8352b' : '#a65f00') + '">' + h(MAIL_KINDS[i.kind]) + '</b><br>'
    + h(i.eq) + ' · ' + h(i.ref) + '<br><span style="color:#5b7078">Bénéficiaire ' + h(i.who) + ' · ' + h(i.when) + '</span></td>'
    + '<td style="padding:10px 12px;border-bottom:1px solid #e3ecee;text-align:right;white-space:nowrap"><a href="' + h(base + i.ref) + '" style="color:#0a7c88;font-weight:600">Ouvrir la fiche</a></td></tr>').join('');
  const html = '<div style="font-family:Arial,Helvetica,sans-serif;color:#0d2730;max-width:620px;margin:0 auto">'
    + '<div style="background:#0b5361;color:#fff;padding:16px 20px;border-radius:12px 12px 0 0"><b style="font-size:18px;color:#62cfc4">Mana</b><b style="font-size:18px">Process</b> · Parc NFC</div>'
    + '<div style="border:1px solid #d5dfe1;border-top:0;border-radius:0 0 12px 12px;padding:18px 20px">'
    + '<p style="margin:0 0 12px">Bonjour,</p><p style="margin:0 0 14px">Voici les ordonnances à traiter pour les locations de la <b>' + h(ph.name) + '</b> :</p>'
    + '<table style="width:100%;border-collapse:collapse;font-size:14px">' + rows + '</table>'
    + '<p style="margin:16px 0 0;font-size:13px;color:#5b7078">Pour enregistrer une nouvelle ordonnance, ouvrez la fiche dans le portail puis « Enregistrer la nouvelle ordonnance ». '
    + 'Aucune ordonnance n\'est stockée en ligne : elles restent sur le serveur de la pharmacie.</p>'
    + '<p style="margin:12px 0 0;font-size:12px;color:#8fa6ad">Message automatique envoyé une fois par jour lorsqu\'il y a du nouveau. Pour changer l\'adresse de réception : portail, menu Plus, « E-mail des rappels ».</p></div></div>';
  const text = 'Rappels ordonnances · ' + ph.name + '\n\n' + items.map(i => '- ' + MAIL_KINDS[i.kind] + ' : ' + i.eq + ' (' + i.ref + '), bénéficiaire ' + i.who + ', ' + i.when + '\n  ' + base + i.ref).join('\n')
    + '\n\nAucune ordonnance n\'est stockée en ligne : elles restent sur le serveur de la pharmacie.\nMessage automatique.';
  return { subject, html, text };
}
async function runReminders(manual) {
  const res = { at: nowStamp(), sent: 0, skipped: 0, errors: [] };
  if (!mailer.configured()) { res.errors.push('Envoi d\'e-mails non configuré.'); setSetting('mail_log', JSON.stringify(res)); return res; }
  for (const ph of q('SELECT * FROM pharmacies ORDER BY name').all()) {
    const items = pendingReminders(ph.id), to = emailsOf(ph.email);
    if (!items.length) continue;
    if (!to.length) { res.skipped++; continue; }
    try {
      await mailer.send(Object.assign({ to }, reminderMail(ph, items)));
      tx(() => items.forEach(i => q('INSERT OR IGNORE INTO notifications(rental_id,kind,ckey,sent_at) VALUES(?,?,?,?)').run(i.rental_id, i.kind, i.key, nowStamp())));
      res.sent++;
    } catch (e) { res.errors.push(ph.name + ' : ' + e.message); }
  }
  setSetting('mail_log', JSON.stringify(res));
  if (!manual) setSetting('mail_last_run', today());
  if (res.sent || res.errors.length) console.log('Rappels e-mail : ' + res.sent + ' envoyé(s), ' + res.errors.length + ' erreur(s).');
  return res;
}
setInterval(() => {
  if (setting('mail_enabled', '1') !== '1' || setting('mail_last_run') === today()) return;
  const hour = Number(new Date().toLocaleString('sv-SE', { timeZone: TZ }).slice(11, 13));
  if (hour >= Number(setting('mail_hour', '7'))) runReminders(false).catch(e => console.error('Rappels e-mail :', e.message));
}, 10 * 60e3).unref();

/* ---------- Outils HTTP ---------- */
class HttpError extends Error { constructor(status, msg) { super(msg); this.status = status; } }
const fail = (s, m) => { throw new HttpError(s, m); };
function send(req, res, status, body, type, extra) {
  let buf = Buffer.isBuffer(body) ? body : Buffer.from(body);
  const h = Object.assign({ 'Content-Type': type, 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'same-origin' }, extra || {});
  if (buf.length > 1024 && /gzip/.test(req.headers['accept-encoding'] || '') && /json|text|javascript|svg|csv|manifest/.test(type)) {
    buf = zlib.gzipSync(buf); h['Content-Encoding'] = 'gzip'; h['Vary'] = 'Accept-Encoding';
  }
  h['Content-Length'] = buf.length;
  res.writeHead(status, h); res.end(req.method === 'HEAD' ? undefined : buf);
}
const json = (req, res, status, obj, extra) => send(req, res, status, JSON.stringify(obj), 'application/json; charset=utf-8', Object.assign({ 'Cache-Control': 'no-store' }, extra || {}));
function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0; const parts = [];
    req.on('data', c => { size += c.length; if (size > 200e3) { reject(new HttpError(413, 'Requête trop volumineuse.')); req.destroy(); } else parts.push(c); });
    req.on('end', () => { try { resolve(parts.length ? JSON.parse(Buffer.concat(parts).toString('utf8')) : {}); } catch (e) { reject(new HttpError(400, 'Données illisibles.')); } });
    req.on('error', reject);
  });
}
/* Fichier envoyé tel quel (photo ou PDF d'ordonnance), 12 Mo au plus. */
function readRaw(req, limit) {
  return new Promise((resolve, reject) => {
    let size = 0; const parts = [];
    req.on('data', c => { size += c.length; if (size > limit) { reject(new HttpError(413, 'Fichier trop volumineux (12 Mo au plus).')); req.destroy(); } else parts.push(c); });
    req.on('end', () => resolve(Buffer.concat(parts)));
    req.on('error', reject);
  });
}
function sniff(buf) {
  if (buf.length > 3 && buf[0] === 0xFF && buf[1] === 0xD8 && buf[2] === 0xFF) return ['image/jpeg', '.jpg'];
  if (buf.length > 8 && buf.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]))) return ['image/png', '.png'];
  if (buf.length > 5 && buf.slice(0, 5).toString('latin1') === '%PDF-') return ['application/pdf', '.pdf'];
  if (buf.length > 12 && buf.slice(4, 8).toString('latin1') === 'ftyp' && /hei[cfsm]|mif1/.test(buf.slice(8, 12).toString('latin1'))) return ['image/heic', '.heic'];
  return null;
}
function cookies(req) { const o = {}; (req.headers.cookie || '').split(';').forEach(p => { const i = p.indexOf('='); if (i > 0) o[p.slice(0, i).trim()] = decodeURIComponent(p.slice(i + 1).trim()); }); return o; }
function clientIp(req) { return String(req.headers['x-real-ip'] || (req.headers['x-forwarded-for'] || '').split(',')[0] || req.socket.remoteAddress || '').trim(); }
function sessionCookie(token, maxAge) {
  return 'mp_sid=' + token + '; Path=' + BASE + '; HttpOnly; SameSite=Lax; Max-Age=' + maxAge + (SECURE ? '; Secure' : '');
}
function currentUser(req) {
  const t = cookies(req).mp_sid; if (!t) return null;
  const s = q('SELECT user_id, expires_at FROM sessions WHERE token_hash=?').get(sha(t));
  if (!s || s.expires_at < Date.now()) return null;
  const u = q('SELECT id,login,name,role,pharmacy_id,must_change,active FROM users WHERE id=?').get(s.user_id);
  return u && u.active ? u : null;
}
const isStaff = u => u.role === 'admin' || u.role === 'equipe';
function needStaff(u) { if (!isStaff(u)) fail(403, 'Action réservée à l\'équipe du parc.'); }
function needAdmin(u) { if (u.role !== 'admin') fail(403, 'Action réservée à l\'administrateur.'); }
function publicUser(u) {
  const ph = u.pharmacy_id ? q('SELECT id,name,commune FROM pharmacies WHERE id=?').get(u.pharmacy_id) : null;
  return { id: u.id, login: u.login, name: u.name, role: u.role, pharmacy: ph, must_change: !!u.must_change };
}

/* Limitation des tentatives de connexion : 8 échecs par adresse et identifiant en 15 minutes. */
const attempts = new Map();
function tooMany(key) { const a = attempts.get(key); return a && a.n >= 8 && Date.now() - a.t < 15 * 60e3; }
function failAttempt(key) { const a = attempts.get(key); if (!a || Date.now() - a.t > 15 * 60e3) attempts.set(key, { n: 1, t: Date.now() }); else a.n++; }
setInterval(() => { const now = Date.now(); for (const [k, a] of attempts) if (now - a.t > 15 * 60e3) attempts.delete(k); }, 600e3).unref();

/* ---------- Accès aux données ---------- */
function openRental(eqId) { return q('SELECT * FROM rentals WHERE equipment_id=? AND end_date IS NULL').get(eqId); }
function equipmentFor(u, id) {
  const e = q('SELECT * FROM equipment WHERE id=?').get(Number(id));
  if (!e) fail(404, 'Équipement introuvable.');
  if (!isStaff(u)) {
    const r = openRental(e.id);
    if (!r || r.pharmacy_id !== u.pharmacy_id) fail(404, 'Équipement introuvable.');
  }
  return e;
}
function patientNames(ids) {
  const m = new Map(); if (!ids.length) return m;
  for (const p of q('SELECT id, name FROM patients WHERE id IN (' + ids.map(() => '?').join(',') + ')').all(...ids)) m.set(p.id, dec(p.name));
  return m;
}
/* Remplace {p} par le nom du bénéficiaire de la location (déchiffré à l'affichage seulement). */
function eventTexts(rows) {
  const rids = [...new Set(rows.map(r => r.rental_id).filter(Boolean))];
  const rp = new Map(); if (rids.length) for (const r of q('SELECT id, patient_id FROM rentals WHERE id IN (' + rids.map(() => '?').join(',') + ')').all(...rids)) rp.set(r.id, r.patient_id);
  const names = patientNames([...new Set(rp.values())]);
  return rows.map(r => r.text.includes('{p}') ? r.text.split('{p}').join(names.get(rp.get(r.rental_id)) || 'bénéficiaire') : r.text);
}
function addEvent(eqId, rentalId, text, u, photoId) { q('INSERT INTO events(equipment_id,rental_id,at,text,user_name,photo_id) VALUES(?,?,?,?,?,?)').run(eqId, rentalId || null, nowStamp(), text, u ? u.name : '', photoId || null); }
function durLabel(n) { return n % 7 === 0 ? (n / 7 === 1 ? '1 semaine' : n / 7 + ' semaines') : n === 90 ? '3 mois' : n + ' jours'; }

function state(u) {
  const T = today(), staff = isStaff(u), ph = u.pharmacy_id;
  const pharmacies = staff ? q('SELECT id,name,commune,email FROM pharmacies ORDER BY name').all() : q('SELECT id,name,commune,email FROM pharmacies WHERE id=?').all(ph);
  const eqRows = staff ? q(`SELECT e.*, r.id rental_id, r.patient_id, r.pharmacy_id, r.start_date, r.planned_end
      FROM equipment e LEFT JOIN rentals r ON r.equipment_id=e.id AND r.end_date IS NULL ORDER BY e.ref`).all()
    : q(`SELECT e.*, r.id rental_id, r.patient_id, r.pharmacy_id, r.start_date, r.planned_end
      FROM equipment e JOIN rentals r ON r.equipment_id=e.id AND r.end_date IS NULL WHERE r.pharmacy_id=? ORDER BY e.ref`).all(ph);
  const closedDays = new Map();
  if (staff) for (const r of q(`SELECT equipment_id, SUM(julianday(end_date)-julianday(start_date)) d FROM rentals WHERE end_date IS NOT NULL GROUP BY equipment_id`).all())
    closedDays.set(r.equipment_id, Math.round(r.d || 0));
  const evRows = staff
    ? q(`SELECT * FROM (SELECT ev.*, ROW_NUMBER() OVER (PARTITION BY equipment_id ORDER BY at DESC, id DESC) rn FROM events ev) WHERE rn<=8`).all()
    : q(`SELECT * FROM (SELECT ev.*, ROW_NUMBER() OVER (PARTITION BY ev.equipment_id ORDER BY ev.at DESC, ev.id DESC) rn FROM events ev
         JOIN rentals r ON r.id=ev.rental_id WHERE r.pharmacy_id=?) WHERE rn<=8`).all(ph);
  const evText = eventTexts(evRows); evRows.forEach((e, i) => { e.text = evText[i]; });
  const evs = new Map(); for (const e of evRows) { if (!evs.has(e.equipment_id)) evs.set(e.equipment_id, []); evs.get(e.equipment_id).push(e); }
  const scRows = staff
    ? q(`SELECT * FROM (SELECT s.*, ROW_NUMBER() OVER (PARTITION BY equipment_id ORDER BY at DESC, id DESC) rn FROM scans s) WHERE rn=1`).all()
    : q(`SELECT * FROM (SELECT s.*, ROW_NUMBER() OVER (PARTITION BY s.equipment_id ORDER BY s.at DESC, s.id DESC) rn FROM scans s
         JOIN rentals r ON r.id=s.rental_id WHERE r.pharmacy_id=?) WHERE rn=1`).all(ph);
  const scans = new Map(scRows.map(s => [s.equipment_id, s]));
  const phRows = staff
    ? q(`SELECT * FROM (SELECT p.*, ROW_NUMBER() OVER (PARTITION BY equipment_id ORDER BY at DESC, id DESC) rn FROM photos p) WHERE rn<=6`).all()
    : q(`SELECT * FROM (SELECT p.*, ROW_NUMBER() OVER (PARTITION BY p.equipment_id ORDER BY p.at DESC, p.id DESC) rn FROM photos p
         JOIN rentals r ON r.id=p.rental_id WHERE r.pharmacy_id=?) WHERE rn<=6`).all(ph);
  const photos = new Map(); for (const x of phRows) { if (!photos.has(x.equipment_id)) photos.set(x.equipment_id, []); photos.get(x.equipment_id).push({ id: x.id, at: x.at, by: x.user_name, kind: x.kind, lat: x.lat, lon: x.lon }); }
  const presc = new Map(q(`SELECT p.* FROM prescriptions p JOIN rentals r ON r.id=p.rental_id WHERE r.end_date IS NULL ${staff ? '' : 'AND r.pharmacy_id=?'}`)
    .all(...(staff ? [] : [ph])).map(p => [p.rental_id, { date: p.presc_date, valid: p.valid_until || null, ref: p.ref, at: p.at, by: p.user_name }]));
  const docs = new Map();
  for (const d of q(`SELECT d.id, d.rental_id, d.filename, d.mime, d.size, d.at, d.user_name FROM documents d JOIN rentals r ON r.id=d.rental_id
      WHERE r.end_date IS NULL ${staff ? '' : 'AND r.pharmacy_id=?'} ORDER BY d.at`).all(...(staff ? [] : [ph]))) {
    if (!docs.has(d.rental_id)) docs.set(d.rental_id, []);
    docs.get(d.rental_id).push({ id: d.id, name: d.filename, mime: d.mime, size: d.size, at: d.at, by: d.user_name });
  }
  const equipment = eqRows.map(e => {
    const o = {
      id: e.id, ref: e.ref, name: e.name, brand: e.brand, kind: e.kind, photo: e.photo, catalog: e.catalog, week_price: e.week_price,
      status: e.status, since: e.status === 'loc' && e.start_date ? e.start_date : e.status_since, next_check: e.next_check,
      patient_id: e.patient_id || null, pharmacy_id: e.pharmacy_id || null, planned_end: e.planned_end || null,
      rental_id: e.rental_id || null, documents: e.rental_id ? (docs.get(e.rental_id) || []) : [],
      prescription: e.rental_id ? (presc.get(e.rental_id) || null) : null,
      photos: photos.get(e.id) || [],
      events: (evs.get(e.id) || []).map(v => ({ id: v.id, at: v.at, text: v.text, by: v.user_name, photo: v.photo_id || null })),
      last_scan: scans.has(e.id) ? (s => ({ at: s.at, by: s.user_name, lat: s.lat, lon: s.lon, accuracy: s.accuracy, source: s.source }))(scans.get(e.id)) : null
    };
    if (staff) Object.assign(o, { buy_price: e.buy_price, buy_estimated: !!e.buy_estimated, rented_days: e.prior_days + (closedDays.get(e.id) || 0), link: e.link });
    return o;
  });
  const closed = (staff ? q(`SELECT r.*, e.ref, e.name, e.photo, e.kind FROM rentals r JOIN equipment e ON e.id=r.equipment_id WHERE r.end_date IS NOT NULL ORDER BY r.end_date DESC LIMIT 200`).all()
    : q(`SELECT r.*, e.ref, e.name, e.photo, e.kind FROM rentals r JOIN equipment e ON e.id=r.equipment_id WHERE r.end_date IS NOT NULL AND r.pharmacy_id=? ORDER BY r.end_date DESC LIMIT 200`).all(ph))
    .map(r => ({ id: r.id, equipment: { id: r.equipment_id, ref: r.ref, name: r.name, photo: r.photo, kind: r.kind, week_price: r.week_price },
      patient_id: r.patient_id, pharmacy_id: r.pharmacy_id, start: r.start_date, end: r.end_date, amount: Math.round(r.week_price * diffDays(r.start_date, r.end_date) / 7) }));
  const pIds = new Set(equipment.filter(e => e.patient_id).map(e => e.patient_id).concat(closed.map(c => c.patient_id)));
  const patients = (staff ? q('SELECT * FROM patients').all() : q('SELECT * FROM patients').all().filter(p => pIds.has(p.id)))
    .map(p => ({ id: p.id, name: dec(p.name), address: dec(p.address), commune: p.commune, phone: dec(p.phone), lat: p.lat, lon: p.lon, anonymized: !!p.anonymized }))
    .sort((a, b) => a.name.localeCompare(b.name, 'fr'));
  return { me: publicUser(u), documents_enabled: DOCUMENTS_ENABLED, today: T, link_base: setting('link_base', PUBLIC_URL), communes: Object.keys(COMMUNES), pharmacies, patients, equipment, closed };
}

/* Facturation : jours de location compris dans le mois (le jour du retour n'est pas facturé). */
function billing(u, month, pharmacyId) {
  if (!/^\d{4}-\d{2}$/.test(month || '')) fail(400, 'Mois invalide.');
  const ms = month + '-01', next = addDays(addDays(ms, 31).slice(0, 7) + '-01', 0), T = today();
  const ph = isStaff(u) ? (pharmacyId ? Number(pharmacyId) : null) : u.pharmacy_id;
  const rows = q(`SELECT r.*, e.ref, e.name eq_name, f.name pharmacy, pr.presc_date, pr.ref presc_ref FROM rentals r
      JOIN equipment e ON e.id=r.equipment_id JOIN pharmacies f ON f.id=r.pharmacy_id
      LEFT JOIN prescriptions pr ON pr.rental_id=r.id
      WHERE r.start_date < ? AND (r.end_date IS NULL OR r.end_date > ?) ${ph ? 'AND r.pharmacy_id=?' : ''}
      ORDER BY f.name, e.ref`).all(...(ph ? [next, ms, ph] : [next, ms]));
  const names = patientNames([...new Set(rows.map(r => r.patient_id))]);
  rows.forEach(r => { r.patient = names.get(r.patient_id) || ''; });
  rows.sort((a, b) => a.pharmacy.localeCompare(b.pharmacy, 'fr') || a.patient.localeCompare(b.patient, 'fr') || a.ref.localeCompare(b.ref));
  const lines = rows.map(r => {
    const from = r.start_date > ms ? r.start_date : ms;
    const until = r.end_date && r.end_date < next ? r.end_date : next;
    const days = Math.max(0, diffDays(from, until));
    return { rental_id: r.id, pharmacy_id: r.pharmacy_id, pharmacy: r.pharmacy, patient: r.patient, ref: r.ref, equipment: r.eq_name,
      from, to: addDays(until, -1), days, week_price: r.week_price, amount: Math.round(r.week_price * days / 7), open: !r.end_date,
      presc_date: r.presc_date || null, presc_ref: r.presc_ref || '' };
  }).filter(l => l.days > 0);
  return { month, provisional: next > T, total: lines.reduce((a, l) => a + l.amount, 0), lines };
}
function billingCsv(b) {
  const esc = v => '"' + String(v).replace(/"/g, '""') + '"';
  const fr = d => d.split('-').reverse().join('/');
  const head = ['Pharmacie', 'Bénéficiaire', 'Référence', 'Équipement', 'Du', 'Au', 'Jours', 'Tarif hebdo XPF', 'Montant XPF', 'Location en cours', 'Ordonnance du', 'N° interne ordonnance'];
  const rows = b.lines.map(l => [l.pharmacy, l.patient, l.ref, l.equipment, fr(l.from), fr(l.to), l.days, l.week_price, l.amount, l.open ? 'oui' : 'non', l.presc_date ? fr(l.presc_date) : 'non vérifiée', l.presc_ref]);
  rows.push(['Total', '', '', '', '', '', '', '', b.total, '', '', '']);
  return '﻿' + [head].concat(rows).map(r => r.map(esc).join(';')).join('\r\n') + '\r\n';
}

/* ---------- API ---------- */
async function api(req, res, route, url) {
  const m = req.method;
  const upload = m === 'POST' && /^(rentals\/\d+\/documents|equipment\/\d+\/photos)$/.test(route);
  if (m === 'POST') {
    if (upload ? req.headers['x-mediparc'] !== '1' : !/application\/json/.test(req.headers['content-type'] || '')) fail(415, 'Format de requête non accepté.');
    const origin = req.headers.origin;
    if (origin) { let h = ''; try { h = new URL(origin).host; } catch (e) {} if (h !== req.headers.host) fail(403, 'Origine refusée.'); }
  }
  const body = m === 'POST' && !upload ? await readBody(req) : {};

  if (route === 'login' && m === 'POST') {
    const login = String(body.login || '').trim().toLowerCase(), key = clientIp(req) + '|' + login;
    if (tooMany(key)) fail(429, 'Trop de tentatives. Réessayez dans 15 minutes.');
    const u = q('SELECT * FROM users WHERE login=?').get(login);
    if (!u || !u.active || !checkPassword(String(body.password || ''), u.pass_hash)) { failAttempt(key); fail(401, 'Identifiant ou mot de passe incorrect.'); }
    attempts.delete(key);
    const token = crypto.randomBytes(32).toString('base64url');
    q('INSERT INTO sessions(token_hash,user_id,expires_at,created_at) VALUES(?,?,?,?)').run(sha(token), u.id, Date.now() + SESSION_DAYS * 864e5, nowStamp());
    q('UPDATE users SET last_login=? WHERE id=?').run(nowStamp(), u.id);
    return json(req, res, 200, { me: publicUser(u) }, { 'Set-Cookie': sessionCookie(token, SESSION_DAYS * 86400) });
  }
  if (route === 'logout' && m === 'POST') {
    const t = cookies(req).mp_sid; if (t) q('DELETE FROM sessions WHERE token_hash=?').run(sha(t));
    return json(req, res, 200, { ok: true }, { 'Set-Cookie': sessionCookie('', 0) });
  }

  const guide = route.match(/^guides\/(pharmacie|administrateur)\.pdf$/);
  const sendGuide = n => {
    const f = path.join(ROOT, 'guides', 'guide-' + n + '.pdf'); if (!fs.existsSync(f)) fail(404, 'Guide introuvable.');
    return send(req, res, 200, fs.readFileSync(f), 'application/pdf', { 'Cache-Control': 'private, max-age=3600',
      'Content-Disposition': 'attachment; filename="Guide-MediParc-' + (n === 'pharmacie' ? 'Pharmacie' : 'Administrateur') + '.pdf"' });
  };
  if (guide && m === 'GET' && guide[1] === 'pharmacie') return sendGuide('pharmacie');
  const u = currentUser(req);
  if (!u) fail(401, 'Connexion requise.');
  if (guide && m === 'GET') { needStaff(u); return sendGuide('administrateur'); }
  if (route === 'me' && m === 'GET') return json(req, res, 200, { me: publicUser(u) });
  if (route === 'password' && m === 'POST') {
    const full = q('SELECT pass_hash FROM users WHERE id=?').get(u.id);
    if (!checkPassword(String(body.current || ''), full.pass_hash)) fail(400, 'Le mot de passe actuel est incorrect.');
    const pb = passwordProblem(body.next); if (pb) fail(400, pb);
    if (body.next === body.current) fail(400, 'Choisissez un mot de passe différent de l\'actuel.');
    const keep = sha(cookies(req).mp_sid || '');
    tx(() => { q('UPDATE users SET pass_hash=?, must_change=0 WHERE id=?').run(hashPassword(body.next), u.id); q('DELETE FROM sessions WHERE user_id=? AND token_hash<>?').run(u.id, keep); });
    return json(req, res, 200, { me: publicUser(Object.assign({}, u, { must_change: 0 })) });
  }
  if (u.must_change) fail(403, 'Changez votre mot de passe provisoire pour continuer.');

  if (route === 'state' && m === 'GET') return json(req, res, 200, state(u));

  let mm;
  if ((mm = route.match(/^equipment\/(\d+)$/)) && m === 'GET') {
    const e = equipmentFor(u, mm[1]);
    const evs = isStaff(u) ? q('SELECT id,at,text,rental_id,photo_id,user_name by_ FROM events WHERE equipment_id=? ORDER BY at DESC, id DESC').all(e.id)
        : q('SELECT ev.id,ev.at,ev.text,ev.rental_id,ev.photo_id,ev.user_name by_ FROM events ev JOIN rentals r ON r.id=ev.rental_id WHERE ev.equipment_id=? AND r.pharmacy_id=? ORDER BY ev.at DESC, ev.id DESC').all(e.id, u.pharmacy_id);
    const sc = isStaff(u) ? q('SELECT at,user_name,lat,lon,accuracy,source FROM scans WHERE equipment_id=? ORDER BY at DESC, id DESC LIMIT 20').all(e.id)
      : q('SELECT s.at,s.user_name,s.lat,s.lon,s.accuracy,s.source FROM scans s JOIN rentals r ON r.id=s.rental_id WHERE s.equipment_id=? AND r.pharmacy_id=? ORDER BY s.at DESC LIMIT 20').all(e.id, u.pharmacy_id);
    const pho = isStaff(u) ? q('SELECT id,at,user_name,kind,lat,lon FROM photos WHERE equipment_id=? ORDER BY at DESC, id DESC').all(e.id)
      : q('SELECT p.id,p.at,p.user_name,p.kind,p.lat,p.lon FROM photos p JOIN rentals r ON r.id=p.rental_id WHERE p.equipment_id=? AND r.pharmacy_id=? ORDER BY p.at DESC').all(e.id, u.pharmacy_id);
    const tx2 = eventTexts(evs);
    return json(req, res, 200, { events: evs.map((v, i) => ({ id: v.id, at: v.at, text: tx2[i], by: v.by_, photo: v.photo_id || null })), scans: sc,
      photos: pho.map(x => ({ id: x.id, at: x.at, by: x.user_name, kind: x.kind, lat: x.lat, lon: x.lon })) });
  }
  if ((mm = route.match(/^equipment\/(\d+)\/action$/)) && m === 'POST') {
    needStaff(u);
    const e = equipmentFor(u, mm[1]), T = today(), a = body.action;
    tx(() => {
      const r = openRental(e.id);
      if (a === 'return') {
        if (e.status !== 'loc' || !r) fail(409, 'Cet équipement n\'est pas en location.');
        q('UPDATE rentals SET end_date=? WHERE id=?').run(T, r.id);
        q("UPDATE equipment SET status='desinf', status_since=? WHERE id=?").run(T, e.id);
        addEvent(e.id, r.id, 'Retour de location ({p}), en attente de désinfection', u);
      } else if (a === 'clean') {
        if (e.status !== 'desinf') fail(409, 'Cet équipement n\'est pas en attente de désinfection.');
        q("UPDATE equipment SET status='dispo', status_since=? WHERE id=?").run(T, e.id);
        addEvent(e.id, null, 'Désinfection validée, remis en stock', u);
      } else if (a === 'repair') {
        if (e.status !== 'maint') fail(409, 'Cet équipement n\'est pas en maintenance.');
        q("UPDATE equipment SET status='dispo', status_since=?, next_check=CASE WHEN next_check<? THEN ? ELSE next_check END WHERE id=?").run(T, T, addDays(T, 365), e.id);
        addEvent(e.id, null, 'Maintenance clôturée, contrôle conforme', u);
      } else if (a === 'fault') {
        if (e.status === 'maint') fail(409, 'Cet équipement est déjà en maintenance.');
        if (r) q('UPDATE rentals SET end_date=? WHERE id=?').run(T, r.id);
        q("UPDATE equipment SET status='maint', status_since=? WHERE id=?").run(T, e.id);
        addEvent(e.id, r ? r.id : null, 'Panne signalée, envoyé à l\'atelier', u);
      } else fail(400, 'Action inconnue.');
    });
    return json(req, res, 200, { ok: true });
  }
  if (route === 'rentals' && m === 'POST') {
    needStaff(u);
    const e = equipmentFor(u, body.equipment), days = Number(body.days);
    if (e.status !== 'dispo') fail(409, 'Cet équipement n\'est pas disponible.');
    if (![7, 14, 28, 90].includes(days)) fail(400, 'Durée invalide.');
    const p = q('SELECT * FROM patients WHERE id=?').get(Number(body.patient)); if (!p) fail(400, 'Bénéficiaire introuvable.');
    const f = q('SELECT * FROM pharmacies WHERE id=?').get(Number(body.pharmacy)); if (!f) fail(400, 'Pharmacie introuvable.');
    const T = today();
    tx(() => {
      const rid = Number(q('INSERT INTO rentals(equipment_id,patient_id,pharmacy_id,start_date,planned_end,week_price,created_by) VALUES(?,?,?,?,?,?,?)')
        .run(e.id, p.id, f.id, T, addDays(T, days), e.week_price, u.name).lastInsertRowid);
      q("UPDATE equipment SET status='loc', status_since=? WHERE id=?").run(T, e.id);
      addEvent(e.id, rid, 'Livré chez {p} par la ' + f.name + ' pour ' + durLabel(days), u);
    });
    return json(req, res, 200, { ok: true });
  }
  if (route === 'rentals/extend' && m === 'POST') {
    needStaff(u);
    const days = Number(body.days) || 7; if (days < 1 || days > 365) fail(400, 'Durée invalide.');
    const list = body.patient ? q('SELECT * FROM rentals WHERE patient_id=? AND end_date IS NULL').all(Number(body.patient))
      : [openRental(equipmentFor(u, body.equipment).id)].filter(Boolean);
    if (!list.length) fail(409, 'Aucune location en cours à prolonger.');
    tx(() => list.forEach(r => { q('UPDATE rentals SET planned_end=? WHERE id=?').run(addDays(r.planned_end, days), r.id); addEvent(r.equipment_id, r.id, 'Location prolongée de ' + durLabel(days), u); }));
    return json(req, res, 200, { ok: true, count: list.length });
  }
  if ((mm = route.match(/^equipment\/(\d+)\/link$/)) && m === 'POST') {
    needStaff(u);
    const e = equipmentFor(u, mm[1]); let link = String(body.link || '').trim();
    if (link) { try { const x = new URL(link); if (!/^https?:$/.test(x.protocol)) throw 0; } catch (z) { fail(400, 'Lien invalide.'); } }
    tx(() => {
      if (link) for (const o of q("SELECT id FROM equipment WHERE id<>? AND lower(rtrim(link,'/'))=lower(rtrim(?,'/'))").all(e.id, link)) {
        q("UPDATE equipment SET link='' WHERE id=?").run(o.id); addEvent(o.id, null, 'Puce NFC réattribuée à ' + e.ref, u);
      }
      q('UPDATE equipment SET link=? WHERE id=?').run(link, e.id);
      addEvent(e.id, null, link ? 'Puce NFC associée' : 'Puce NFC retirée', u);
    });
    return json(req, res, 200, { ok: true });
  }
  if (route === 'links/reset' && m === 'POST') {
    needStaff(u);
    if (body.mode === 'clear') q("UPDATE equipment SET link=''").run();
    else if (body.mode === 'default') q('UPDATE equipment SET link=?||ref').run(setting('link_base', PUBLIC_URL));
    else fail(400, 'Mode inconnu.');
    return json(req, res, 200, { ok: true });
  }
  if (route === 'settings' && m === 'POST') {
    needAdmin(u);
    let b = String(body.link_base || '').trim();
    try { const x = new URL(b); if (!/^https?:$/.test(x.protocol)) throw 0; } catch (z) { fail(400, 'Adresse invalide.'); }
    if (!/[\/#=]$/.test(b)) b += '/';
    const old = setting('link_base', PUBLIC_URL);
    tx(() => { q('UPDATE equipment SET link=?||ref WHERE link=?||ref').run(b, old); setSetting('link_base', b); });
    return json(req, res, 200, { ok: true });
  }
  if (route === 'scans' && m === 'POST') {
    const e = equipmentFor(u, body.equipment), r = openRental(e.id);
    const num = (v, lo, hi) => (typeof v === 'number' && isFinite(v) && v >= lo && v <= hi) ? v : null;
    const lat = num(body.lat, -90, 90), lon = num(body.lon, -180, 180);
    const src = ['nfc', 'lien', 'saisie'].includes(body.source) ? body.source : 'nfc';
    q('INSERT INTO scans(equipment_id,rental_id,at,user_id,user_name,lat,lon,accuracy,source) VALUES(?,?,?,?,?,?,?,?,?)')
      .run(e.id, r ? r.id : null, nowStamp(), u.id, u.name, lat, lat === null ? null : lon, lat === null ? null : num(body.accuracy, 0, 1e6), src);
    return json(req, res, 200, { ok: true });
  }
  if ((mm = route.match(/^equipment\/(\d+)\/photos$/)) && m === 'POST') {
    const e = equipmentFor(u, mm[1]), r = openRental(e.id);
    const kind = PHOTO_KINDS[req.headers['x-kind']] ? req.headers['x-kind'] : 'etat';
    const buf = await readRaw(req, 8 * 1024 * 1024);
    const t = sniff(buf); if (!t || !/^image\/(jpeg|png)$/.test(t[0])) fail(415, 'Envoyez une photo (JPEG ou PNG).');
    const num = (v, lo, hi) => { const n = parseFloat(v); return isFinite(n) && n >= lo && n <= hi ? n : null; };
    const lat = num(req.headers['x-lat'], -90, 90), lon = lat === null ? null : num(req.headers['x-lon'], -180, 180);
    const file = crypto.randomBytes(16).toString('hex') + t[1];
    fs.writeFileSync(path.join(PHOTOS, file), buf, { mode: 0o600 });
    const at = nowStamp();
    const id = Number(q('INSERT INTO photos(equipment_id,rental_id,at,user_id,user_name,kind,lat,lon,accuracy,file,size) VALUES(?,?,?,?,?,?,?,?,?,?,?)')
      .run(e.id, r ? r.id : null, at, u.id, u.name, kind, lat, lon, lat === null ? null : num(req.headers['x-acc'], 0, 1e6), file, buf.length).lastInsertRowid);
    addEvent(e.id, r ? r.id : null, 'Photo du matériel (' + PHOTO_KINDS[kind] + ')', u, id);
    return json(req, res, 200, { id, at });
  }
  if ((mm = route.match(/^photos\/(\d+)$/)) && m === 'GET') {
    const x = q('SELECT p.*, r.pharmacy_id FROM photos p LEFT JOIN rentals r ON r.id=p.rental_id WHERE p.id=?').get(Number(mm[1]));
    if (!x || (!isStaff(u) && x.pharmacy_id !== u.pharmacy_id)) fail(404, 'Photo introuvable.');
    return send(req, res, 200, fs.readFileSync(path.join(PHOTOS, x.file)), /\.png$/.test(x.file) ? 'image/png' : 'image/jpeg',
      { 'Cache-Control': 'private, max-age=86400', 'Content-Disposition': 'inline; filename="photo-' + x.id + (/\.png$/.test(x.file) ? '.png' : '.jpg') + '"', 'Content-Security-Policy': "sandbox; default-src 'none'; img-src 'self'" });
  }
  if ((mm = route.match(/^photos\/(\d+)\/delete$/)) && m === 'POST') {
    needStaff(u);
    const x = q('SELECT * FROM photos WHERE id=?').get(Number(mm[1])); if (!x) fail(404, 'Photo introuvable.');
    tx(() => { q('DELETE FROM photos WHERE id=?').run(x.id); q('UPDATE events SET photo_id=NULL WHERE photo_id=?').run(x.id); addEvent(x.equipment_id, x.rental_id, 'Photo du ' + x.at.split(' ')[0].split('-').reverse().join('/') + ' supprimée', u); });
    try { fs.unlinkSync(path.join(PHOTOS, x.file)); } catch (e) {}
    return json(req, res, 200, { ok: true });
  }
  if ((mm = route.match(/^rentals\/(\d+)\/documents$/)) && m === 'POST') {
    if (!DOCUMENTS_ENABLED) fail(403, 'Dépôt de documents désactivé : ce serveur n\'est pas certifié pour héberger des données de santé.');
    const r = q('SELECT * FROM rentals WHERE id=?').get(Number(mm[1]));
    if (!r || (!isStaff(u) && r.pharmacy_id !== u.pharmacy_id)) fail(404, 'Location introuvable.');
    if (q('SELECT COUNT(*) n FROM documents WHERE rental_id=?').get(r.id).n >= 10) fail(409, 'Dix documents au plus par location.');
    const buf = await readRaw(req, 12 * 1024 * 1024);
    const t = sniff(buf); if (!t) fail(415, 'Format non accepté : envoyez une photo (JPEG, PNG, HEIC) ou un PDF.');
    let name = decodeURIComponent(String(req.headers['x-filename'] || 'ordonnance')).replace(/[\u0000-\u001f\\/:*?"<>|]+/g, ' ').trim().slice(0, 100) || 'ordonnance';
    if (!name.toLowerCase().endsWith(t[1])) name = name.replace(/\.[a-z0-9]{2,5}$/i, '') + t[1];
    const file = crypto.randomBytes(16).toString('hex') + t[1];
    fs.writeFileSync(path.join(DOCS, file), buf, { mode: 0o600 });
    const id = Number(q('INSERT INTO documents(rental_id,filename,mime,size,file,at,user_name) VALUES(?,?,?,?,?,?,?)').run(r.id, name, t[0], buf.length, file, nowStamp(), u.name).lastInsertRowid);
    addEvent(r.equipment_id, r.id, 'Ordonnance ajoutée (' + name + ')', u);
    return json(req, res, 200, { id });
  }
  if ((mm = route.match(/^rentals\/(\d+)\/prescription(\/delete)?$/)) && m === 'POST') {
    const r = q('SELECT * FROM rentals WHERE id=?').get(Number(mm[1]));
    if (!r || (!isStaff(u) && r.pharmacy_id !== u.pharmacy_id)) fail(404, 'Location introuvable.');
    if (r.end_date) fail(409, 'Location terminée.');
    if (mm[2]) {
      tx(() => { q('DELETE FROM prescriptions WHERE rental_id=?').run(r.id); addEvent(r.equipment_id, r.id, 'Vérification de l\'ordonnance annulée', u); });
      return json(req, res, 200, { ok: true });
    }
    if (body.attest !== true) fail(400, 'Confirmez que la pharmacie détient l\'ordonnance.');
    const d = String(body.date || '');
    if (!isDate(d) || d > today() || d < addDays(today(), -400)) fail(400, 'Date d\'ordonnance invalide.');
    const ref = String(body.ref || '').trim().slice(0, 80);
    if (/[^\p{L}\p{N} ._\/-]/u.test(ref)) fail(400, 'Le numéro interne ne peut contenir que des lettres, chiffres, espaces et . _ / -');
    const v = String(body.valid_until || '');
    if (!isDate(v)) fail(400, 'Indiquez jusqu\'à quand l\'ordonnance est valable.');
    if (v < d) fail(400, 'La fin de validité doit être après la date de l\'ordonnance.');
    if (v > addDays(d, 400)) fail(400, 'Validité trop longue : 13 mois au plus après la date de l\'ordonnance.');
    const before = q('SELECT presc_date FROM prescriptions WHERE rental_id=?').get(r.id);
    const fr = x => x.split('-').reverse().join('/');
    tx(() => {
      q(`INSERT INTO prescriptions(rental_id,presc_date,valid_until,ref,at,user_name) VALUES(?,?,?,?,?,?) ON CONFLICT(rental_id) DO UPDATE SET
         presc_date=excluded.presc_date, valid_until=excluded.valid_until, ref=excluded.ref, at=excluded.at, user_name=excluded.user_name`).run(r.id, d, v, ref, nowStamp(), u.name);
      addEvent(r.equipment_id, r.id, (before && before.presc_date !== d ? 'Nouvelle ordonnance vérifiée' : 'Ordonnance vérifiée') + ' par la pharmacie (ordonnance du ' + fr(d) + ', valable jusqu\'au ' + fr(v) + (ref ? ', n° ' + ref : '') + ')', u);
    });
    return json(req, res, 200, { ok: true });
  }
  if ((mm = route.match(/^documents\/(\d+)$/)) && m === 'GET') {
    const d = q('SELECT d.*, r.pharmacy_id FROM documents d JOIN rentals r ON r.id=d.rental_id WHERE d.id=?').get(Number(mm[1]));
    if (!d || (!isStaff(u) && d.pharmacy_id !== u.pharmacy_id)) fail(404, 'Document introuvable.');
    const disp = (url.searchParams.get('dl') ? 'attachment' : 'inline') + "; filename*=UTF-8''" + encodeURIComponent(d.filename);
    return send(req, res, 200, fs.readFileSync(path.join(DOCS, d.file)), d.mime, { 'Cache-Control': 'private, no-store', 'Content-Disposition': disp, 'Content-Security-Policy': 'sandbox; default-src \'none\'; img-src \'self\'; style-src \'unsafe-inline\'; plugin-types application/pdf' });
  }
  if ((mm = route.match(/^documents\/(\d+)\/delete$/)) && m === 'POST') {
    const d = q('SELECT d.*, r.pharmacy_id, r.equipment_id, r.end_date FROM documents d JOIN rentals r ON r.id=d.rental_id WHERE d.id=?').get(Number(mm[1]));
    if (!d || (!isStaff(u) && d.pharmacy_id !== u.pharmacy_id)) fail(404, 'Document introuvable.');
    if (d.end_date && !isStaff(u)) fail(409, 'Location terminée : document conservé.');
    tx(() => { q('DELETE FROM documents WHERE id=?').run(d.id); addEvent(d.equipment_id, d.rental_id, 'Ordonnance retirée (' + d.filename + ')', u); });
    try { fs.unlinkSync(path.join(DOCS, d.file)); } catch (e) {}
    return json(req, res, 200, { ok: true });
  }
  if (route === 'billing' && m === 'GET') return json(req, res, 200, billing(u, url.searchParams.get('month'), url.searchParams.get('pharmacy')));
  if (route === 'billing.csv' && m === 'GET') {
    const b = billing(u, url.searchParams.get('month'), url.searchParams.get('pharmacy'));
    return send(req, res, 200, billingCsv(b), 'text/csv; charset=utf-8', { 'Cache-Control': 'no-store', 'Content-Disposition': 'attachment; filename="facturation-' + b.month + '.csv"' });
  }
  if (route === 'patients' && m === 'POST') {
    needStaff(u);
    const name = String(body.name || '').trim(), commune = String(body.commune || '').trim();
    if (name.length < 2) fail(400, 'Indiquez le nom du bénéficiaire.');
    const c = COMMUNES[commune]; if (!c) fail(400, 'Choisissez une commune.');
    const phone = String(body.phone || '').trim();
    if (phone && !/^\+?[0-9 .-]{6,20}$/.test(phone)) fail(400, 'Numéro de téléphone invalide.');
    const id = Number(q('INSERT INTO patients(name,address,commune,phone,lat,lon,created_at) VALUES(?,?,?,?,?,?,?)')
      .run(enc(name.slice(0, 120)), enc(String(body.address || '').trim().slice(0, 200)), commune, enc(phone), c[0], c[1], nowStamp()).lastInsertRowid);
    return json(req, res, 200, { id });
  }
  if (route === 'pharmacies' && m === 'POST') {
    needAdmin(u);
    const name = String(body.name || '').trim(); if (name.length < 2) fail(400, 'Indiquez le nom de la pharmacie.');
    const id = Number(q('INSERT INTO pharmacies(name,commune,created_at) VALUES(?,?,?)').run(name.slice(0, 120), String(body.commune || '').trim().slice(0, 80), nowStamp()).lastInsertRowid);
    return json(req, res, 200, { id });
  }
  if ((mm = route.match(/^pharmacies\/(\d+|me)\/email$/)) && m === 'POST') {
    const id = mm[1] === 'me' ? u.pharmacy_id : Number(mm[1]);
    if (mm[1] !== 'me') needAdmin(u); else if (!id) fail(403, 'Réservé aux comptes pharmacie.');
    if (!q('SELECT id FROM pharmacies WHERE id=?').get(id)) fail(404, 'Pharmacie introuvable.');
    const raw = String(body.email || '').trim(), list = emailsOf(raw);
    if (raw && list.length !== raw.split(/[,;\s]+/).filter(Boolean).length) fail(400, 'Adresse e-mail invalide. Séparez plusieurs adresses par une virgule.');
    if (list.length > 5) fail(400, 'Cinq adresses au plus.');
    q('UPDATE pharmacies SET email=? WHERE id=?').run(list.join(', '), id);
    return json(req, res, 200, { email: list.join(', ') });
  }
  if (route === 'mail' && m === 'GET') {
    needAdmin(u);
    let log = null; try { log = JSON.parse(setting('mail_log', 'null')); } catch (e) {}
    return json(req, res, 200, Object.assign(mailer.info(), { enabled: setting('mail_enabled', '1') === '1', hour: Number(setting('mail_hour', '7')), last_run: setting('mail_last_run', null), log }));
  }
  if (route === 'mail/settings' && m === 'POST') {
    needAdmin(u);
    if (typeof body.enabled === 'boolean') setSetting('mail_enabled', body.enabled ? '1' : '0');
    if (body.hour !== undefined) { const hh = Number(body.hour); if (!Number.isInteger(hh) || hh < 5 || hh > 20) fail(400, 'Heure invalide (5 à 20 h).'); setSetting('mail_hour', String(hh)); }
    return json(req, res, 200, { ok: true });
  }
  if (route === 'mail/test' && m === 'POST') {
    needAdmin(u);
    const to = emailsOf(body.to); if (!to.length) fail(400, 'Adresse e-mail invalide.');
    try { await mailer.send({ to, subject: 'Test des e-mails MédiParc NFC', text: 'Cet e-mail confirme que l\'envoi automatique fonctionne.', html: '<p>Cet e-mail confirme que l\'envoi automatique des rappels <b>MédiParc NFC</b> fonctionne.</p>' }); }
    catch (e) { fail(502, e.message); }
    return json(req, res, 200, { ok: true });
  }
  if (route === 'mail/run' && m === 'POST') { needAdmin(u); return json(req, res, 200, await runReminders(true)); }
  if (route === 'mail/preview' && m === 'GET') {
    needAdmin(u);
    return json(req, res, 200, { pharmacies: q('SELECT * FROM pharmacies ORDER BY name').all().map(f => ({ name: f.name, email: f.email, items: pendingReminders(f.id).map(i => ({ kind: MAIL_KINDS[i.kind], ref: i.ref, eq: i.eq, who: i.who, when: i.when })) })) });
  }
  if (route === 'users' && m === 'GET') {
    needAdmin(u);
    return json(req, res, 200, { users: q('SELECT u.id,u.login,u.name,u.role,u.pharmacy_id,u.active,u.must_change,u.last_login,f.name pharmacy FROM users u LEFT JOIN pharmacies f ON f.id=u.pharmacy_id ORDER BY u.role, u.name').all() });
  }
  if (route === 'users' && m === 'POST') {
    needAdmin(u);
    const login = String(body.login || '').trim().toLowerCase(), name = String(body.name || '').trim(), role = body.role;
    if (!/^[a-z0-9._-]{3,40}$/.test(login)) fail(400, 'Identifiant : 3 à 40 caractères parmi lettres minuscules, chiffres, point, tiret.');
    if (name.length < 2) fail(400, 'Indiquez le nom de la personne.');
    if (!['admin', 'equipe', 'pharmacie'].includes(role)) fail(400, 'Rôle inconnu.');
    let ph = null;
    if (role === 'pharmacie') { ph = Number(body.pharmacy); if (!ph || !q('SELECT id FROM pharmacies WHERE id=?').get(ph)) fail(400, 'Choisissez la pharmacie de ce compte.'); }
    if (q('SELECT id FROM users WHERE login=?').get(login)) fail(409, 'Cet identifiant existe déjà.');
    const pw = tempPassword();
    q('INSERT INTO users(login,name,role,pharmacy_id,pass_hash,must_change,created_at) VALUES(?,?,?,?,?,1,?)').run(login, name.slice(0, 120), role, ph, hashPassword(pw), nowStamp());
    return json(req, res, 200, { login, password: pw });
  }
  if ((mm = route.match(/^users\/(\d+)\/(reset|active)$/)) && m === 'POST') {
    needAdmin(u);
    const t = q('SELECT * FROM users WHERE id=?').get(Number(mm[1])); if (!t) fail(404, 'Compte introuvable.');
    if (mm[2] === 'reset') {
      const pw = tempPassword();
      tx(() => { q('UPDATE users SET pass_hash=?, must_change=1 WHERE id=?').run(hashPassword(pw), t.id); q('DELETE FROM sessions WHERE user_id=?').run(t.id); });
      return json(req, res, 200, { login: t.login, password: pw });
    }
    if (t.id === u.id) fail(400, 'Vous ne pouvez pas désactiver votre propre compte.');
    const active = body.active ? 1 : 0;
    tx(() => { q('UPDATE users SET active=? WHERE id=?').run(active, t.id); if (!active) q('DELETE FROM sessions WHERE user_id=?').run(t.id); });
    return json(req, res, 200, { ok: true });
  }
  fail(404, 'Adresse inconnue.');
}

/* ---------- Fichiers du site ---------- */
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.jpg': 'image/jpeg', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.json': 'application/json', '.ico': 'image/x-icon' };
const CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; " +
  "img-src 'self' data: blob:; connect-src 'self'; manifest-src 'self'; worker-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'";
function serveFile(req, res, rel) {
  let f = path.normalize(path.join(SITE, rel));
  if (!f.startsWith(SITE)) return send(req, res, 404, 'Introuvable', 'text/plain; charset=utf-8');
  let st = null; try { st = fs.statSync(f); } catch (e) {}
  if (!st || st.isDirectory()) {
    if (path.extname(rel)) return send(req, res, 404, 'Introuvable', 'text/plain; charset=utf-8');
    f = path.join(SITE, 'index.html');
  }
  const ext = path.extname(f), type = TYPES[ext] || 'application/octet-stream';
  const nocache = ext === '.html' || path.basename(f) === 'sw.js';
  const extra = { 'Cache-Control': nocache ? 'no-cache' : 'public, max-age=86400' };
  if (ext === '.html') Object.assign(extra, { 'Content-Security-Policy': CSP, 'X-Frame-Options': 'DENY', 'Permissions-Policy': 'geolocation=(self), camera=(), microphone=()' });
  if (path.basename(f) === 'sw.js') extra['Service-Worker-Allowed'] = BASE + '/';
  send(req, res, 200, fs.readFileSync(f), type, extra);
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://local');
    let p = decodeURIComponent(url.pathname);
    if (p === BASE) { res.writeHead(301, { Location: BASE + '/' }); return res.end(); }
    if (!p.startsWith(BASE + '/')) return send(req, res, 404, 'Introuvable', 'text/plain; charset=utf-8');
    p = p.slice(BASE.length + 1);
    if (p.startsWith('api/')) return await api(req, res, p.slice(4).replace(/\/+$/, ''), url);
    if (req.method !== 'GET' && req.method !== 'HEAD') return send(req, res, 405, 'Méthode non autorisée', 'text/plain; charset=utf-8');
    return serveFile(req, res, p || 'index.html');
  } catch (e) {
    if (e instanceof HttpError) return json(req, res, e.status, { error: e.message });
    console.error(e);
    return json(req, res, 500, { error: 'Erreur du serveur. Réessayez dans un instant.' });
  }
});
server.listen(PORT, () => console.log('MédiParc NFC prêt sur le port ' + PORT + ' (' + BASE + '/)'));
process.on('SIGTERM', () => { server.close(); try { db.close(); } catch (e) {} process.exit(0); });
