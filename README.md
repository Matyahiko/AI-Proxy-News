# AI Proxy News プロトタイプ

このリポジトリは、透明性の高い C2PA 署名付き AI 支援ニュースワークフローの最小プロトタイプです。短いインタビューを録音し、Google Speech-to-Text で文字起こしを行い、Gemini API で要約と追加質問を生成し、C2PA で署名した記事を GitHub Pages で公開することを目指します。

詳細な設計は `docs/design.md`、手順は `docs/workflow.md` を参照してください。

API キーを含む `.env` ファイルはリポジトリのルートに配置してください。

## Docker での実行

1. `.env.example` を参考に API キーを記入した `.env` を作成します。
2. 以下のコマンドでイメージをビルドします。

```bash
docker build -t ai-proxy-news .
```

3. 音声ファイル `data/record.wav` を用意し、次を実行してデモを開始します。

```bash
docker run --rm -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/docs:/app/docs \
  --env-file .env \
  ai-proxy-news bash scripts/run_demo.sh data/record.wav
```

生成された `docs/article_signed.md` をコミットして GitHub Pages へ公開してください。
