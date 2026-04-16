# 第4章 構成診断

## 対象

- 現在の第4章: [slide_30.html](/private/tmp/slides/slide_30.html), [slide_31.html](/private/tmp/slides/slide_31.html), [slide_32.html](/private/tmp/slides/slide_32.html), [slide_33.html](/private/tmp/slides/slide_33.html), [slide_34.html](/private/tmp/slides/slide_34.html)
- 後続の第5章: [slide_35.html](/private/tmp/slides/slide_35.html), [slide_36.html](/private/tmp/slides/slide_36.html)
- 構成の正本: [/Users/yuta/workspace/shared/docs/problem-solving.md](/Users/yuta/workspace/shared/docs/problem-solving.md)
- 過去ログの要約: [history-ledger.md](/private/tmp/slides/docs/ai-slide-system/history-ledger.md)

## 結論

現状の第4章は、**章のテーマ自体は正しいが、論点の立て方とスライドの並べ方が弱い**。

問題は「4章が間違った内容になっている」ことより、以下の3点にある。

1. **第3章との役割分担が曖昧**
2. **第4章で最も重要な論点が一枚抜けている**
3. **過去ログの参照単位がページ番号ベースでずれ、修正意図が散逸した**

その結果、第4章は「論点定義が最重要である」という強いメッセージを打ち出す章ではなく、**『べき』という表現ルールを説明する小章**のように見えている。

## 現状診断

### 1. 章の主張が弱い

現在の第4章の中核は次の2枚である。

- [slide_32.html](/private/tmp/slides/slide_32.html): 「論点には必ず『べき』を含める」
- [slide_33.html](/private/tmp/slides/slide_33.html): 「論点定義の3つの必須行動」

この並びだと、章の主張が

- 論点定義とは何か
- なぜそれが最重要なのか
- 間違えると何が壊れるのか

ではなく、

- 問いの文末はどうあるべきか

に見えやすい。

### 2. 第3章と内容が競合している

第3章の後半ではすでに、

- [slide_25.html](/private/tmp/slides/slide_25.html): 「論点は、行動を起こすための問いである」
- [slide_26.html](/private/tmp/slides/slide_26.html): 7ステップの中の論点定義
- [slide_28.html](/private/tmp/slides/slide_28.html): 問いの置き方に時間を使う
- [slide_29.html](/private/tmp/slides/slide_29.html): 今どの段階にいるかを把握する

まで説明済みである。

その直後の第4章が `べき` の説明から始まるため、受け手には

- 「第3章の続きの注意事項」
- 「既に言ったことの言い換え」

として受け取られやすい。

### 3. 第4章の重みとページ配分が釣り合っていない

現在の第4章は実質的に

- 章アジェンダ
- 章扉
- 内容2枚
- まとめ1枚

で終わる。

一方で第5章は分解原則の概要と各論を十分な枚数で持っている。

しかし構成の正本である [/Users/yuta/workspace/shared/docs/problem-solving.md](/Users/yuta/workspace/shared/docs/problem-solving.md) では、論点定義は

> 問題解決の全工程で最も重要なステップ。問いが間違っていたら行動は間違える

という扱いであり、今の枚数感と見せ方はその重要度に見合っていない。

### 4. 過去ログの修正意図がページ番号ずれで分断されている

[history-ledger.md](/private/tmp/slides/docs/ai-slide-system/history-ledger.md) には、過去の重要な指示として次が残っている。

- `P28にやはりハンバーガーの例が継続して載っていますが...`  
  4章ではなく分解章の具体例が前倒しで侵入していたことへの指摘。
- `4章のアジェンダのページがなくなってしまっていませんか？`  
  4章の導線そのものを欠落させないことへの指摘。
- `P28 下記の情報をベースにつくりかえてください...`  
  「今どの段階にいるか」「問題解決には流れがある」「行き来する」という橋渡しの論点を明示する指示。

ただしこのログ群は、途中で挿入・削除が起きたため、**当時の P28/P32/P33 が現在の slide 番号と一致しない**。  
このページ番号ずれが、修正意図の取りこぼしを生みやすくしている。

## 過去ログから読める本来の第4章

ログと正本を合わせると、第4章で本来伝えたいことは次の順序である。

1. **問題解決には流れがある**
2. **その中でも論点定義が最重要である**
3. **問いが間違うと後続の分解・仮説・検証が全部ずれる**
4. **良い論点は行動に結びつく**
5. **その実務上のチェックが『べき』である**
6. **上段の問いを解像度高く理解し、一文で固定する**

