# Design Tokens

## Runtime

- Format: `1280x720 HTML`
- Shared CSS SSOT: [`slides.css`](/private/tmp/slides/slides/slides.css)
- Shared JS SSOT: [`slides.js`](/private/tmp/slides/slides/slides.js)
- Canonical slide container: `.slide-container`

## Layout Geometry

### Shared header/footer

- `--header-band-height: 156px`
- `--header-pill-top: 20px`
- `--header-text-top: 28px`
- `--content-left: 80px`
- `--content-width: 1120px`
- `--header-copy-width: 1120px` (`--content-width` を参照)
- `--content-right: 1200px`
- `--content-center: 640px`
- Footer baseline: `top: 660px`, height `60px`
- Conclusion dock: `bottom: 60px` above footer, use `.ds-summary-dock`

### Section-first layout

- Detailed workflow SSOT: [`layout-sections.md`](/private/tmp/slides/docs/ai-slide-system/layout-sections.md)
- body の主要コンテンツは、まず親 wrapper と section skeleton を置いてから組む
- section の height / width / gap を grid / flex で先に決める
- object は owning section の内側で完結させる
- overlap や余白は section budget の再配分で解く
- absolute positioning は section 内の図解や micro-layout に限定する

### Background families

- `slide-theme-paper`
- `slide-theme-mist`
- `data-background="grain"`
- `data-background="halftone"`

Custom slide でも背景はこの family に寄せる。新規 background style を増やす前に既存 family へ吸収できないかを先に検討する。

## Typography Tokens

### Header / footer

- `--font-size-header-pill: 9px`
- `--font-size-header-chapter: 12px`
- `--font-size-header-title: 36px`
- `--letter-spacing-header-title: 1px`
- `--line-height-header-title: 1.2`
- `--font-size-header-subtitle: 14px`
- `--line-height-header-subtitle: 1.4`
- `--font-size-footer-meta: 11px`

### Center title

- `--font-size-center-chapter: 13px`
- `--font-size-center-title: 48px`
- `--font-size-center-subtitle: 22px`

### Cover / divider / agenda

- `--font-size-cover-title: 60px`
- `--font-size-cover-subtitle: 22px`
- `--font-size-divider-brand: 11px`
- `--font-size-divider-index: 160px`
- `--font-size-divider-kicker: 12px`
- `--font-size-divider-title: 60px`
- `--font-size-divider-subtitle: 18px`
- `--font-size-agenda-label: 11px`
- `--font-size-agenda-title: 52px`

### Vertical rhythm

- `--space-stack-lead-title: 6px`
- `--space-stack-title-body: 12px`
- `--space-stack-lead-title-loose: 36px`
- `--space-stack-title-body-loose: 24px`

lead-in (`eyebrow / kicker / label / num`) → title → body の距離は、この 4 token を SSOT にする。`stack-card` / `ds-card__head` / `ds-panel__head` の shared slot もこの scale に乗せる。局所修正で `padding-bottom` や生の `8px` を足して吸収しない。

### Optical gap（廃止）

optical gap 指示は受け入れない。「見た目で 48px」のような要求はスペーシングスケール上の最も近い値（`--sp-48`）に丸める。中間値の需要が 3 枚以上で出現した場合はスケール自体を見直す。

`.stack-optical` クラスは legacy として残すが、新規スライドでは使用しない。

## Color System

7段階のインクスケール + 背景 + アクセント。全スライドのハードコード値はこのトークンに集約済み。

### Ink (text/border)

| Token | Value | Semantic role |
|---|---|---|
| `--ink-100` | `#1a1a1a` | Primary text |
| `--ink-82` | `rgba(0,0,0,.82)` | Strong emphasis |
| `--ink-68` | `rgba(0,0,0,.68)` | Secondary text / body |
| `--ink-50` | `rgba(0,0,0,.50)` | Muted text |
| `--ink-34` | `rgba(0,0,0,.34)` | Eyebrow / label / kicker |
| `--ink-18` | `rgba(0,0,0,.18)` | Disabled / placeholder |
| `--ink-08` | `rgba(0,0,0,.08)` | Border light |
| `--ink-04` | `rgba(0,0,0,.04)` | Border subtle / divider |

