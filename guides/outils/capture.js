const {chromium}=require('playwright');const B='http://localhost:3456/materiel/',D='/tmp/claude-0/-home-user-NFCMEDICAL/32d5afab-7c23-5fce-a572-344481db6cae/';
const O=D+'scratchpad/shots/';
(async()=>{const b=await chromium.launch();const errs=[];
const mk=async()=>{const c=await b.newContext({viewport:{width:430,height:932},deviceScaleFactor:2,geolocation:{latitude:-17.6352,longitude:-149.6071,accuracy:8},permissions:['geolocation']});
  const p=await c.newPage();p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{const st=document.createElement('style');st.textContent='.toast{display:none!important}';document.addEventListener('DOMContentLoaded',()=>document.head.appendChild(st));
    window.__files={};const fh=n=>({kind:'file',name:n,getFile:async()=>new File([window.__files[n]],n,{type:'application/pdf',lastModified:Date.now()})});
    const dir={name:'Ordonnances',queryPermission:async()=>'granted',requestPermission:async()=>'granted',values:function(){const ks=Object.keys(window.__files);let i=0;return {next:async()=>i<ks.length?{done:false,value:fh(ks[i++])}:{done:true}};},
      getFileHandle:async(n,o)=>{if(!(o&&o.create)&&!(n in window.__files))throw new DOMException('x','NotFoundError');return {createWritable:async()=>({write:async(bl)=>{window.__files[n]=bl;},close:async()=>{}})};}};
    window.showDirectoryPicker=async()=>dir;});
  return p;};
const shot=async(p,n,w)=>{await p.waitForTimeout(w||450);await p.screenshot({path:O+n+'.jpg',type:'jpeg',quality:84});};
const el=async(p,sel,n)=>{const l=p.locator(sel).first();await l.scrollIntoViewIfNeeded();await p.waitForTimeout(350);await l.screenshot({path:O+n+'.jpg',type:'jpeg',quality:86});};
const secOf=t=>`section:has(.sec-h h2:has-text("${t}"))`;
const login=async(p,l,p1,p2,pre)=>{await p.goto(B);await p.waitForTimeout(700);if(pre)await shot(p,pre+'login');await p.fill('#lg-login',l);await p.fill('#lg-pass',p1);await p.click('#f-login button[type=submit]');await p.waitForTimeout(700);
  if(await p.$('#pw-cur')){if(pre)await shot(p,pre+'pwd');await p.fill('#pw-cur',p1);await p.fill('#pw-new',p2);await p.fill('#pw-new2',p2);await p.click('#f-pwd button[type=submit]');await p.waitForTimeout(1300);}};
// ---------- ADMIN ----------
const a=await mk();await login(a,'admin','Provisoire2026','AdminParc2026','a_');
await shot(a,'a_home');
await a.evaluate(()=>document.querySelector('main').scrollTo(0,560));await shot(a,'a_home2');
const pw=await a.evaluate(async()=>{const r=await fetch('/materiel/api/users',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'Pharmacie du Lagon',login:'lagon',role:'pharmacie',pharmacy:1})});
  await fetch('/materiel/api/pharmacies/1/email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:'officine@lagon.pf'})});return (await r.json()).password;});
// photos sur LIT-0101
await a.goto(B+'LIT-0101');await a.waitForTimeout(1500);
for(const k of ['livraison','etat']){await a.click('[data-act=take-photo]');await a.waitForTimeout(300);await a.click('[data-pkind='+k+']');await a.waitForTimeout(200);
  const [fc]=await Promise.all([a.waitForEvent('filechooser'),a.click('[data-act=photo-shoot]')]);await fc.setFiles(D+'scratchpad/lit-real.jpg');await a.waitForTimeout(2600);}
await a.evaluate(()=>document.querySelector('.dscroll').scrollTo(0,0));await shot(a,'a_fiche_loc');
await a.click('[data-act=take-photo]');await shot(a,'a_photo_sheet');await a.click('.sheet [data-act=close-sheet]');
await el(a,secOf('Photos du matériel'),'a_photos');
await el(a,secOf('Historique'),'a_hist');
await a.click('[data-act=back]');await a.waitForTimeout(400);
// parc
await a.click('.tabs [data-tab=parc]');await shot(a,'a_parc');
await a.click('[data-mode=plan]');await shot(a,'a_plan');await a.click('[data-mode=stats]');await shot(a,'a_stats');await a.click('[data-mode=grid]');
await a.click('.st[data-filter=dispo]');await a.waitForTimeout(300);await a.click('#parc-list .card');await a.waitForTimeout(900);await shot(a,'a_fiche_dispo');
await a.click('[data-act=assign]');await shot(a,'a_assign');
await a.click('[data-act=new-pat]');await a.fill('#pa-name','Teva Teriitahi');await a.click('[data-sel=commune] [data-opt=Arue]');await a.fill('#pa-addr','Servitude Tama, PK 6');await a.fill('#pa-tel','87 99 88 77');await shot(a,'a_newpat');
await a.click('.sheet [data-act=close-sheet]').catch(()=>{});await a.keyboard.press('Escape');await a.waitForTimeout(300);await a.keyboard.press('Escape');await a.waitForTimeout(400);
// locations
await a.goto(B);await a.waitForTimeout(1200);
await a.click('.tabs [data-tab=loc]');await shot(a,'a_loc');
await a.click('[data-ltab=renew]');await shot(a,'a_renew');await a.click('[data-ltab=cur]');
await a.click('.tabs [data-tab=ent]');await shot(a,'a_ent');
await a.click('.tabs [data-tab=rap]');await shot(a,'a_rap');
await a.click('.chip[data-rtab=fact]');await a.waitForTimeout(900);await shot(a,'a_fact');
await a.click('.chip[data-rtab=exp]');await shot(a,'a_exp');
// quick + more
await a.click('[data-act=quick]');await shot(a,'a_quick');await a.click('.sheet [data-act=close-sheet]').catch(()=>{});await a.keyboard.press('Escape');
await a.click('.tabs [data-act=more]');await shot(a,'a_more');
await a.click('.menu [data-act=settings]');await a.waitForTimeout(700);await shot(a,'a_settings');
await a.click('#settings [data-tag]');await shot(a,'a_tag');await a.keyboard.press('Escape');await a.waitForTimeout(300);
await a.click('[data-act=close-settings]');await a.waitForTimeout(300);
await a.click('.tabs [data-act=more]');await a.waitForTimeout(300);await a.click('.menu [data-act=accounts]');await a.waitForTimeout(1300);await shot(a,'a_accounts');
await a.click('[data-act=new-user]');await a.fill('#u-name','Pharmacie Moana');await a.fill('#u-login','moana');await a.click('[data-sel=pharm] .chip:has-text("Moana")');await shot(a,'a_newuser');
await a.click('#f-user button[type=submit]');await a.waitForTimeout(800);await a.evaluate(()=>{const c=document.querySelector('.pwbox code');if(c)c.textContent='https://manaprocess.cloud/materiel/';});await shot(a,'a_newuser_pw',300);await a.keyboard.press('Escape');await a.waitForTimeout(300);
await el(a,'#settings '+secOf('E-mails de rappel'),'a_mail');
await a.click('[data-act=close-settings]');
// ---------- PHARMACIE ----------
const p=await mk();await login(p,'lagon',pw,'Lagon2026parc','p_');
await shot(p,'p_home');await p.evaluate(()=>document.querySelector('main').scrollTo(0,520));await shot(p,'p_home2');
await p.click('.tabs [data-tab=loc]');await shot(p,'p_loc');
await p.goto(B+'LIT-0101');await p.waitForTimeout(1800);await p.evaluate(()=>document.querySelector('.dscroll').scrollTo(0,0));await shot(p,'p_fiche');
await el(p,secOf('Ordonnance'),'p_ordo');
await el(p,secOf('Photos du matériel'),'p_photos');
const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('[data-act=scan-presc]')]);await fc.setFiles(D+'scratchpad/ordo-photo.jpg');await p.waitForTimeout(1500);await shot(p,'p_scan');
await p.click('[data-act=scan-save-dir]');await p.waitForTimeout(1200);
const t=new Date(),iso=t.toISOString().slice(0,10);await p.fill('#pr-date',iso);await p.click('[data-pvalid="6"]');await p.check('#pr-ok');await shot(p,'p_presc');
await p.click('#f-presc button[type=submit]');await p.waitForTimeout(1400);
await el(p,secOf('Ordonnance'),'p_ordo_ok');
await p.click('[data-act=view-presc]');await shot(p,'p_view',900);await p.keyboard.press('Escape');await p.waitForTimeout(300);
await el(p,secOf('Historique'),'p_hist');
await p.click('[data-act=back]');await p.waitForTimeout(400);
await p.click('.tabs [data-tab=fact]');await p.waitForTimeout(1000);await shot(p,'p_fact');
await p.click('.tabs [data-act=more]');await shot(p,'p_more');
await p.click('.menu [data-act=my-mail]');await shot(p,'p_mail');
console.log('erreurs:',errs);await b.close();})();