現在の第4章は、このうち 2, 3 が弱く、4, 5, 6 だけが前面に出ている。

## どう修正すべきか

### 優先度A: 第4章の1枚目を差し替える

今の [slide_32.html](/private/tmp/slides/slide_32.html) を第4章の実質1枚目にしている構成では弱い。  
最初に置くべきは、次のどちらかである。

- 「論点定義が最重要」
- 「問いが間違うと、その後の思考は全部ずれる」

ここでは `べき` をまだ主役にしない。  
まず **第4章の勝ち筋は『問いの発射角度を定める章』である** と腹落ちさせるべき。

### 優先度A: `べき` を“表現ルール”ではなく“判定基準”として置く

[slide_32.html](/private/tmp/slides/slide_32.html) 自体の方向は悪くない。  
ただし見出しの受け取り方が「語尾ルール」に寄る。

修正方針:

- 目的: 行動を決める問いになっているか
- 判定基準: `べき` が入っているか

という順に主従を明確化する。

### 優先度A: [slide_33.html](/private/tmp/slides/slide_33.html) を「3つの必須行動」に寄せる

正本では「実践ルール」よりも

- 上段の問いを解像度高く理解する
- 一文で明文化する
- `べき` を入れる

という**必須行動**の整理が強い。

したがって [slide_33.html](/private/tmp/slides/slide_33.html) は、一般的なルール一覧より、

- やること
- やらないと何が起きるか

が一目で分かる実務チェックリストの形に寄せた方がよい。

なお `最初に必ず論点を置く` は捨てる必要はないが、これは第4章の内側のルールというより、  
**問題解決全体の進め方に関するプロセス規律**である。置くなら [slide_26.html](/private/tmp/slides/slide_26.html) や [slide_29.html](/private/tmp/slides/slide_29.html) 側の方が自然である。

### 優先度B: 第3章末尾から第4章への橋を強くする

[slide_28.html](/private/tmp/slides/slide_28.html) と [slide_29.html](/private/tmp/slides/slide_29.html) は内容として悪くないが、第4章への接続が弱い。

過去ログにある

- 「今どの段階にいるのかを理解する」
- 「問題解決には流れがある」
- 「現実には行き来する」

という説明は、**第3章の締め**としては正しい。  
その代わり第4章の最初で、

- その流れの中で最も外すと痛いのが論点定義

を明示しないと、章境界が立たない。

### 優先度B: ページ番号ではなく意味単位でログを再接続する

今回のように `P28` などの参照は、スライド挿入後に崩れる。  
今後の修正ではページ番号ではなく、少なくとも以下の単位で追うべき。

- section_title
- slide title
- file path

すでに [deck-manifest.yaml](/private/tmp/slides/docs/ai-slide-system/deck-manifest.yaml) には `section_title` があるため、  
「第4章 論点定義」単位で履歴を束ね直す方が事故が少ない。

## 推奨する再構成

第4章は以下の4枚構成が自然。

1. **論点定義が最重要**
   - 問いが間違うと後続が全部ずれる
   - 「正しい問いの発射角度を担保する」を主張
2. **良い論点は行動に結びつく**
   - `べき` を判定基準として使う
   - 悪い問い vs 良い問い
3. **論点定義の3つの必須行動**
   - 上段の問いを解像度高く理解する
   - 一文で固定
   - `べき`
4. **第4章のまとめ**
   - 次章の「分解」に滑らかにつなぐ

現行の素材を生かすなら、

- 新規追加: 1枚
- 再編集: [slide_32.html](/private/tmp/slides/slide_32.html), [slide_33.html](/private/tmp/slides/slide_33.html)
- 維持: [slide_30.html](/private/tmp/slides/slide_30.html), [slide_31.html](/private/tmp/slides/slide_31.html), [slide_34.html](/private/tmp/slides/slide_34.html)

が最小変更である。

## 実務上の注意

今回のズレの根本原因は、内容そのものの質だけではなく、

- 章番号の繰り上がり
- 過去ログの `Pxx` 参照
- 分解章の古い具体例が前章に残っていた履歴

が混ざったことにある。

したがって次回以降は、

1. 正本は [/Users/yuta/workspace/shared/docs/problem-solving.md](/Users/yuta/workspace/shared/docs/problem-solving.md)
2. 章単位の整合は [deck-manifest.yaml](/private/tmp/slides/docs/ai-slide-system/deck-manifest.yaml)
3. 修正履歴は [history-ledger.md](/private/tmp/slides/docs/ai-slide-system/history-ledger.md)

の順で見るのがよい。
