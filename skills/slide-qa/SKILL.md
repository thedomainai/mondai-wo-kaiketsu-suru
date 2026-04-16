---
name: slide-qa
description: HTML スライド deck の deterministic QA を行う。manifest / kind schema / legacy map を読み、filename contiguous、page drift、required attrs、background、assets、stale total-slide assumptions を検査するときに使う。
---

# Slide QA

この skill は deterministic QA を担当する。

## 先に読むもの

1. [`../../docs/ai-slide-system/deck-manifest.yaml`](../../docs/ai-slide-system/deck-manifest.yaml)
2. [`../../docs/ai-slide-system/slide-kinds.yaml`](../../docs/ai-slide-system/slide-kinds.yaml)
3. [`../../docs/ai-slide-system/legacy-map.yaml`](../../docs/ai-slide-system/legacy-map.yaml)

## 実行

```bash
python3 tools/slide_governance.py qa
```

必要に応じて report を明示的に出す。

```bash
python3 tools/slide_governance.py qa --report docs/ai-slide-system/qa-report.md
```

## 検査対象

- slide filename の連番性
- manifest と実ファイル順の一致
- `data-slide-kind` の一致
- kind ごとの required attrs / markers
- page number drift
- slide title drift
- agenda drift
- asset existence
- stale `TOTAL_SLIDES`

## Vertical rhythm drift の spot check

deterministic QA 本体では完全検証しきれないが、semantic spacing drift は最低限ここまで確認する。

```bash
rg -n "(eyebrow|kicker|label|num|index|focus|head|title)[^\\n]*margin-bottom:[0-9]+px|margin:0 0 [0-9]+px[^\\n]*(eyebrow|kicker|label|num|index|focus|head|title)" slides/slide_*.html slides/slides.css
```

結果が空でない場合は、`slides.css` token か parent `gap / row-gap` へ寄せる。  
lead-in に対する `padding-bottom` も drift とみなす。

optical gap の指定がある場合は、追加でこれを確認する。

- child text の `margin-bottom` で距離を持っていないか
- parent stack が `gap / row-gap` を持っているか
- 補正が必要なら local custom property (`--stack-optical-comp`) に閉じているか
- 最終値は screenshot で確認されているか

## Section-first の扱い

- deterministic QA は section-first を完全には証明しない
- ただし新規作成 / 大幅改修では [`../../docs/ai-slide-system/layout-sections.md`](../../docs/ai-slide-system/layout-sections.md) を authoring default とみなす
- section-first 違反は review rules と semantic review で拾う

## 修正系コマンド

```bash
python3 tools/slide_governance.py sync
python3 tools/slide_governance.py sync-slide-kinds
python3 tools/slide_governance.py sync-titles
python3 tools/slide_governance.py sync-agendas
```

QA は raw HTML を source-of-truth にせず、manifest に照らして差分を見る。
