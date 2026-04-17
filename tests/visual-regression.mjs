#!/usr/bin/env node

/**
 * Visual Regression Testing Tool for Slide Deck
 *
 * This script captures screenshots of all slide HTML files and compares them
 * pixel-by-pixel to detect visual regressions.
 *
 * Usage:
 *   node visual-regression.mjs baseline                    # Take baseline screenshots
 *   node visual-regression.mjs current                     # Take current screenshots
 *   node visual-regression.mjs compare                     # Compare and report
 *   node visual-regression.mjs --slides 1-10 baseline      # Specific range
 *   node visual-regression.mjs --threshold 1.0 compare     # Custom threshold
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';
import pixelmatch from 'pixelmatch';
import { PNG } from 'pngjs';

// Directory setup
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '..');
const SLIDES_DIR = path.join(PROJECT_ROOT, 'slides');
const SCREENSHOTS_DIR = path.join(__dirname, 'screenshots');

// Default configuration
const DEFAULT_CONFIG = {
  viewport: { width: 1280, height: 720 },
  slideRange: { start: 1, end: 81 },
  threshold: 0.5, // percentage of pixels that can differ
  waitAfterLoad: 500, // ms to wait for fonts/rendering
};

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const config = { ...DEFAULT_CONFIG };
  let command = null;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--slides') {
      const range = args[++i];
      const [start, end] = range.split('-').map(Number);
      config.slideRange = { start, end };
    } else if (arg === '--threshold') {
      config.threshold = parseFloat(args[++i]);
    } else if (['baseline', 'current', 'compare'].includes(arg)) {
      command = arg;
    }
  }

  if (!command) {
    console.error('Error: Missing command (baseline, current, or compare)');
    console.error('Usage: node visual-regression.mjs [options] <command>');
    process.exit(1);
  }

  return { command, config };
}

/**
 * Ensure directory exists
 */
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * Get list of slide files in the specified range
 */
function getSlideFiles(config) {
  const { start, end } = config.slideRange;
  const slides = [];

  for (let i = start; i <= end; i++) {
    const slideNum = String(i).padStart(2, '0');
    const filename = `slide_${slideNum}.html`;
    const filepath = path.join(SLIDES_DIR, filename);

    if (fs.existsSync(filepath)) {
      slides.push({ number: i, filename, filepath });
    }
  }

  return slides;
}

/**
 * Take screenshot of a single slide
 */
async function captureSlide(browser, slide, outputPath) {
  const page = await browser.newPage();

  try {
    // Set viewport to exact slide dimensions
    await page.setViewport(DEFAULT_CONFIG.viewport);

    // Navigate to the slide file
    const fileUrl = `file://${slide.filepath}`;
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });

    // Wait for fonts to load and rendering to stabilize
    await page.waitForTimeout(DEFAULT_CONFIG.waitAfterLoad);

    // Take screenshot
    await page.screenshot({ path: outputPath, fullPage: false });

    return true;
  } catch (error) {
    console.error(`Error capturing slide ${slide.filename}:`, error.message);
    return false;
  } finally {
    await page.close();
  }
}

/**
 * Take screenshots of all slides
 */
async function captureScreenshots(type, config) {
  const slides = getSlideFiles(config);
  const outputDir = path.join(SCREENSHOTS_DIR, type);

  ensureDir(outputDir);

  console.log(`📸 Taking ${type} screenshots...`);
  console.log(`   Range: slides ${config.slideRange.start}-${config.slideRange.end}`);
  console.log(`   Output: ${outputDir}`);
  console.log('');

  const browser = await puppeteer.launch({ headless: 'new' });

  let successCount = 0;
  let failCount = 0;

  for (const slide of slides) {
    const slideNum = String(slide.number).padStart(2, '0');
    const outputPath = path.join(outputDir, `slide_${slideNum}.png`);

    process.stdout.write(`   Capturing slide_${slideNum}.html... `);

    const success = await captureSlide(browser, slide, outputPath);

    if (success) {
      console.log('✓');
      successCount++;
    } else {
      console.log('✗');
      failCount++;
    }
  }

  await browser.close();

  console.log('');
  console.log(`✅ Complete: ${successCount} screenshots saved`);
  if (failCount > 0) {
    console.log(`❌ Failed: ${failCount} screenshots`);
  }
}

/**
 * Compare two PNG images and return diff stats
 */
