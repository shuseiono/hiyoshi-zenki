# 模擬国連 — 日吉前期

一次資料・会議準備・AI議論用メモの作業用リポジトリ。

GitHub Pages: https://shuseiono.github.io/hiyoshi-zenki/（`docs/` を公開）

## フォルダ構成

| フォルダ | 用途 |
|----------|------|
| `一次資料/pdf/` | 公式原文（PDF） |
| `一次資料/markdown/` | PDF 変換テキスト（カテゴリ別）・[目次](一次資料/markdown/README.md) |
| `二次資料/` | 学術論文・書籍・模擬国連手法の参考 PDF・[目次](二次資料/README.md) |
| `会議準備/` | 配布 PDF（国割・BG）・国内ミート KPI・[ミート・メンター](会議準備/ミート・メンター/) メモ |
| `会議設計/` | Claude リサーチ成果物（**作業の正本**） |
| `会議設計/参考/` | 過去 BG 等の参考 PDF |
| `docs/` | GitHub Pages 公開用（`会議設計/` からレビュー後に同期） |
| `reviews/` | HTMLレビュー用 bundle（reviewable-html-workbench） |
| `対AI/` | Claude 等との議論用 Markdown |
| `bin/` | レビュービルド・docs 同期などの補助スクリプト |

## 運用ルール

- **一次 vs 二次**: UN/ILO 等の公式文書 → `一次資料/`。論文・解説・書籍 → `二次資料/`
- **会議設計 vs docs**: 編集は `会議設計/` で行い、公開前に `bin/sync-docs.sh` で `docs/` へ反映
- **会議準備**: 配布物 PDF と国内ミート関連（KPI・メンターメモ）をまとめる
