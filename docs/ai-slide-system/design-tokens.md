# Design Tokens

## Runtime

- Format: `1280x720 HTML`
- Shared CSS SSOT: [`slides.css`](/private/tmp/slides/slides.css)
- Shared JS SSOT: [`slides.js`](/private/tmp/slides/slides.js)
- Canonical slide container: `.slide-container`

## Layout Geometry

### Shared header/footer

- `--header-band-height: 156px`
- `--header-pill-top: 20px`
- `--header-text-top: 28px`
- `--content-left: 80px`
- `--content-width: 1120px`
- `--content-right: 1200px`
- `--content-center: 640px`
- Footer baseline: `top: 660px`, height `60px`

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

- `--space-stack-lead-title: 12px`
- `--space-stack-title-body: 16px`
- `--space-stack-lead-title-loose: 24px`
- `--space-stack-title-body-loose: 36px`

lead-in (`eyebrow / kicker / label / num`) → title → body の距離は、この 4 token を SSOT にする。shared header / divider / center-title / agenda も別 token を増やさず、この scale に乗せる。局所修正で `padding-bottom` や生の `8px` を足して吸収しない。

### Optical gap

- 「48px 空ける」のような指定は、既定では `margin-bottom: 48px` ではなく「文字の見た目の上下端の距離」と解釈する。
- この場合、距離の責任は親 stack が持つ。子テキストの `margin` は 0 に寄せる。
- 補正は global token を増やさず、stack ローカルの custom property で持つ。3 枚以上で同じ補正を繰り返すまで、SSOT へ昇格させない。
- 共通パターンは `.stack-optical` を使う。

```css
.stack-optical {
  display: grid;
  row-gap: calc(var(--stack-gap) + var(--stack-optical-comp, 0px));
}

.stack-optical > :is(p, h1, h2, h3, h4, h5, h6, span) {
  margin: 0;
}
```

例:

```css
.qa-stack {
  --stack-gap: var(--space-stack-title-body-loose);
  --stack-optical-comp: 12px;
}
```

補正値はコード上の box gap ではなく、スクリーンショット上の見た目距離で決める。

## Shared UI Classes

- `.slide-standard-header*`
- `.slide-standard-footer*`
- `.slide-divider*`
- `.slide-center-title*`
- `.agenda-panel*`
- `.ui-kicker`
- `.ui-kicker-sm`
- `.ui-display-30`
- `.ui-title-sm`
- `.ui-copy-sm`
- `.ui-body-16`
- `.step-card*`

新規 slide はまず shared class で成立させる。inline style は custom kind か、既存 class へ吸収しきれない局所レイアウトに限定する。

## Governance Rules

1. `content` slide は data-attribute + shared runtime で header/footer を出す。
2. 新規作成 / 大幅改修は section-first layout を既定にする。
3. `agenda` は manifest source から row を導出する。
4. `divider` と `center-title` は既存 class/data contract を維持する。
5. `summary / closing / cta / qa` は custom kind だが、background / footer meta / visual family は shared token に揃える。
6. token 名ではなく生の px 値を増やすときは、まず SSOT へ昇格すべきか判断する。
7. `eyebrow / title / body` の距離は、親の `gap` か子の `margin` のどちらか一方で持つ。両方に分散させない。
8. 「見た目で 48px」のような指定は optical gap とみなし、親 `gap / row-gap` と local compensation で実装する。