function compareImages(baselinePath, currentPath, diffPath) {
  const baseline = PNG.sync.read(fs.readFileSync(baselinePath));
  const current = PNG.sync.read(fs.readFileSync(currentPath));

  const { width, height } = baseline;
  const diff = new PNG({ width, height });

  // Perform pixel-by-pixel comparison
  const numDiffPixels = pixelmatch(
    baseline.data,
    current.data,
    diff.data,
    width,
    height,
    { threshold: 0.1 } // pixelmatch threshold (0-1, lower = more sensitive)
  );

  // Save diff image
  fs.writeFileSync(diffPath, PNG.sync.write(diff));

  // Calculate percentage
  const totalPixels = width * height;
  const diffPercent = (numDiffPixels / totalPixels) * 100;

  return {
    numDiffPixels,
    totalPixels,
    diffPercent: parseFloat(diffPercent.toFixed(4)),
  };
}

/**
 * Compare baseline and current screenshots
 */
async function compareScreenshots(config) {
  const slides = getSlideFiles(config);
  const baselineDir = path.join(SCREENSHOTS_DIR, 'baseline');
  const currentDir = path.join(SCREENSHOTS_DIR, 'current');
  const diffDir = path.join(SCREENSHOTS_DIR, 'diff');

  ensureDir(diffDir);

  // Check that baseline directory exists
  if (!fs.existsSync(baselineDir)) {
    console.error('❌ Error: Baseline screenshots not found.');
    console.error('   Run "node visual-regression.mjs baseline" first.');
    process.exit(1);
  }

  // Check that current directory exists
  if (!fs.existsSync(currentDir)) {
    console.error('❌ Error: Current screenshots not found.');
    console.error('   Run "node visual-regression.mjs current" first.');
    process.exit(1);
  }

  console.log(`🔍 Comparing screenshots...`);
  console.log(`   Threshold: ${config.threshold}% pixel difference`);
  console.log('');

  const results = [];
  let passCount = 0;
  let failCount = 0;

  for (const slide of slides) {
    const slideNum = String(slide.number).padStart(2, '0');
    const filename = `slide_${slideNum}.png`;

    const baselinePath = path.join(baselineDir, filename);
    const currentPath = path.join(currentDir, filename);
    const diffPath = path.join(diffDir, filename);

    // Skip if either file is missing
    if (!fs.existsSync(baselinePath)) {
      console.log(`   slide_${slideNum}: ⊘  (baseline missing)`);
      continue;
    }

    if (!fs.existsSync(currentPath)) {
      console.log(`   slide_${slideNum}: ⊘  (current missing)`);
      continue;
    }

    // Compare images
    const stats = compareImages(baselinePath, currentPath, diffPath);
    const passed = stats.diffPercent <= config.threshold;

    results.push({
      slide: slideNum,
      ...stats,
      passed,
    });

    if (passed) {
      passCount++;
      console.log(`   slide_${slideNum}: ✓  ${stats.diffPercent.toFixed(2)}%`);
    } else {
      failCount++;
      console.log(`   slide_${slideNum}: ✗  ${stats.diffPercent.toFixed(2)}% (threshold: ${config.threshold}%)`);
    }
  }

  // Print summary
  console.log('');
  console.log('═'.repeat(60));
  console.log('SUMMARY');
  console.log('═'.repeat(60));
  console.log(`Total slides:  ${results.length}`);
  console.log(`Passed:        ${passCount} ✓`);
  console.log(`Failed:        ${failCount} ✗`);
  console.log('');

  if (failCount > 0) {
    console.log('Failed slides:');
    results
      .filter(r => !r.passed)
      .forEach(r => {
        console.log(`   slide_${r.slide}: ${r.diffPercent.toFixed(2)}% (${r.numDiffPixels.toLocaleString()} pixels)`);
      });
    console.log('');
    console.log(`Diff images saved to: ${diffDir}`);
    process.exit(1);
  } else {
    console.log('✅ All slides passed!');
    process.exit(0);
  }
}

/**
 * Main entry point
 */
async function main() {
  const { command, config } = parseArgs();

  console.log('');
  console.log('═'.repeat(60));
  console.log('VISUAL REGRESSION TESTING');
  console.log('═'.repeat(60));
  console.log('');

  switch (command) {
    case 'baseline':
      await captureScreenshots('baseline', config);
      break;

    case 'current':
      await captureScreenshots('current', config);
      break;

    case 'compare':
      await compareScreenshots(config);
      break;
  }
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
