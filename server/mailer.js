'use strict';
/*
 * Envoi d'e-mails sans dépendance externe.
 * MAIL_PROVIDER = resend | brevo | smtp (vide : envoi désactivé)
 *   resend / brevo : MAIL_API_KEY
 *   smtp           : SMTP_HOST, SMTP_PORT (587 STARTTLS ou 465 TLS), SMTP_USER, SMTP_PASS
 * MAIL_FROM   : expéditeur, ex. « MédiParc <rappels@manaprocess.com> » (adresse d'un domaine vérifié chez le service)
 * MAIL_REPLY_TO (facultatif)
 */
const net = require('node:net');
const tls = require('node:tls');
const crypto = require('node:crypto');
const os = require('node:os');

const P = (process.env.MAIL_PROVIDER || '').toLowerCase();
const FROM = process.env.MAIL_FROM || '';
const REPLY = process.env.MAIL_REPLY_TO || '';

function parseAddr(a) { const m = /^\s*(.*?)\s*<([^>]+)>\s*$/.exec(a || ''); return m ? { name: m[1].replace(/^"|"$/g, ''), email: m[2] } : { name: '', email: String(a || '').trim() }; }
function configured() {
  if (!FROM) return false;
  if (P === 'resend' || P === 'brevo') return !!process.env.MAIL_API_KEY;
  if (P === 'smtp') return !!(process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS);
  return false;
}
function info() { return { provider: P || null, configured: configured(), from: FROM ? parseAddr(FROM).email : null }; }

async function viaResend(m) {
  const r = await fetch(process.env.MAIL_API_URL || 'https://api.resend.com/emails', {
    method: 'POST', headers: { Authorization: 'Bearer ' + process.env.MAIL_API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: FROM, to: m.to, subject: m.subject, html: m.html, text: m.text, reply_to: REPLY || undefined })
  });
  if (!r.ok) throw new Error('Resend ' + r.status + ' : ' + (await r.text()).slice(0, 200));
}
async function viaBrevo(m) {
  const f = parseAddr(FROM);
  const r = await fetch(process.env.MAIL_API_URL || 'https://api.brevo.com/v3/smtp/email', {
    method: 'POST', headers: { 'api-key': process.env.MAIL_API_KEY, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ sender: { name: f.name || undefined, email: f.email }, to: m.to.map(e => ({ email: e })), subject: m.subject,
      htmlContent: m.html, textContent: m.text, replyTo: REPLY ? { email: parseAddr(REPLY).email } : undefined })
  });
  if (!r.ok) throw new Error('Brevo ' + r.status + ' : ' + (await r.text()).slice(0, 200));
}

/* Client SMTP minimal (EHLO, STARTTLS, AUTH PLAIN/LOGIN, envoi d'un message multipart). */
function smtpSend(m) {
  const host = process.env.SMTP_HOST, port = Number(process.env.SMTP_PORT || 587), user = process.env.SMTP_USER, pass = process.env.SMTP_PASS;
  const b64 = s => Buffer.from(s, 'utf8').toString('base64');
  const enc = s => /^[\x20-\x7e]*$/.test(s) ? s : '=?UTF-8?B?' + b64(s) + '?=';
  const f = parseAddr(FROM), bnd = 'mp-' + crypto.randomBytes(8).toString('hex');
  const wrap = s => b64(s).replace(/.{1,76}/g, '$&\r\n');
  const msg = [
    'From: ' + (f.name ? enc(f.name) + ' <' + f.email + '>' : f.email), 'To: ' + m.to.join(', '), 'Subject: ' + enc(m.subject),
    REPLY ? 'Reply-To: ' + parseAddr(REPLY).email : null, 'Date: ' + new Date().toUTCString(),
    'Message-ID: <' + crypto.randomBytes(12).toString('hex') + '@' + (f.email.split('@')[1] || 'mediparc') + '>', 'MIME-Version: 1.0',
    'Content-Type: multipart/alternative; boundary="' + bnd + '"', '',
    '--' + bnd, 'Content-Type: text/plain; charset=utf-8', 'Content-Transfer-Encoding: base64', '', wrap(m.text),
    '--' + bnd, 'Content-Type: text/html; charset=utf-8', 'Content-Transfer-Encoding: base64', '', wrap(m.html), '--' + bnd + '--', ''
  ].filter(l => l !== null).join('\r\n');
  return new Promise((resolve, reject) => {
    let sock = port === 465 ? tls.connect({ host, port, servername: host }) : net.connect({ host, port });
    let buf = '', step = 0, waiting = null;
    const timer = setTimeout(() => { sock.destroy(); reject(new Error('SMTP : délai dépassé')); }, 30000);
    const fail = e => { clearTimeout(timer); try { sock.destroy(); } catch (x) {} reject(e); };
    const read = () => new Promise(res => { waiting = res; pump(); });
    function pump() {
      const lines = buf.split('\r\n'); const i = lines.findIndex(l => /^\d{3} /.test(l));
      if (i >= 0 && waiting) { const reply = lines.slice(0, i + 1).join('\n'); buf = lines.slice(i + 1).join('\r\n'); const w = waiting; waiting = null; w(reply); }
    }
    const attach = s => { s.on('data', d => { buf += d.toString('utf8'); pump(); }); s.on('error', fail); };
    attach(sock);
    const cmd = async (c, ok) => { if (c !== null) sock.write(c + '\r\n'); const r = await read(); if (!ok.test(r.slice(0, 3))) throw new Error('SMTP : ' + r.split('\n').pop()); return r; };
    (async () => {
      await cmd(null, /^220/);
      let ehlo = await cmd('EHLO ' + os.hostname(), /^250/);
      if (port !== 465 && /STARTTLS/i.test(ehlo)) {
        await cmd('STARTTLS', /^220/);
        sock.removeAllListeners('data');
        sock = tls.connect({ socket: sock, servername: host }); attach(sock);
        await new Promise((res, rej) => { sock.once('secureConnect', res); sock.once('error', rej); });
        ehlo = await cmd('EHLO ' + os.hostname(), /^250/);
      }
      if (/AUTH[^\n]*PLAIN/i.test(ehlo)) await cmd('AUTH PLAIN ' + Buffer.from('\0' + user + '\0' + pass).toString('base64'), /^235/);
      else { await cmd('AUTH LOGIN', /^334/); await cmd(b64(user), /^334/); await cmd(b64(pass), /^235/); }
      await cmd('MAIL FROM:<' + f.email + '>', /^250/);
      for (const t of m.to) await cmd('RCPT TO:<' + t + '>', /^25[01]/);
      await cmd('DATA', /^354/);
      await cmd(msg.replace(/\r\n\./g, '\r\n..') + '\r\n.', /^250/);
      sock.write('QUIT\r\n'); clearTimeout(timer); sock.end(); resolve();
    })().catch(fail);
  });
}

async function send(m) {
  if (!configured()) throw new Error('Envoi d\'e-mails non configuré sur le serveur.');
  m.to = (Array.isArray(m.to) ? m.to : [m.to]).filter(Boolean);
  if (!m.to.length) throw new Error('Aucun destinataire.');
  if (P === 'resend') return viaResend(m);
  if (P === 'brevo') return viaBrevo(m);
  return smtpSend(m);
}
module.exports = { send, info, configured };
