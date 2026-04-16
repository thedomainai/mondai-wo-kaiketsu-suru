---
name: slide-deck-governor
description: HTML スライド deck の governance 入口。slide kind を先に特定し、manifest・kind schema・review rules を読み込んでから authoring / review / qa の各 workflow に振り分ける。`/private/tmp/slides` 系の deck で新規作成、改修、監査、全体整合チェックをするときに使う。
---

# Slide Deck Governor

この skill は deck 全体の入口である。最初に slide kind と作業種別を決め、必要な spec を最小限だけ読む。

## 最初に読むもの

1. [`../../docs/ai-slide-system/deck-manifest.yaml`](../../docs/ai-slide-system/deck-manifest.yaml)
2. [`../../docs/ai-slide-system/slide-kinds.yaml`](../../docs/ai-slide-system/slide-kinds.yaml)
3. 新規作成 / 大幅改修なら [`../../docs/ai-slide-system/layout-sections.md`](../../docs/ai-slide-system/layout-sections.md)
4. 作業が review / qa なら [`../../docs/ai-slide-system/review-rules.yaml`](../../docs/ai-slide-system/review-rules.yaml)
5. 既存 slide の例外に触るなら [`../../docs/ai-slide-system/legacy-map.yaml`](../../docs/ai-slide-system/legacy-map.yaml)

## ルーティング

- 新規作成 / 改修: [`../slide-authoring/SKILL.md`](../slide-authoring/SKILL.md)
- デザイン / narrative review: [`../slide-review/SKILL.md`](../slide-review/SKILL.md)
- 静的 QA / numbering / asset / contract check: [`../slide-qa/SKILL.md`](../slide-qa/SKILL.md)

## 基本原則

1. slide kind を先に決める  
`cover / intro / agenda / divider / center-title / content / summary / closing / cta / qa` のどれかを必ず先に選ぶ。

2. manifest を deck source-of-truth とみなす  
slide order、page label、agenda row、canonical kind は manifest を優先する。

3. layout は section-first で組む  
slide body は section skeleton を先に置き、その内側へ content を入れる。object を先に作って page へ積む流儀を既定にしない。

4. content では shared runtime を使う  
header/footer を手書き DOM で増やさず、`data-header-*` と `data-footer="standard"` に寄せる。

5. custom kind を無秩序に増やさない  
custom は `cover / intro / summary / closing / cta / qa` に閉じる。分類不能な custom は作らない。

6. 変更後は sync と QA を通す  
少なくとも `python3 tools/slide_governance.py sync` で title / agenda / index / page metadata を同期し、`python3 tools/slide_governance.py qa` を走らせる。

7. 削除や差し替えの前に page と title を照合する  
`P65` のような依頼は filename と同一視しない。削除・差し替え・移動の前に `python3 tools/slide_governance.py resolve-slide --page P65 --title "..."` を実行し、page label と title が同じ slide を指していることを確認する。

8. 同種要素は deck 横断で比較する  
`eyebrow / kicker / label / num / index -> title / head -> body / copy / text` のような semantic stack は、対象 slide 単体ではなく deck 全体の同種要素を見てから揃える。1 枚だけを局所最適化しない。

9. 視覚距離の指定は optical gap として扱う  
「48px 空ける」のような依頼は raw `margin-bottom` の値ではなく、文字同士の見た目距離の指定とみなす。親 stack の `gap / row-gap` を責任者にし、必要なら local compensation を持つ。
