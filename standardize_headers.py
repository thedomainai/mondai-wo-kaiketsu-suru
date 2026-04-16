#!/usr/bin/env python3
"""
LEGACY MIGRATION ONLY.

Standardize headers and footers for an older 47-slide deck snapshot.
This script is kept for migration/reference purposes and is not a source of
truth for the current 74-slide deck. Use docs/ai-slide-system plus
tools/slide_governance.py for canonical metadata.
"""
import os
import re
from pathlib import Path

SLIDES_DIR = "/tmp/slides"
TOTAL_SLIDES = len(list(Path(SLIDES_DIR).glob("slide_*.html")))

# slide_num -> (chapter_label, slide_title, main_message, bg_color)
SLIDE_DATA = {
    3:  ("第1章 前提：期待値と再現性", "問題解決能力が高いとは何か", "本質は「期待値を高めること」", "#ffffff"),
    4:  ("第1章 前提：期待値と再現性", "結果と行動を切り離す", "思考/行動が悪かったことを以って変える", "#ffffff"),
    5:  ("第1章 前提：期待値と再現性", "再現性とは「正しく間違えること」", "誤りを検知した階層で、同じ親の別の枝を探索する", "#ececec"),
    7:  ("第2章 前提・背景", "問題解決の本質", "正しい行動が決まれば、あとは実行するのみ", "#ffffff"),
    8:  ("第2章 前提・背景", "問題解決の型（7ステップ）", "再現性のあるプロセスを意識的に回す", "#ffffff"),
    9:  ("第2章 前提・背景", "メタ認知：プロセスを回す", "4つの必須行動", "#ffffff"),
    11: ("第3章 論点を定義する", "論点には必ず「べき」を含める", "行動を伴わない問い ＝ 自己満足・無意味", "#ffffff"),
    12: ("第3章 論点を定義する", "実践ルール", "論点定義の3つの必須行動", "#ffffff"),
    14: ("第4章 論点を分解する", "分解の5原則：概要", "論点を効果的に分解するための5つの原則", "#ffffff"),
    15: ("第4章 論点を分解する", "原則1：ツリー状に分解する", "論点はツリー構造で階層的に分解する", "#ffffff"),
    16: ("第4章 論点を分解する", "原則2：MECEに分解する", "1階層ずつ、網羅的かつMECEに", "#ffffff"),
    17: ("第4章 論点を分解する", "原則3：モデル（式）で考える", "四則演算で上位要素を成立させるように分解する", "#ffffff"),
    18: ("第4章 論点を分解する", "原則4：5分ルール", "5分以上かかるなら論点が間違っているか、さらに分解が必要", "#ffffff"),
    19: ("第4章 論点を分解する", "原則5：トップダウンとボトムアップ", "2つのアプローチを行き来しながら作る", "#ffffff"),
    20: ("第4章 論点を分解する", "ワーク例", "「美味しいハンバーガー」の分解", "#ffffff"),
    21: ("第4章 論点を分解する", "ダメな分解 vs 良い分解", "具体例で比較する", "#ffffff"),
    23: ("第5章 仮説を構築する", "仮説構築の目的", "正しさではなく検証可能性が目的", "#ffffff"),
    24: ("第5章 仮説を構築する", "良い仮説の条件", "4つの必須条件", "#ffffff"),
    25: ("第5章 仮説を構築する", "仮説の作り方", "論点に対する仮の答えを検証可能な形に整えて出す", "#ffffff"),
    26: ("第5章 仮説を構築する", "仮説を作る技法", "アナリティカル思考とコンセプチュアル思考", "#ffffff"),
    27: ("第5章 仮説を構築する", "知見がないときどうするか", "知見がない ＝ 仮説が浅くなるリスク", "#ffffff"),
    28: ("第5章 仮説を構築する", "Deep Dive：情報の海に潜る", "情報収集は時間を区切って潜る", "#ffffff"),
    29: ("第5章 仮説を構築する", "仮の答えを出すことから逃げない", "仮の答えを出す規律を持つ", "#ffffff"),
    31: ("第6章 仮説を検証する", "何を先に検証するか", "制約下で最も影響の大きい論点から検証する", "#ffffff"),
    32: ("第6章 仮説を検証する", "検証可能な形に変換する", "曖昧な仮説＝検証不可能 → 反証可能な命題に変換する", "#ffffff"),
    33: ("第6章 仮説を検証する", "検証手段を選ぶ", "最も低コスト × 判定力が高い手段から当てる", "#ffffff"),
    34: ("第6章 仮説を検証する", "トレードオフを評価する", "選択肢が複数ある場合は表形式で可視化する", "#ffffff"),
    35: ("第6章 仮説を検証する", "検証結果から次の行動を決める", "検証後の3つのパターンと対処法", "#ffffff"),
    37: ("第7章 解を伝える", "受け手視点で伝達を設計する", "伝達の起点は受け手視点", "#ffffff"),
    38: ("第7章 解を伝える", "意思決定構造を押さえる", "組織相手の場合、構造を押さえないと外れる", "#ffffff"),
    39: ("第7章 解を伝える", "誤解ポイントを先回りして潰す", "× どう話すか / ○ どこで誤解されるか", "#ffffff"),
    40: ("第7章 解を伝える", "解を伝える基本構造：5要素", "解を伝えるための構造化フレーム", "#ffffff"),
    41: ("第7章 解を伝える", "1. 結論：曖昧性を排除する", "受け手によって解釈が分かれる表現を避ける", "#ffffff"),
    42: ("第7章 解を伝える", "2. 根拠：センターピンに接続する", "なぜその結論に至ったかを論理的に示す", "#ffffff"),
    43: ("第7章 解を伝える", "3. ネクストアクション + 4. 残論点", "行動と未解決事項を明確にする", "#ffffff"),
    44: ("第7章 解を伝える", "5. 情報確度の明示", "確定情報と仮説を混ぜない", "#ffffff"),
    45: ("第7章 解を伝える", "ピラミッドストラクチャー", "解を伝える際の基本構造はピラミッド型である", "#ffffff"),
    46: ("まとめ", "覚えるべき5つの原則", "問題解決の5つの原則", "#ffffff"),
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
    page_str = f"{slide_num:02d} / {TOTAL_SLIDES}"
    return f'''<!-- === STANDARDIZED FOOTER === -->
<div style="position: absolute; left: 0; top: 660px; width: 1280px; height: 60px; background-color: {bg_color}; border-top: 1px solid rgba(0,0,0,0.08); z-index: 50;"></div>
<div style="position: absolute; left: 40px; top: 680px; z-index: 55;">
<p style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: var(--font-size-footer-meta); color: #bbb; letter-spacing: 1.5px;">LOGICAL THINKING TRAINING</p>
</div>
<div style="position: absolute; right: 40px; top: 680px; z-index: 55;">
<p style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: var(--font-size-footer-meta); color: #bbb; letter-spacing: 0.5px;">{page_str}</p>
</div>
<!-- === END FOOTER === -->'''


def remove_element_containing(html, search_text):
    """Remove the data-object div containing the specified text."""
    idx = html.find(search_text)
    if idx == -1:
        return html

    # Search backwards for the enclosing data-object div
    search_pos = idx
    div_start = -1
    while search_pos > 0:
        pos = html.rfind('<div', 0, search_pos)
        if pos == -1:
            break
        tag_end = html.find('>', pos)
        if tag_end == -1:
            break
        tag = html[pos:tag_end + 1]
        if 'data-object=' in tag or 'data-object-type=' in tag:
            div_start = pos
            break
        search_pos = pos

    if div_start == -1:
        return html

    # Find matching closing </div>
    depth = 0
    i = div_start
    div_end = -1
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                div_end = i + 6
                break
            i += 6
        else:
            i += 1

    if div_end == -1:
        return html

    # Extend to consume trailing whitespace
    while div_end < len(html) and html[div_end] in ' \t\n\r':
        div_end += 1

    # Also remove preceding HTML comment if present
    pre = html[:div_start].rstrip()
    comment_start = div_start
    if pre.endswith('-->'):
        ci = pre.rfind('<!--')
        if ci != -1 and pre[ci:].count('\n') <= 1:
            comment_start = ci
            # Consume whitespace before comment
            while comment_start > 0 and html[comment_start - 1] in ' \t\n\r':
                comment_start -= 1
            comment_start += 1  # Keep one newline

    return html[:comment_start] + html[div_end:]


def remove_leading_title_blocks(html):
    """Remove body-level title blocks replaced by the standardized header."""
    pattern = (
        r'\s*<!--\s*(?:Section Title(?: and Subtitle)?|Title(?:\s*&\s*Subtitle)?|Subtitle)\s*(?:\([^)]+\))?\s*-->\s*'
        r'<div\s+data-object="true"\s+data-object-type="textbox"\s+'
        r'style="position:\s*absolute;\s*left:\s*80px;\s*top:\s*160px;[^"]*">'
        r'(?:(?!<div\b).)*?</div>\s*'
    )
    return re.sub(pattern, '\n', html, flags=re.DOTALL)


def process_slide(slide_num):
    if slide_num not in SLIDE_DATA:
        return

    chapter_label, slide_title, main_message, bg_color = SLIDE_DATA[slide_num]
    filepath = os.path.join(SLIDES_DIR, f"slide_{slide_num:02d}.html")

    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original_len = len(html)

    # 1. Remove branding pill (contains "PROBLEM SOLVING")
    html = remove_element_containing(html, 'PROBLEM SOLVING')

    # 2. Remove navigation arrow (contains "fa-chevron-right")
    html = remove_element_containing(html, 'fa-chevron-right')
    html = remove_leading_title_blocks(html)

    # 3. Insert header after <div class="slide-container">
    header_html = make_header_html(chapter_label, slide_title, main_message, bg_color)
    footer_html = make_footer_html(slide_num, bg_color)

    # Find slide-container opening
    container_tag = 'class="slide-container"'
    container_idx = html.find(container_tag)
    if container_idx == -1:
        print(f"  ERROR: slide-container not found in slide {slide_num}")
        return
    insert_after = html.find('>', container_idx) + 1
    html = html[:insert_after] + '\n' + header_html + '\n' + html[insert_after:]

    # 4. Insert footer before closing </div> of slide-container (last </div> before </body>)
    body_close = html.rfind('</body>')
    if body_close == -1:
        body_close = len(html)
    container_close = html.rfind('</div>', 0, body_close)
    if container_close == -1:
        print(f"  ERROR: closing </div> not found in slide {slide_num}")
        return
    html = html[:container_close] + footer_html + '\n' + html[container_close:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    new_len = len(html)
    print(f"  slide_{slide_num:02d}.html: {original_len} -> {new_len} bytes")


def main():
    print("Standardizing headers and footers...")
    print(f"Processing {len(SLIDE_DATA)} content slides\n")

    for slide_num in sorted(SLIDE_DATA.keys()):
        print(f"Processing slide {slide_num:02d}...")
        process_slide(slide_num)

    print(f"\nDone! Processed {len(SLIDE_DATA)} slides.")


if __name__ == '__main__':
    main()
