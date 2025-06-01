# AI Proxy News プロトタイプ

このリポジトリは、透明性の高い C2PA 署名付き AI 支援ニュースワークフローの最小プロトタイプです。短いインタビューを録音し、Google Speech-to-Text で文字起こしを行い、Gemini API で要約と追加質問を生成し、C2PA で署名した記事を GitHub Pages で公開することを目指します。

詳細な設計は `docs/design.md`、手順は `docs/workflow.md` を参照してください。

API キーを含む `.env` ファイルはリポジトリのルートに配置してください。
