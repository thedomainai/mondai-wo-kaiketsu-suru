# AI Slide System QA Report

- Deck: `問題を解決する`
- Total slides: `77`
- Findings: `6`

## Inventory

- `cover`: `1`
- `intro`: `6`
- `agenda`: `8`
- `divider`: `8`
- `center-title`: `5`
- `content`: `43`
- `summary`: `2`
- `closing`: `1`
- `cta`: `1`
- `qa`: `2`

## Findings

- **ERROR** `inline-header-reimplementation` `slide_15.html`: Content slides must not hand-roll header markup
- **ERROR** `missing-required-attr` `slide_15.html`: Missing `data-header-chapter` on slide container
- **ERROR** `missing-required-attr` `slide_15.html`: Missing `data-header-title` on slide container
- **ERROR** `missing-required-attr` `slide_15.html`: Missing `data-header-subtitle` on slide container
- **ERROR** `missing-required-marker` `slide_49.html`: Expected marker `LOGICAL THINKING TRAINING`
- **ERROR** `missing-required-marker` `slide_50.html`: Expected marker `LOGICAL THINKING TRAINING`