### Surface

| Token | Value | Usage |
|---|---|---|
| `--surface-white` | `#ffffff` | Slide background |
| `--surface-mist` | `#f7f7f7` | Card flat / subtle bg |
| `--surface-card` | `#ffffff` | Card default bg |

### Accent

| Token | Value | Usage |
|---|---|---|
| `--accent-purple` | `#5a4970` | Accent (kicker, badges) — used in 13+ slides |
| `--accent-red` | `#9e3434` | Negative / warning |

## Typography Scale

| Token | px | Usage |
|---|---|---|
| `--fs-11` | 11 | Footer, small eyebrow |
| `--fs-12` | 12 | Eyebrow, labels |
| `--fs-13` | 13 | Body small, captions |
| `--fs-14` | 14 | Body, row values |
| `--fs-15` | 15 | Body default, card title |
| `--fs-16` | 16 | Body large, panel title |
| `--fs-17` | 17 | Body emphasis |
| `--fs-18` | 18 | Subtitle |
| `--fs-22` | 22 | Section subtitle |
| `--fs-24` | 24 | Section title |
| `--fs-30` | 30 | Title large |
| `--fs-34` | 34 | Display |
| `--fs-36` | 36 | Header title |
| `--fs-42` | 42 | Display large |
| `--fs-48` | 48 | Center title |

## Spacing Scale

4px ベースの 8 段スケール。

| Token | px | Usage |
|---|---|---|
| `--sp-4` | 4 | Micro gap |
| `--sp-8` | 8 | Tight gap |
| `--sp-12` | 12 | Default gap, lead→title |
| `--sp-16` | 16 | Section gap, title→body |
| `--sp-20` | 20 | Stage gap default |
| `--sp-24` | 24 | Loose gap |
| `--sp-32` | 32 | Section separator |
| `--sp-48` | 48 | Major section break |

## Shared UI Classes

### Structural (existing)

- `.slide-standard-header*` / `.slide-standard-footer*`
- `.slide-divider*` / `.slide-center-title*`
- `.agenda-panel*`
- `.stack` / `.stack-optical` (legacy)
- `.step-card*` / `.stack-card*` / `.number-card*`

### Design System (ds-* — new)

