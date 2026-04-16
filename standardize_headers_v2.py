#!/usr/bin/env python3
"""
LEGACY MIGRATION ONLY.

Standardize headers and footers for an older 50-slide deck snapshot.
This script is kept for migration/reference purposes and is not a source of
truth for the current 74-slide deck. Use docs/ai-slide-system plus
tools/slide_governance.py for canonical metadata.
"""

import re
import os
from pathlib import Path

SLIDE_DIR = "/private/tmp/slides"
TOTAL_SLIDES = len(list(Path(SLIDE_DIR).glob("slide_*.html")))

# 10 excluded slides: title(1), agenda(2), chapter dividers(5,9,13,16,25,33,39), Q&A(50)
EXCLUDED = {1, 2, 5, 9, 13, 16, 25, 33, 39, 50}

# (chapter_label, slide_title, main_message, bg_color)
SLIDE_DATA = {
    3:  ("ワーク", "ワーク", "現在地と研修後の状態の差分を体感する", "#ececec"),
    4:  ("ワーク", "ワーク：問題解決の体験", "個人ワーク：10分間", "#ececec"),
    6:  ("第1章 前提：期待値と再現性", "問題解決能力が高いとは何か", "本質は「期待値を高めること」", "#ffffff"),
    7:  ("第1章 前提：期待値と再現性", "結果と行動を切り離す", "思考/行動が悪かったことを以って変える", "#ffffff"),
    8:  ("第1章 前提：期待値と再現性", "再現性とは「正しく間違えること」", "誤りを検知した階層で、同じ親の別の枝を探索する", "#ececec"),
    10: ("第2章 前提・背景", "問題解決の本質", "正しい行動が決まれば、あとは実行するのみ", "#ffffff"),
    11: ("第2章 前提・背景", "問題解決の型（7ステップ）", "再現性のあるプロセスを意識的に回す", "#ffffff"),
    12: ("第2章 前提・背景", "メタ認知：プロセスを回す", "4つの必須行動", "#ffffff"),
    14: ("第3章 論点を定義する", "論点には必ず「べき」を含める", "行動を伴わない問い ＝ 自己満足・無意味", "#ffffff"),
    15: ("第3章 論点を定義する", "実践ルール", "論点定義の3つの必須行動", "#ffffff"),
    17: ("第4章 論点を分解する", "分解の5原則：概要", "論点を効果的に分解するための5つの原則", "#ffffff"),
    18: ("第4章 論点を分解する", "原則1：ツリー状に分解する", "論点はツリー構造で階層的に分解する", "#ffffff"),
    19: ("第4章 論点を分解する", "原則2：MECEに分解する", "MECEの徹底", "#ffffff"),
    20: ("第4章 論点を分解する", "原則3：モデル（式）で考える", "四則演算で上位要素を成立させるように分解する", "#ececec"),
    21: ("第4章 論点を分解する", "原則4：5分ルール", "5分以上かかるなら論点が間違っているか、さらに分解が必要", "#ffffff"),
    22: ("第4章 論点を分解する", "原則5：トップダウンとボトムアップ", "2つのアプローチを行き来しながら作る", "#ffffff"),
    23: ("第4章 論点を分解する", "ワーク例：ハンバーガーの分解", "「美味しいハンバーガー」の分解", "#ffffff"),
    24: ("第4章 論点を分解する", "ダメな分解 vs 良い分解", "具体例で比較する", "#ffffff"),
    26: ("第5章 仮説を構築する", "仮説構築の目的", "正しさではなく検証可能性が目的", "#ffffff"),
    27: ("第5章 仮説を構築する", "良い仮説の条件", "4つの必須条件", "#ffffff"),
    28: ("第5章 仮説を構築する", "仮説の作り方", "論点に対する仮の答えを検証可能な形に整えて出す", "#ffffff"),
    29: ("第5章 仮説を構築する", "仮説を作る技法", "アナリティカル思考とコンセプチュアル思考", "#ffffff"),
    30: ("第5章 仮説を構築する", "知見がないときどうするか", "知見がない ＝ 仮説が浅くなるリスク", "#ffffff"),
    31: ("第5章 仮説を構築する", "Deep Dive：情報の海に潜る", "情報収集は時間を区切って潜る", "#ffffff"),
    32: ("第5章 仮説を構築する", "仮の答えを出すことから逃げない", "仮の答えを出す規律を持つ", "#ffffff"),
    34: ("第6章 仮説を検証する", "何を先に検証するか", "制約下で最も影響の大きい論点から検証する", "#ffffff"),
    35: ("第6章 仮説を検証する", "検証可能な形に変換する", "曖昧な仮説＝検証不可能 → 反証可能な命題に変換する", "#ffffff"),
    36: ("第6章 仮説を検証する", "検証手段を選ぶ", "最も低コスト × 判定力が高い手段から当てる", "#ffffff"),
    37: ("第6章 仮説を検証する", "トレードオフを評価する", "選択肢が複数ある場合は表形式で可視化する", "#ffffff"),
    38: ("第6章 仮説を検証する", "検証結果から次の行動を決める", "検証後の3つのパターンと対処法", "#ffffff"),
    40: ("第7章 解を伝える", "受け手視点で伝達を設計する", "伝達の起点は受け手視点", "#ffffff"),
    41: ("第7章 解を伝える", "意思決定構造を押さえる", "組織相手の場合、構造を押さえないと外れる", "#ffffff"),
    42: ("第7章 解を伝える", "誤解ポイントを先回りして潰す", "どこで誤解されるかを先に潰す", "#ffffff"),
    43: ("第7章 解を伝える", "解を伝える基本構造：5要素", "解を効果的に伝えるための5つの要素を紹介する", "#ffffff"),
    44: ("第7章 解を伝える", "結論：曖昧性を排除する", "受け手によって解釈が分かれる曖昧な表現を避ける", "#ffffff"),
    45: ("第7章 解を伝える", "根拠：センターピンに接続する", "結論を支える理由を相手のセンターピンに接続する", "#ffffff"),
    46: ("第7章 解を伝える", "ネクストアクション + 残論点", "行動と未解決事項を明確にする", "#ececec"),
    47: ("第7章 解を伝える", "情報確度の明示", "確定情報と仮説を混ぜない", "#ffffff"),
    48: ("第7章 解を伝える", "ピラミッドストラクチャー", "解を伝える際の基本構造はピラミッド型である", "#ffffff"),
    49: ("まとめ", "まとめ：覚えるべき5つの原則", "問題解決の5つの原則", "#ffffff"),
}


