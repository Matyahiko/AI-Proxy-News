# AI Proxy News プロトタイプ

このリポジトリは、透明性の高い AI 支援ニュースワークフローの最小プロトタイプです。短いインタビューを録音し、Google Speech-to-Text の長時間音声用 API で文字起こしを行い、Gemini API で要約と追加質問を生成した記事を GitHub Pages で公開することを目指します。

詳細な設計は `docs/design.md`、手順は `docs/workflow.md` を参照してください。

API キーなどの認証情報は `secrets/.env` にまとめて保存してください。

## Docker での実行

1. `.env.example` を参考に `secrets/.env` を作成し、API キーと `GCS_BUCKET` を記入します。
2. 以下のコマンドでイメージをビルドします。 `secrets/.env` に `PROXY` を設定す
   ると自動で利用されます。`docker build` だけでビルドする場合は
   `--build-arg PROXY=<proxy-url>` を渡してください。

```bash
bash scripts/build_image.sh
# 例: プロキシを指定して直接ビルドする場合
docker build --build-arg PROXY=http://example.com:8080 -t ai-proxy-news .
```
3. 任意で Gemini の利用可能なモデルを確認します。

```bash
python3 scripts/list_models.py
```


4. 音声ファイル `data/record.wav` や `data/record.mp3` などを用意し、次を実行してデモを開始します。音声は Google Cloud Storage にアップロードされ、URI で認識されます。

```bash
docker run --rm -it \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/run_demo.sh data/record.mp3
```

生成された `docs/article.md` をコミットして GitHub Pages へ公開してください。

## ローカルでデモサイトを表示する

`docs/` ディレクトリには、インタビュー動画のサンプルを使ったデモサイト
(`demo.html`) が含まれています。以下のスクリプトで簡易 HTTP サーバーを起動し、
ブラウザで `http://localhost:8000/demo.html` を開いて確認できます。

```bash
bash scripts/serve_docs.sh [ポート番号]
```

ポート番号を省略すると `8000` で起動します。