| Class | Role |
|---|---|
| `.ds-stage` | Main content area below header. Override with `--stage-top`, `--stage-gap` |
| `.ds-description` / `.ds-description__text` | Body top description strip. First child of `.ds-stage`. `--description-fs` (default `--fs-14`), `--description-color` (default `--ink-68`). Variant: `--inline` (no fill, bottom-border). |
| `.ds-stage--summary-reserve` | Reserve a fixed bottom zone for a docked conclusion / summary above the footer |
| `.ds-grid` `.ds-grid--2..5` | Grid layouts. Override with `--ds-grid-gap` |
| `.ds-stack` | Vertical stack. Child margins are reset; spacing is owned by parent `gap` via `--stack-gap` |
| `.ds-eyebrow` | Small label (Space Grotesk, 12px, ink-34) |
| `.ds-title` / `.ds-title--lg` / `.ds-title--xl` | Section titles (24/30/34px) |
| `.ds-title-sm` | Card/panel titles (15px) |
| `.ds-subtitle` | Subtitle/lead (18px, ink-50) |
| `.ds-body` / `.ds-body--sm` / `.ds-body--lg` | Body text (15/13/16px) |
| `.ds-number` | Large index number (Space Grotesk) |
| `.ds-kicker` | Accent-colored statement (purple, 15px bold) |
| `.ds-card` / `.ds-card--strong` / `.ds-card--flat` | Card component (flex column + gap). Head/body gap: `--card-gap` (default: `--space-stack-title-body`) |
| `.ds-card__head` / `.ds-card__head--loose` | Card head stack. eyebrow → title の距離を shared vertical-rhythm token で管理する |
| `.ds-card__body` | Card body slot. head の下に置く本文領域 |
| `.ds-panel` / `.ds-panel--strong` | Panel with slot structure: head → body. Head/body gap: `--panel-gap` (default: `--space-stack-title-body`) |
| `.ds-panel__head` / `.ds-panel__head--loose` | Panel head stack. label → title → sub の距離を shared vertical-rhythm token で管理する |
| `.ds-panel__label` / `.ds-panel__title` / `.ds-panel__sub` | Panel slots (label: eyebrow, title: heading, sub: supporting copy) |
| `.ds-rows` / `.ds-row` | Row list inside panels. Row: grid 2-col (key + value). `flex:1` for equal height distribution |
| `.ds-row--center` / `.ds-rows--center` | Row vertical alignment: center (default: start/top) |
| `.ds-comparison` | Parallel panels with subgrid row matching. `--panel-slots`, `--row-count` for track control |
| `.ds-comparison--cards` | Comparison layout for card-to-card contrast with aligned `head / media / body` tracks |
| `.ds-compare-card*` | Compare card slots: `__head`, `__badge`, `__copy`, `__media`, `__body` |
| `.ds-summary` / `.ds-summary--box` / `.ds-summary--tint` | Takeaway / summary block |
| `.ds-summary-dock` | Docked bottom conclusion block that sits above the standard footer |
| `.ds-flow-arrow` / `.ds-flow-arrow--down` | CSS-drawn connector arrow |
| `.ds-list` | Styled ordered/unordered list |
| `.ds-badge` / `--dark` / `--light` / `--accent` | Pill badges |

### Typography utilities

`.ui-kicker`, `.ui-kicker-sm`, `.ui-display-30`, `.ui-title-sm`, `.ui-copy-sm`, `.ui-body-16`

### Spacing / color / alignment utilities

`.ds-mt-*`, `.ds-mb-*`, `.ds-gap-*`, `.ds-ink-*`, `.ds-accent`, `.ds-bold`, `.ds-black`, `.ds-center`, `.ds-left`

新規 slide はまず ds-* shared class で成立させる。inline style は custom kind か、既存 class へ吸収しきれない局所レイアウトに限定する。

## Governance Rules

1. `content` slide は data-attribute + shared runtime で header/footer を出す。
2. 新規作成 / 大幅改修は `ds-stage` + `ds-grid` で section-first layout を組む。
3. `agenda` は manifest source から row を導出する。
4. `divider` と `center-title` は既存 class/data contract を維持する。
5. `summary / closing / cta / qa` は custom kind だが、background / footer meta / visual family は shared token に揃える。
6. **ハードコード値の禁止**: `color: rgba(0,0,0,.34)` → `color: var(--ink-34)`, `font-size: 14px` → `font-size: var(--fs-14)` を使う。
7. **スペーシングは親の `gap` に固定する。** 子の `margin` は使わない。不均一な距離が必要な場合はサブコンテナを挟む。
8. **optical gap 指示は受け入れない。** スペーシングスケール上の値に丸める。中間値の需要が 3 枚以上で出現した場合はスケールを見直す。
9. 新規コンポーネントは 3 枚以上で同じパターンが出現したら `ds-*` クラスに昇格させる。
10. **装飾 border-top / border-left の禁止。** 枠の一辺だけを太線・アクセント色で強調するパターンは使わない。強調は tint fill / badge / typography / 全周の細い border で行う。
11. **完成度ゲート（Completion Workflow）。** スライドの作成・改修は「レイアウト設計 → コンテンツ配置 → ずれレビュー → 修正」の 4 ステップを必ず通す。内容が正しくてもレイアウトが崩れた状態でタスク完了としない。詳細は `layout-sections.md` の Completion Workflow セクションを参照。
12. **未定義の `ds-*` class を使わない。** semantic な class 名だけ先に置いて inline style で成立させるのは禁止。共有 CSS に定義するか、slide ローカル class に閉じる。
