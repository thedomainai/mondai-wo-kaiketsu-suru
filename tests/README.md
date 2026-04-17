# Visual Regression Testing

This directory contains a visual regression testing tool for the slide deck.

## Setup

Install dependencies:

```bash
cd tests
npm install
```

## Usage

### 1. Take Baseline Screenshots

Before making any changes to the slides, capture baseline screenshots:

```bash
node visual-regression.mjs baseline
```

This creates PNG screenshots of all slides (1-81) in `tests/screenshots/baseline/`.

### 2. Make Changes

Edit your slide HTML files as needed.

### 3. Take Current Screenshots

After making changes, capture new screenshots:

```bash
node visual-regression.mjs current
```

This saves screenshots to `tests/screenshots/current/`.

### 4. Compare Screenshots

Compare the current screenshots against the baseline:

```bash
node visual-regression.mjs compare
```

This will:
- Generate pixel-diff images in `tests/screenshots/diff/`
- Report the percentage of pixels that changed for each slide
- Mark slides as PASS or FAIL based on the threshold (default: 0.5%)
- Exit with code 1 if any slides failed

## Advanced Options

### Test Specific Slide Range

```bash
node visual-regression.mjs --slides 1-10 baseline
node visual-regression.mjs --slides 1-10 current
node visual-regression.mjs --slides 1-10 compare
```

### Custom Threshold

```bash
node visual-regression.mjs --threshold 1.0 compare
```

This allows up to 1% of pixels to differ before marking a slide as failed.

### NPM Scripts

For convenience, you can use the npm scripts defined in `package.json`:

```bash
npm run test:baseline   # Take baseline screenshots
npm run test:current    # Take current screenshots
npm run test:compare    # Compare screenshots
npm run test:full       # Run current + compare
```

## Interpreting Results

### Example Output

```
🔍 Comparing screenshots...
   Threshold: 0.5% pixel difference

   slide_01: ✓  0.00%
   slide_02: ✓  0.12%
   slide_03: ✗  1.23% (threshold: 0.5%)
   ...

═══════════════════════════════════════════════════════════
SUMMARY
═══════════════════════════════════════════════════════════
Total slides:  81
Passed:        78 ✓
Failed:        3 ✗

Failed slides:
   slide_03: 1.23% (11,304 pixels)
   slide_15: 0.87% (8,022 pixels)
   slide_42: 2.45% (22,608 pixels)

Diff images saved to: tests/screenshots/diff
```

### Understanding Diff Images

The diff images (in `tests/screenshots/diff/`) highlight changed pixels in pink/red:
- **Pink pixels**: Areas that differ between baseline and current
- **Gray pixels**: Areas that are identical

### Common Causes of Failures

1. **Font rendering differences**: Different OS or browser versions may render fonts slightly differently
2. **Anti-aliasing**: Sub-pixel rendering can vary
3. **Date/time stamps**: If slides contain dynamic dates
4. **Random elements**: Any random colors, positions, etc.

### Threshold Selection

- **0.1%**: Very strict, catches tiny differences (may have false positives from font rendering)
- **0.5%**: Default, good balance for catching real visual changes
- **1.0%**: More lenient, ignores minor rendering differences
- **2.0%+**: Very lenient, only catches major layout changes

## Directory Structure

```
tests/
├── visual-regression.mjs    # Main testing script
├── package.json             # Dependencies
├── README.md                # This file
└── screenshots/
    ├── baseline/            # Original screenshots
    │   ├── slide_01.png
    │   ├── slide_02.png
    │   └── ...
    ├── current/             # Current screenshots
    │   ├── slide_01.png
    │   └── ...
    └── diff/                # Diff visualizations
        ├── slide_01.png
        └── ...
```

## Technical Details

- **Screenshot size**: 1280×720px (exact slide dimensions)
- **Browser**: Puppeteer (Chromium)
- **Comparison**: Pixel-by-pixel using pixelmatch
- **Font loading**: 500ms wait after page load for Google Fonts
- **Image format**: PNG (lossless)

## Troubleshooting

### "Baseline screenshots not found"

Run `node visual-regression.mjs baseline` first.

### "Current screenshots not found"

Run `node visual-regression.mjs current` before comparing.

### Slides missing from results

Check that the slide HTML files exist in `/slides/`. The tool automatically skips missing files.

### High diff percentages on all slides

This may indicate:
- Font loading issues (check network connectivity)
- Different Chromium version
- Need to retake baseline screenshots

## Integration with CI/CD

You can integrate this into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: cd tests && npm install

- name: Take current screenshots
  run: cd tests && node visual-regression.mjs current

- name: Compare screenshots
  run: cd tests && node visual-regression.mjs compare

- name: Upload diff images
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: visual-regression-diffs
    path: tests/screenshots/diff/
```

The script exits with code 1 if any slides fail, which will fail the CI build.
