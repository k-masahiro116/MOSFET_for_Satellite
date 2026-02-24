# MOSFET_for_Satellite

このリポジトリは、衛星システムにおける MOSFET の利用に関する作業をまとめます。

## 概要
- 目的: MOSFET 選定と設計に関するメモ、データ、実験結果を整理する。

## プレビュー
- [Base page preview](https://htmlpreview.github.io/?https://raw.githubusercontent.com/k-masahiro116/MOSFET_for_Satellite/codex/work/docs/research/base.html)

## はじめに
1. リポジトリをクローンします。
2. 文書・スクリプト・データを適切なフォルダに追加します。

## 構成（予定）
- `docs/`: 設計メモや参考資料。
- `data/`: 測定データや解析結果。
- `src/`: スクリプトやシミュレーション。

## コントリビュート
`codex/` プレフィックスのブランチを作成し、プルリクエストで変更を提出してください。

## コミットメッセージ規則
チーム開発で読みやすく、追跡しやすい履歴にするため、以下を推奨します。
参考: [SE-EDU の best practices](https://se-education.org/learningresources/contents/revisionControl/bestPracticesGit.html), [Conventional Commits](https://www.conventionalcommits.org/)

- 件名と本文は空行で区切る
- 件名は 50 文字以内（厳密な上限は 72 文字）
- 件名は先頭大文字・末尾ピリオドなし
- 件名は命令形（例: Add, Fix, Update）で書く
- 本文は 72 文字で折り返す
- 本文には「何を」「なぜ」を書き、「どうやって」は書かない

さらに、変更種別を明確にするため `Conventional Commits` 形式を推奨します:
`<type>[optional scope]: <description>`

例:
- `docs: add research plan page`
- `feat(power): add MOSFET candidate list`

## ライセンス
未定
