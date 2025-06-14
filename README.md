# AI Proxy News プロトタイプ

このリポジトリは、透明性の高い AI 支援ニュースワークフローの最小プロトタイプです。短いインタビューを録音し、Google Speech-to-Text の長時間音声用 API で文字起こしを行い、Gemini API で要約と追加質問を生成した記事を 静的サイトとして保存し、任意の方法で公開できるようにします。

詳細な設計は `docs/spec/design.md`、手順は `docs/spec/workflow.md` を参照してください。

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

生成された `docs/site/article.md` をコミットし、静的サイトとして任意の方法で公開してください。

## ローカルでデモサイトを表示する

`docs/site/` ディレクトリにはデモ用の `demo.html` が含まれています。
`scripts/serve_docs.sh` を実行すると、プロジェクトルートの `data/` ディレクトリ
にある動画ファイルを自動で読み込み、簡易 HTTP サーバーを起動します。ブラウザで
`http://localhost:8000/demo.html` を開いて確認できます。

```bash
bash scripts/serve_docs.sh [ポート番号]
```

ポート番号を省略すると `8000` で起動します。

### リアルタイム文字起こしを試す

別のターミナルで WebSocket サーバー `scripts/realtime_server.py` を起動すると、
`demo.html` 再生時に動画の音声が Google Speech-to-Text へ送信され、右側の
"リアルタイム文字起こし" パネルに逐次表示されます。

```bash
python3 scripts/realtime_server.py
```

`ASR_PORT` 環境変数で待ち受けポートを変更できます。

### まとめて実行する

リアルタイムサーバーとデモサイトを同時に起動するスクリプト
`scripts/start_realtime_demo.sh` を用意しています。仮想環境が自動で作成され、
依存パッケージのインストールからサーバー起動までを一括で行います。

```bash
bash scripts/start_realtime_demo.sh
```

終了すると両方のサーバーが停止します。

Docker コンテナ内で実行する場合の例:

```bash
docker run --rm -it \
  -p 8000:8000 \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/start_realtime_demo.sh
```
