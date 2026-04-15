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
- agenda drift
- asset existence
- stale `TOTAL_SLIDES`

## Section-first の扱い

- deterministic QA は section-first を完全には証明しない
- ただし新規作成 / 大幅改修では [`../../docs/ai-slide-system/layout-sections.md`](../../docs/ai-slide-system/layout-sections.md) を authoring default とみなす
- section-first 違反は review rules と semantic review で拾う

## 修正系コマンド

```bash
python3 tools/slide_governance.py sync
python3 tools/slide_governance.py sync-slide-kinds
python3 tools/slide_governance.py sync-agendas
```

QA は raw HTML を source-of-truth にせず、manifest に照らして差分を見る。
