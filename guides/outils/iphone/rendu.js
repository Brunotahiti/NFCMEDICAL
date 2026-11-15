// Rendu des maquettes en images : node rendu.js <dossier html> <dossier des captures>
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [src, dst] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })).newPage();
  for (const f of fs.readdirSync(src).filter(f => f.endsWith('.html'))) {
    await p.goto('file://' + path.resolve(src, f)); await p.waitForTimeout(250);
    await p.screenshot({ path: path.join(dst, f.replace('.html', '.jpg')), type: 'jpeg', quality: 86 });
  }
  await b.close();
})();