def make_header_html(chapter_label, slide_title, main_message, bg_color):
    return f'''<!-- === STANDARDIZED HEADER === -->
<div style="position: absolute; left: 0; top: 0; width: 1280px; height: 148px; background-color: {bg_color}; z-index: 50;"></div>
<div style="position: absolute; right: 80px; top: 18px; z-index: 55;">
<p style="margin: 0; padding: 3px 12px; border: 2px solid #000; border-radius: 9999px; font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: var(--font-size-header-pill); color: #000; letter-spacing: 0.8px; background: {bg_color}; display: inline-block; white-space: nowrap;">PROBLEM SOLVING</p>
</div>
<div style="position: absolute; left: 80px; top: 22px; width: 960px; z-index: 55;">
<p style="margin: 0 0 var(--space-stack-lead-title); font-family: 'Noto Sans JP', sans-serif; font-weight: 400; font-size: var(--font-size-header-chapter); color: #999; letter-spacing: 0.5px; white-space: nowrap;">{chapter_label}</p>
<p style="margin: 0 0 var(--space-stack-title-body); font-family: 'Noto Sans JP', sans-serif; font-weight: 900; font-size: var(--font-size-header-title); color: #000; letter-spacing: var(--letter-spacing-header-title); line-height: var(--line-height-header-title); white-space: nowrap;">{slide_title}</p>
<p style="margin: 0; font-family: 'Noto Sans JP', sans-serif; font-weight: 400; font-size: var(--font-size-header-subtitle); color: #888; line-height: var(--line-height-header-subtitle); white-space: nowrap;">{main_message}</p>
</div>
<!-- === END HEADER === -->'''


def make_footer_html(slide_num, bg_color):
    return f'''<!-- === STANDARDIZED FOOTER === -->
<div style="position: absolute; left: 0; top: 660px; width: 1280px; height: 60px; background-color: {bg_color}; border-top: 1px solid rgba(0,0,0,0.08); z-index: 50;"></div>
<div style="position: absolute; left: 40px; top: 680px; z-index: 55;">
<p style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: var(--font-size-footer-meta); color: #bbb; letter-spacing: 1.5px;">LOGICAL THINKING TRAINING</p>
</div>
<div style="position: absolute; right: 40px; top: 680px; z-index: 55;">
<p style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: var(--font-size-footer-meta); color: #bbb; letter-spacing: 0.5px;">{slide_num} / {TOTAL_SLIDES}</p>
</div>
<!-- === END FOOTER === -->'''


