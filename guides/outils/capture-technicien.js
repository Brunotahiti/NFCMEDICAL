// Captures du guide technicien. Serveur de démonstration lancé sur http://localhost:3456 (voir README).
// Usage : node capture-technicien.js <dossier des captures> <photo de matériel.jpg>
const {chromium}=require('playwright');const B='http://localhost:3456/materiel/';
const O=process.argv[2].replace(/\/?$/,'/'),PHOTO=process.argv[3];
(async()=>{const b=await chromium.launch();const errs=[];
const c=await b.newContext({viewport:{width:430,height:932},deviceScaleFactor:2,geolocation:{latitude:-17.5352,longitude:-149.5694,accuracy:6},permissions:['geolocation']});
const p=await c.newPage();p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{document.addEventListener('DOMContentLoaded',()=>{const st=document.createElement('style');st.textContent='.toast{display:none!important}';document.head.appendChild(st);});
  /* Simulation de Web NFC (Chrome Android) pour illustrer la lecture et l'écriture. */
  window.__nfc=[];window.NDEFReader=class{constructor(){window.__nfc.push(this);}scan(o){this.sig=o&&o.signal;return Promise.resolve();}
    write(m,o){return new Promise((res,rej)=>{window.__writeDone=res;if(o&&o.signal)o.signal.addEventListener('abort',()=>rej(new DOMException('a','AbortError')));});}};
  window.__read=u=>{const r=window.__nfc[window.__nfc.length-1];r.onreading({message:{records:[{recordType:'url',data:new TextEncoder().encode(u)}]}});};});
const shot=async(n,w)=>{await p.waitForTimeout(w||450);await p.screenshot({path:O+n+'.jpg',type:'jpeg',quality:84});};
const el=async(sel,n)=>{const l=p.locator(sel).first();await l.scrollIntoViewIfNeeded();await p.waitForTimeout(350);await l.screenshot({path:O+n+'.jpg',type:'jpeg',quality:86});};
const secOf=t=>`section:has(.sec-h h2:has-text("${t}"))`;
const api=(path,body)=>p.evaluate(async([path,body])=>{const r=await fetch('/materiel/api/'+path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});return r.json();},[path,body]);
// admin crée le compte technicien
await p.goto(B);await p.waitForTimeout(600);await p.fill('#lg-login','admin');await p.fill('#lg-pass','AdminParc2026');await p.click('#f-login button[type=submit]');await p.waitForTimeout(1200);
const pw=(await api('users',{name:'Teiki Teriierooiterai',login:'teiki',role:'equipe'})).password;
await api('logout',{});
await p.goto(B);await p.waitForTimeout(600);await p.fill('#lg-login','teiki');await p.fill('#lg-pass',pw);await p.click('#f-login button[type=submit]');await p.waitForTimeout(700);
await p.fill('#pw-cur',pw);await p.fill('#pw-new','Technicien2026');await p.fill('#pw-new2','Technicien2026');await p.click('#f-pwd button[type=submit]');await p.waitForTimeout(1300);
await shot('t_home');
await p.click('[data-act=quick]');await shot('t_quick');
await p.click('.menu [data-act=scan]');await shot('t_scan',700);
await p.evaluate(()=>window.__read('https://manaprocess.cloud/materiel/LIT-0101'));await p.waitForTimeout(2600);
await p.evaluate(()=>document.querySelector('.dscroll').scrollTo(0,0));await shot('t_fiche');
await el('.kv','t_kv');
await p.click('[data-act=take-photo]');await p.waitForTimeout(300);await p.click('[data-pkind=livraison]');await p.waitForTimeout(200);
const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('[data-act=photo-shoot]')]);await fc.setFiles(PHOTO);await p.waitForTimeout(2800);
await el(secOf('Photos du matériel'),'t_photos');
await p.click('[data-act=program]');await shot('t_write',700);await p.evaluate(()=>window.__writeDone&&window.__writeDone());await p.waitForTimeout(1500);
await p.click('[data-act=back]');await p.waitForTimeout(400);
// désinfection
await p.click('.tabs [data-tab=ent]');await shot('t_ent');
await p.click('#sec-des .row');await p.waitForTimeout(1000);await p.evaluate(()=>document.querySelector('.dscroll').scrollTo(0,0));await shot('t_desinf');await p.click('[data-act=back]');await p.waitForTimeout(400);
await p.click('#sec-mnt .row');await p.waitForTimeout(1000);await p.evaluate(()=>document.querySelector('.dscroll').scrollTo(0,0));await shot('t_maint');await p.click('[data-act=back]');await p.waitForTimeout(400);
// contrôle à venir
await p.click('[data-cdays="30"]');await p.waitForTimeout(400);await p.click('#sec-ctl .row:nth-child(3)');await p.waitForTimeout(1000);
await el('.kv','t_check');
await p.click('[data-act=back]');await p.waitForTimeout(300);
console.log('erreurs:',errs);await b.close();})();
