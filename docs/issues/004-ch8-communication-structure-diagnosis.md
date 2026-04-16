# 第8章 構成診断

## 対象

- [slide_62.html](/private/tmp/slides/slide_62.html)
- [slide_63.html](/private/tmp/slides/slide_63.html)
- [slide_64.html](/private/tmp/slides/slide_64.html)
- [slide_65.html](/private/tmp/slides/slide_65.html)
- [slide_66.html](/private/tmp/slides/slide_66.html)
- [slide_67.html](/private/tmp/slides/slide_67.html)
- [slide_68.html](/private/tmp/slides/slide_68.html)
- [slide_69.html](/private/tmp/slides/slide_69.html)
- [slide_70.html](/private/tmp/slides/slide_70.html)
- [slide_71.html](/private/tmp/slides/slide_71.html)
- 構成の正本: [/Users/yuta/workspace/shared/docs/problem-solving.md](/Users/yuta/workspace/shared/docs/problem-solving.md)

## 結論

現状の第8章は、内容そのものが悪いのではなく、**章の背骨が途中で二重化して見えること**が問題だった。

主な論点は次の3つ。

1. **前半の「受け手を読む話」と後半の「解を組み立てる話」の切り替わりが明示されていない**
2. **`slide_71.html` が終盤で新しい原理を追加して見え、`slide_66.html` - `slide_68.html` と競合していた**
3. **`slide_62.html` と [slide_63.html](/private/tmp/slides/slide_63.html) の導入コピーが実質的に重複し、章の立ち上がりが少し冗長だった**

その結果、第8章は本来

- 相手を読む
- 解を組み立てる
- 伝達前にチェックする

という素直な流れで読めるはずなのに、実際には

- 原理
- 似た原理の再説明
- 実務の型
- さらに別の構造原理

と受け取られやすくなっていた。

## 現状診断

### 1. 前半と後半の役割分担が、見出しだけでは見えにくい

- [slide_62.html](/private/tmp/slides/slide_62.html): コミュニケーションの原理
- [slide_63.html](/private/tmp/slides/slide_63.html): 受け手視点の3軸
- [slide_64.html](/private/tmp/slides/slide_64.html): 意思決定構造
- [slide_65.html](/private/tmp/slides/slide_65.html): 誤解ポイント

ここまでは「相手を読む」章として自然だが、[slide_66.html](/private/tmp/slides/slide_66.html) がいきなり5要素の説明に入るため、章の切り替わりが急だった。

### 2. `slide_71.html` が“締め”ではなく“別フレームの追加”に見えていた

もともとの [slide_66.html](/private/tmp/slides/slide_66.html) - [slide_70.html](/private/tmp/slides/slide_70.html) で、

- 結論
- 根拠
- ネクストアクション
- 残論点
- 情報確度

という伝え方の骨格はすでに提示されていた。

その直後に [slide_71.html](/private/tmp/slides/slide_71.html) で「ピラミッドストラクチャー」を独立テーマとして置くと、

- 5要素と別の話なのか
- 結論と根拠の補足なのか
- 章の最後に新しい理論を追加しているのか

が一読で判定しづらかった。

### 3. 導入のコピーが重複していた

[slide_62.html](/private/tmp/slides/slide_62.html) と [slide_63.html](/private/tmp/slides/slide_63.html) は、どちらも「伝えるとは、自分の頭の中をそのまま出すことではない」という主張を前面に置いていた。

原理そのものは正しいが、章の立ち上がりとしては

- まず原理を置く
- 次に見るべき軸を置く

に役割分担した方が読みやすい。

## 実装方針

### 方針A: `slide_66.html` を章の背骨にする

`5要素の一覧` 単体ではなく、

- Step 1: 受け手を読む
- Step 2: 5要素で解を組み立てる

という2段階のブリッジに再設計する。

これにより、`slide_63.html` - `slide_65.html` と `slide_67.html` - `slide_70.html` が同じ章の中でどうつながるかが明示される。

### 方針B: `slide_71.html` は新理論の追加ではなく最終チェックに変える

ピラミッドの考え方自体は残しつつ、

- 結論から根拠・事実へ上下でつながっているか
- So What / Why So で往復できるか

をチェック項目として統合する。

これで終盤は「話を増やす」のではなく「章を閉じる」役割になる。

### 方針C: `slide_63.html` は導入の重複を外し、観点提示に寄せる

章原理の繰り返しではなく、「受け手を読む3軸」を短く言い切る導入に変更する。

## 実施内容

1. [slide_63.html](/private/tmp/slides/slide_63.html) の kicker を観点提示型に変更
2. [slide_66.html](/private/tmp/slides/slide_66.html) を「読む→組み立てる」の2段階ブリッジに再設計
3. [slide_71.html](/private/tmp/slides/slide_71.html) を章の最終チェックに差し替え

## 期待効果

- 第8章の前半と後半の役割分担が明確になる
- 「解のコミュニケーション」の重複感が薄くなる
- 章末が新規論点の追加ではなく、実務チェックとして自然に閉じる
