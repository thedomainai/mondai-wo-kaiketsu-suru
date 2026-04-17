import puppeteer from 'puppeteer';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import { resolve } from 'path';

const SLIDES_DIR = resolve(import.meta.dirname, '../slides');
const TOKENIZED_DIR = '/tmp/vr/tokenized';
const ORIGINAL_DIR = '/tmp/vr/original';

mkdirSync(TOKENIZED_DIR, { recursive: true });

async function captureAll() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  for (let i = 1; i <= 69; i++) {
    const num = String(i).padStart(2, '0');
    const filePath = `${SLIDES_DIR}/slide_${num}.html`;
    const outPath = `${TOKENIZED_DIR}/${num}.png`;

    await page.goto(`file://${filePath}`, { waitUntil: 'networkidle0', timeout: 15000 });
    await page.screenshot({ path: outPath, fullPage: false });
  }

  await browser.close();
  console.log('Screenshots captured.');
}

function compareAll() {
  const results = [];

  for (let i = 1; i <= 69; i++) {
    const num = String(i).padStart(2, '0');
    const origPath = `${ORIGINAL_DIR}/${num}.png`;
    const tokPath = `${TOKENIZED_DIR}/${num}.png`;

    if (!existsSync(origPath) || !existsSync(tokPath)) {
      results.push({ slide: num, status: 'missing', diffPercent: -1 });
      continue;
    }

    const origImg = PNG.sync.read(readFileSync(origPath));
    const tokImg = PNG.sync.read(readFileSync(tokPath));

    const { width, height } = origImg;

    if (tokImg.width !== width || tokImg.height !== height) {
      results.push({ slide: num, status: 'size_mismatch', diffPercent: 100 });
      continue;
    }

    const diffPixels = pixelmatch(origImg.data, tokImg.data, null, width, height, { threshold: 0.1 });
    const diffPercent = parseFloat((diffPixels / (width * height) * 100).toFixed(2));

    results.push({ slide: num, status: 'ok', diffPercent, diffPixels });
  }

  results.sort((a, b) => b.diffPercent - a.diffPercent);

  console.log('\n=== Tokenized vs Original Comparison ===\n');
  console.log('Diff%    | Pixels   | Slide');
  console.log('---------|----------|------');

  let broken = 0, minor = 0, clean = 0;

  for (const r of results) {
    const pct = String(r.diffPercent).padStart(7);
    const px = r.diffPixels !== undefined ? String(r.diffPixels).padStart(8) : '     N/A';
    const flag = r.diffPercent > 5 ? ' *** BROKEN' : r.diffPercent > 1 ? ' * minor' : '';
    console.log(`${pct}% | ${px} | slide_${r.slide}${flag}`);

    if (r.diffPercent > 5) broken++;
    else if (r.diffPercent > 1) minor++;
    else clean++;
  }

  console.log(`\n=== Summary ===`);
  console.log(`Broken (>5%): ${broken}`);
  console.log(`Minor (1-5%): ${minor}`);
  console.log(`Clean (<1%): ${clean}`);

  writeFileSync('/tmp/vr/tokenized-results.json', JSON.stringify(results, null, 2));
}

await captureAll();
compareAll();
