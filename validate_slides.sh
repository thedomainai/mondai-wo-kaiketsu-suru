#!/bin/bash

echo "=== SLIDE DECK QUALITY AUDIT ==="
echo "Checking 73 slides for release readiness..."
echo ""

# 1. Font consistency
echo "1. FONT CONSISTENCY"
echo "-------------------"
missing_noto=0
missing_grotesk=0

for f in slide_*.html; do
  if ! grep -q "Noto Sans JP" "$f"; then
    echo "  ❌ $f: Missing 'Noto Sans JP'"
    ((missing_noto++))
  fi
  if ! grep -q "Space Grotesk" "$f"; then
    echo "  ❌ $f: Missing 'Space Grotesk'"
    ((missing_grotesk++))
  fi
done

if [ $missing_noto -eq 0 ] && [ $missing_grotesk -eq 0 ]; then
  echo "  ✅ All slides have both required fonts"
else
  echo "  ⚠️  $missing_noto slides missing Noto Sans JP, $missing_grotesk missing Space Grotesk"
fi
echo ""

# 2. CSS/JS references
echo "2. CSS/JS REFERENCES"
echo "-------------------"
missing_css=0
missing_js=0

for f in slide_*.html; do
  if ! grep -q 'slides\.css' "$f"; then
    echo "  ❌ $f: Missing slides.css reference"
    ((missing_css++))
  fi
  if ! grep -q 'slides\.js' "$f"; then
    echo "  ❌ $f: Missing slides.js reference"
    ((missing_js++))
  fi
done

if [ $missing_css -eq 0 ] && [ $missing_js -eq 0 ]; then
  echo "  ✅ All slides reference slides.css and slides.js"
else
  echo "  ⚠️  $missing_css missing CSS, $missing_js missing JS"
fi
echo ""

# 3. DOCTYPE and title
echo "3. HTML STRUCTURE"
echo "----------------"
missing_doctype=0
missing_title=0

for f in slide_*.html; do
  if ! grep -q "DOCTYPE" "$f"; then
    echo "  ❌ $f: Missing DOCTYPE"
    ((missing_doctype++))
  fi
  if ! grep -q "<title>" "$f"; then
    echo "  ❌ $f: Missing <title> tag"
    ((missing_title++))
  fi
done

if [ $missing_doctype -eq 0 ] && [ $missing_title -eq 0 ]; then
  echo "  ✅ All slides have DOCTYPE and title"
else
  echo "  ⚠️  $missing_doctype missing DOCTYPE, $missing_title missing title"
fi
echo ""

# 4. Tag balance
echo "4. TAG BALANCE"
echo "-------------"
unbalanced=0

for f in slide_*.html; do
  div_open=$(grep -o "<div" "$f" | wc -l)
  div_close=$(grep -o "</div>" "$f" | wc -l)
  if [ "$div_open" -ne "$div_close" ]; then
    echo "  ❌ $f: Unbalanced divs (open=$div_open, close=$div_close)"
    ((unbalanced++))
  fi
done

if [ $unbalanced -eq 0 ]; then
  echo "  ✅ All slides have balanced <div> tags"
else
  echo "  ⚠️  $unbalanced slides with unbalanced tags"
fi
echo ""

# 5. Very small font sizes
echo "5. FONT SIZE CHECK"
echo "-----------------"
small_fonts=$(grep -rn 'font-size:[0-9]px' slide_*.html | wc -l)

if [ $small_fonts -gt 0 ]; then
  echo "  ⚠️  Found $small_fonts instances of single-digit font sizes (may be intentional):"
  grep -rn 'font-size:[0-9]px' slide_*.html | head -5
  echo "  ... (showing first 5)"
else
  echo "  ✅ No suspiciously small font sizes"
fi
echo ""

# 6. File size check
echo "6. FILE SIZE CHECK"
echo "-----------------"
echo "  Smallest files (potential empty content):"
wc -l slide_*.html | sort -n | head -10
echo ""

# 7. Large positioning values
echo "7. POSITIONING CHECK"
echo "-------------------"
large_pos=$(grep -rn 'top:[0-9]\{4,\}\|left:[0-9]\{4,\}' slide_*.html | wc -l)

if [ $large_pos -gt 0 ]; then
  echo "  ⚠️  Found $large_pos instances of 4+ digit positioning (may extend beyond 1280x720):"
  grep -rn 'top:[0-9]\{4,\}\|left:[0-9]\{4,\}' slide_*.html
else
  echo "  ✅ No positioning values exceed viewport"
fi
echo ""

# Summary
echo "=== SUMMARY ==="
total_issues=$((missing_noto + missing_grotesk + missing_css + missing_js + missing_doctype + missing_title + unbalanced))

if [ $total_issues -eq 0 ]; then
  echo "✅ All critical checks passed! Deck is release-ready."
else
  echo "⚠️  Found $total_issues critical issues that should be fixed before release."
fi
