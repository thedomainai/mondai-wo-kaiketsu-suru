---
name: slide-authoring
description: HTML スライドの新規作成・改修を kind-first で行う。`cover / intro / agenda / divider / center-title / content / summary / closing / cta / qa` の schema を守り、manifest と shared runtime に沿って編集するときに使う。
---

# Slide Authoring

HTML slide を作るときは、まず manifest と slide kind schema に従う。  
レイアウトは `kind-first` に加えて `section-first` を既定にする。

## 先に確認するもの

1. [`../../docs/ai-slide-system/deck-manifest.yaml`](../../docs/ai-slide-system/deck-manifest.yaml)
2. [`../../docs/ai-slide-system/slide-kinds.yaml`](../../docs/ai-slide-system/slide-kinds.yaml)
3. [`../../docs/ai-slide-system/layout-sections.md`](../../docs/ai-slide-system/layout-sections.md)
4. 既存 slide の例外なら [`../../docs/ai-slide-system/legacy-map.yaml`](../../docs/ai-slide-system/legacy-map.yaml)

## Workflow

1. 対象 slide の `data-slide-kind` を確認する。
2. slide の one-message と scan order を先に決める。
3. body safe area の中に section skeleton を先に置く。
4. section ごとの高さ・幅・gap を grid / flex で先に配分する。
5. content はその section の内側にだけ入れる。
6. shared runtime で済むものは `slides.css` / `slides.js` に寄せる。
7. 変更後に `python3 tools/slide_governance.py sync` で title / agenda / index / page metadata を同期し、`python3 tools/slide_governance.py qa` を通す。

## Section-first rules

- 主要 block を page 直下へ `top/left` で積み上げない。
- `main` または親 wrapper が body safe area を持つ。
- 主要 block は `section` / `article` の ownership を持つ。
- overlap や dead space は object 単位の nudge ではなく、section budget の再配分で解く。
- copy を削ったら、その空きは section 側へ返して visual を広げる。
- absolute positioning は section 内の diagram / node / badge / connector に限定する。
- 同一 row に置く parallel card は、対応する内部領域を明示的な track として揃える。`head / body / foot` や `label / text / note` の開始位置を揃えたい場合、copy 量に依存した auto height に任せず、`grid-template-rows`・stretch・`min-height` で揃える。

## Vertical Rhythm rules

- `eyebrow / kicker / label / num / index` は同じ「lead-in」とみなす。
- `title / head` はその下の `body / copy / text / note / list` への橋として扱う。
- 距離は [`../../slides.css`](../../slides.css) の stack token を使う。生の `8px`, `10px`, `12px` を新規追加しない。
- 基本 token:
  - `--space-stack-lead-title`
  - `--space-stack-title-body`
  - `--space-stack-lead-title-loose`
  - `--space-stack-title-body-loose`
- shared header / divider / center-title / agenda は shared CSS を優先し、個別 slide で再実装しない。
- one-off slide で inline style が必要でも、余白だけは token を直接参照する。
- `padding-bottom` を lead-in の見かけ余白として使わない。余白の責任は `margin` か親の `gap / row-gap` のどちらか一方に持たせる。
- parent が `display:grid` / `display:flex` で明示的に `gap / row-gap` を持つときは、子の `lead/title` margin を 0 に寄せ、親を唯一の責任者にする。
- 逆に通常フローで積む block は、親 gap を増やさず、`lead` と `title` の margin token で揃える。
- 「48px 空ける」のような指定は raw box gap ではなく optical gap と読む。文字同士の見た目距離が仕様で、`margin-bottom: 48px` を直書きする意味ではない。
- optical gap を求められた stack は、親 `gap / row-gap` で距離を持ち、子テキストの `margin` は 0 にする。補正は `--stack-optical-comp` のような local custom property に閉じる。
- optical compensation は global token をすぐ増やさない。同じ font pairing / size pairing が deck 横断で 3 回以上現れるまで、stack ローカルで持つ。
- optical gap はコード上の数値だけで確定しない。変更後はスクリーンショットで見た目距離を確認し、必要なら compensation を再調整する。
- 改修対象 slide だけを見るのではなく、同じ semantic role を持つ他 slide を最低 3 枚見て、deck 内の相場に合わせる。

## Anti-patterns

- content を先に作ってから page 上で押し込む
- 重なりを `top` / `left` 微調整だけで解消する
- 図と本文のどちらにも属さない余白を放置する
- section を持たないまま card, chart, note を直接並べる
- 比較 card の内部 line や foot の位置を、文章量の違う auto height のまま偶然に揃う前提で置く
- `eyebrow` は margin、`title` は row-gap、`body` は inline style のように、余白責任が 1 block 内で分散している
- 余白を直したいだけなのに `padding-bottom` を足して応急処置する
- 見た目距離の指定を、そのまま `margin-bottom` の数値に読み替える

## Kind rules

### `content`

- 必須: `data-slide-kind="content"`
- 必須: `data-header-chapter`, `data-header-title`, `data-header-subtitle`
- 必須: `data-footer="standard"` と `data-footer-page`
- 禁止: header/footer の手書き DOM 再実装
- 推奨: `main.content-stage` のような親 wrapper を置き、その中に `section` を切る
- 推奨: 主要 layout は grid / flex で持ち、absolute は局所図解に閉じる

### `agenda`

- row は manifest の `slides[].agenda` から導出する
- 手で item 文面を変える前に manifest を更新する

### `divider`

- `data-divider-*` を維持する
- halftone background を崩さない

### `center-title`

- `.slide-center-title` と `chapter/title/subtitle` block を維持する

### custom kinds

- `cover / intro / summary / closing / cta / qa` の範囲に閉じる
- visual family は shared token に揃える
- custom kind でも section-first は維持する

## 実務メモ

- 新規 slide を足すときは、先に manifest を更新するか `python3 tools/slide_governance.py sync-docs` で再生成する。
- slide の main title を変えたら、`python3 tools/slide_governance.py sync` で `<title>` と viewer index も追従させる。
- agenda slide を更新したら `python3 tools/slide_governance.py sync-agendas` を優先する。
