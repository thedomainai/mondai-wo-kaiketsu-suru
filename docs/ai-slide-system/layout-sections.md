# Section-First Layout

この deck で新規作成・大幅改修を行うときの既定レイアウト方式。

## 原則

1. 先にレイアウト section を置く
2. その section の中に content を入れる
3. 重なりや余白は object 単位の微調整ではなく、section 配分で解く

`slide kind` を決めたあと、まず body safe area の中に section skeleton を作る。  
header / footer は shared runtime の責務、body の主要コンテンツは section の責務とする。

## 推奨手順

1. slide kind と one-message を決める
2. `main` または親 wrapper を置き、body safe area を確定する
3. `section` / `article` で主要 block を先に切る
4. grid / flex で section ごとの height / width / gap を先に配分する
5. その section の内側に content を置く
6. 図解の node や connector のような局所レイアウトだけ absolute positioning を使う
7. content が増減したら、先に section budget を再配分する

## Ownership Rule

- 主要 object は必ず owning section を持つ
- section を跨いで主要 object を重ねない
- page 全体へ直接 `top/left` で primary block を積み上げない
- 余白は section 間で管理し、孤立した dead space を残さない

## 許容される absolute positioning

以下は許容:

- section 内の図解 node
- connector, badge, annotation
- 局所的な micro-adjustment

以下は避ける:

- 主要 card / table / chart / paragraph block を page 直下へ絶対配置する
- overlap を個別要素の `top/left` 微調整だけで解消する
- copy 削除後も元の section 高さを据え置き、空白を放置する

## 推奨 DOM パターン

```html
<div class="slide-container slide-theme-paper" ...>
  <main class="content-stage">
    <section class="stage-intro">...</section>
    <section class="stage-axis">...</section>
    <section class="stage-cards">
      <div class="comparison-grid">
        <article class="person-card">...</article>
      </div>
    </section>
  </main>
</div>
```

命名は slide ごとに変わってよいが、考え方は固定する:

- 親 wrapper が body safe area を持つ
- section が高さ / 幅 / gap を持つ
- content は section の内側で完結する

## Completion Workflow（完成度ゲート）

スライドの作成・改修は、以下の 4 ステップを必ず通す。内容が正しくてもレイアウトが崩れた状態でタスク完了としない。**内容とビジュアルの両方が成立して初めて完了とする。**

### Step 1. レイアウト設計

表示する内容の全体像（テキスト量・図解の有無・カード枚数・注釈の長さ）を把握し、section skeleton と grid/flex の配分を先に決める。この時点ではダミーテキストや概算の高さで構わない。

確認ポイント:
- section 数と grid 列数がコンテンツ量に見合っているか
- 最も長いテキストブロックを想定して高さ budget を取っているか
- header(156px) + footer(60px) を差し引いた safe area 内に収まるか

### Step 2. コンテンツ配置

Step 1 のレイアウトにコンテンツを流し込む。テキスト・図解・バッジ・注釈を全て入れ切る。

### Step 3. ずれレビュー

コンテンツ配置後、以下の観点で視覚的なずれを点検する。

- テキストが section からはみ出していないか（overflow）
- カード間の高さが著しく不揃いになっていないか
- 余白が意図せず空きすぎ or 詰まりすぎていないか
- フッター(y=660px) にコンテンツが被っていないか
- 左右マージン（80px）が侵食されていないか
- フォントサイズ・行間がスケール内に収まっているか

### Step 4. 修正（コンテンツ優先）

ずれが見つかった場合、以下の優先順位で修正する。

1. **コンテンツ側を先に調整する** — テキストの圧縮・改行位置の変更・冗長な表現の削除・図解の簡素化で収める
2. **それでも解消しない場合のみレイアウトを修正する** — section の高さ再配分・grid 列数の変更・stage-top の調整・カードの min-height 変更

レイアウトを安易に壊すとデッキ全体の統一感が崩れる。コンテンツ調整で 8 割は解消できる。

### 判定基準

以下の全てを満たしたとき、そのスライドのタスクを完了とする。

- [ ] 伝えたい情報が全て含まれている（内容の完全性）
- [ ] テキスト・図解が section 内に収まっている（はみ出しゼロ）
- [ ] safe area (80px〜1200px, header下〜660px) 内で完結している
- [ ] DS トークンとクラスを使用している（ガバナンスルール準拠）
- [ ] 隣接スライドと視覚的な統一感がある

## Review 観点

- section skeleton が先に見えるか
- section の高さ配分に意味があるか
- object が section の内側で完結しているか
- overlap 修正を relayout で解いているか
- copy の増減が section 配分へ反映されているか
