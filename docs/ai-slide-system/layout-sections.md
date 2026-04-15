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

## Review 観点

- section skeleton が先に見えるか
- section の高さ配分に意味があるか
- object が section の内側で完結しているか
- overlap 修正を relayout で解いているか
- copy の増減が section 配分へ反映されているか
