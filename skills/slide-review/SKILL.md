---
name: slide-review
description: HTML スライド deck を Layout / Typography / Graphics / Narrative flow の観点でレビューする。whole-deck report と issue markdown を出し、review rules と legacy map に照らして改善点を洗い出すときに使う。
---

# Slide Review

この skill は semantic review を担当する。まず deterministic QA を見てから、視覚と言語の質を見る。

## 先に読むもの

1. [`../../docs/ai-slide-system/deck-manifest.yaml`](../../docs/ai-slide-system/deck-manifest.yaml)
2. [`../../docs/ai-slide-system/review-rules.yaml`](../../docs/ai-slide-system/review-rules.yaml)
3. [`../../docs/ai-slide-system/layout-sections.md`](../../docs/ai-slide-system/layout-sections.md)
4. [`../../docs/ai-slide-system/legacy-map.yaml`](../../docs/ai-slide-system/legacy-map.yaml)

## 基本手順

1. `python3 tools/slide_governance.py qa` を実行し、contract drift を先に把握する。
2. そのうえで `Layout / Typography / Graphics / Narrative flow` を診る。
3. whole-deck report は Markdown を既定にする。
4. 個別の深掘りは `docs/issues/*.md` に切り出す。

## 必ず確認する観点

- section skeleton が先に成立しているか
- object が section ownership を持っているか
- 重なりや余白を relayout で解いているか
- copy の増減が section budget に反映されているか
- parallel card / 比較表で、対応する内部 line や foot の開始位置が明示的な track 設計で揃っているか
- `eyebrow / kicker / label / num / index -> title / head -> body / copy / text` の距離が token ベースで揃っているか
- 同じ semantic role の要素を複数 slide で見たとき、1 枚だけ tight / loose になっていないか
- 余白責任が `margin` / `padding-bottom` / 親 `gap` / inline style に分散していないか
- 「48px 空ける」のような要求が raw `margin-bottom` として実装されていないか。視覚距離の要求なら、親 stack の gap と optical compensation で持っているか
- optical gap を使った箇所は、スクリーンショット上の見た目距離で最終確認されているか
- bridge slide の接続の明確さ
- 5 card 横並びのバランス
- summary / closing / cta / qa の役割分離
- object grammar の数
- scan order と情報密度

## 出力

- findings を severity 順に並べる
- file reference を添える
- whole-deck summary は短く保つ
- content-first stacking の疑いがあるときは、その object ではなく section 設計から指摘する
- vertical rhythm の指摘は、対象 slide 単体ではなく「同種要素の deck 内相場」とセットで指摘する