def remove_standardized_blocks(html):
    """Remove existing STANDARDIZED HEADER and FOOTER blocks."""
    html = re.sub(
        r'\n?<!-- === STANDARDIZED HEADER === -->.*?<!-- === END HEADER === -->\n?',
        '\n', html, flags=re.DOTALL
    )
    html = re.sub(
        r'\n?<!-- === STANDARDIZED FOOTER === -->.*?<!-- === END FOOTER === -->\n?',
        '\n', html, flags=re.DOTALL
    )
    return html


def remove_element_containing(html, search_text):
    """Remove a data-object div that contains the given text."""
    pattern = r'<div\s+data-object="true"[^>]*>.*?' + re.escape(search_text) + r'.*?</div>\s*'
    return re.sub(pattern, '', html, flags=re.DOTALL)


def remove_branding_pill(html):
    """Remove the original PROBLEM SOLVING branding pill (non-standardized)."""
    # Match div containing "PROBLEM SOLVING" text in a pill-shaped badge
    # but NOT our standardized header (which is inside <!-- === STANDARDIZED HEADER === -->)
    pattern = r'<div\s+data-object="true"[^>]*>[\s\S]*?PROBLEM\s+SOLVING[\s\S]*?</div>\s*'
    return re.sub(pattern, '', html, flags=re.DOTALL)


def remove_nav_arrows(html):
    """Remove navigation arrow elements (fa-chevron-right etc)."""
    pattern = r'<div\s+data-object="true"[^>]*>[\s\S]*?fa-chevron-right[\s\S]*?</div>\s*'
    return re.sub(pattern, '', html, flags=re.DOTALL)


def remove_leading_title_blocks(html):
    """Remove body-level title/subtitle blocks replaced by the standardized header."""
    pattern = (
        r'\s*<!--\s*(?:Section Title(?: and Subtitle)?|Title(?:\s*&\s*Subtitle)?|Subtitle)\s*(?:\([^)]+\))?\s*-->\s*'
        r'<div\s+data-object="true"\s+data-object-type="textbox"\s+'
        r'style="position:\s*absolute;\s*left:\s*80px;\s*top:\s*160px;[^"]*">'
        r'(?:(?!<div\b).)*?</div>\s*'
    )
    return re.sub(pattern, '\n', html, flags=re.DOTALL)


def process_slide(slide_num):
    filepath = os.path.join(SLIDE_DIR, f"slide_{slide_num:02d}.html")
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Step 1: Remove any existing standardized blocks (from all slides)
    html = remove_standardized_blocks(html)

    if slide_num in EXCLUDED:
        # For excluded slides, just clean up and save
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  slide_{slide_num:02d}: cleaned (excluded)")
        return

    if slide_num not in SLIDE_DATA:
        print(f"  slide_{slide_num:02d}: ERROR - no data defined!")
        return

    chapter_label, slide_title, main_message, bg_color = SLIDE_DATA[slide_num]

    # Step 2: Remove old branding elements (PROBLEM SOLVING pill, nav arrows)
    html = remove_branding_pill(html)
    html = remove_nav_arrows(html)
    html = remove_leading_title_blocks(html)

    # Step 3: Insert new standardized header after <div class="slide-container">
    header_html = make_header_html(chapter_label, slide_title, main_message, bg_color)
    footer_html = make_footer_html(slide_num, bg_color)

    # Insert header right after slide-container opening tag
    html = re.sub(
        r'(<div\s+class="slide-container"[^>]*>)',
        r'\1\n' + header_html + '\n',
        html,
        count=1
    )

    # Insert footer right before closing </div> of slide-container (last </div> before </body>)
    # Find the position just before the last </div></body>
    html = re.sub(
        r'(</div>\s*</body>)',
        footer_html + '\n' + r'\1',
        html,
        count=1
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  slide_{slide_num:02d}: OK ({chapter_label} / {slide_title})")


def main():
    print(f"Processing {TOTAL_SLIDES} slides...")
    print(f"Excluded: {sorted(EXCLUDED)}")
    print(f"Content slides: {len(SLIDE_DATA)}")
    print()

    for i in range(1, TOTAL_SLIDES + 1):
        process_slide(i)

    print()
    print("Done!")


if __name__ == "__main__":
    main()
