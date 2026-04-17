import { readFileSync, writeFileSync, readdirSync, existsSync } from 'fs';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

const origDir = '/tmp/vr/original';
const currDir = '/tmp/vr/current';
const results = [];

const files = readdirSync(origDir).filter(f => f.endsWith('.png')).sort();

for (const file of files) {
  const origPath = `${origDir}/${file}`;
  const currPath = `${currDir}/${file}`;

  if (!existsSync(currPath)) {
    results.push({ file, status: 'missing_current', diffPercent: 100 });
    continue;
  }

  const origImg = PNG.sync.read(readFileSync(origPath));
  const currImg = PNG.sync.read(readFileSync(currPath));

  const { width, height } = origImg;

  if (currImg.width !== width || currImg.height !== height) {
    results.push({ file, status: 'size_mismatch', diffPercent: 100 });
    continue;
  }

  const diffPixels = pixelmatch(origImg.data, currImg.data, null, width, height, { threshold: 0.1 });
  const totalPixels = width * height;
  const diffPercent = (diffPixels / totalPixels * 100).toFixed(2);

  results.push({ file, status: 'compared', diffPercent: parseFloat(diffPercent), diffPixels });
}

// Sort by diff percentage descending
results.sort((a, b) => b.diffPercent - a.diffPercent);

console.log('=== Visual Regression Results ===\n');
console.log('Diff%    | Pixels   | Slide');
console.log('---------|----------|------------------');

let broken = 0, minor = 0, clean = 0;

for (const r of results) {
  const pct = String(r.diffPercent).padStart(7);
  const px = r.diffPixels ? String(r.diffPixels).padStart(8) : '     N/A';
  const flag = r.diffPercent > 5 ? ' *** BROKEN' : r.diffPercent > 1 ? ' * minor' : '';
  console.log(`${pct}% | ${px} | ${r.file}${flag}`);

  if (r.diffPercent > 5) broken++;
  else if (r.diffPercent > 1) minor++;
  else clean++;
}

console.log('\n=== Summary ===');
console.log(`Total: ${results.length} slides`);
console.log(`Broken (>5%): ${broken}`);
console.log(`Minor (1-5%): ${minor}`);
console.log(`Clean (<1%): ${clean}`);

// Save JSON for further analysis
writeFileSync('/tmp/vr/results.json', JSON.stringify(results, null, 2));
