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
`http://localhost:7000/demo.html` を開いて確認できます。

```bash
bash scripts/serve_docs.sh [ポート番号]
```

ポート番号を省略すると `7000` で起動します。

### リアルタイム文字起こしを試す

別のターミナルで WebSocket サーバー `scripts/realtime_server.py` を起動すると、
`demo.html` 再生時に動画の音声が Google Speech-to-Text へ送信され、右側の
"リアルタイム文字起こし" パネルに逐次表示されます。

```bash
python3 scripts/realtime_server.py
```

このデモでは、動画の音声を WebM/Opus として
Google Speech-to-Text へ送信します。`GOOGLE_APPLICATION_CREDENTIALS`
環境変数など、認証情報の設定も忘れずに行ってください。
接続後に "READY" メッセージが届いたら録音が開始されます。

`ASR_PORT` 環境変数で待ち受けポートを変更できます。

#### Docker コンテナで同時に起動する

HTTP サーバーとリアルタイム文字起こしサーバーを一度に立ち上げたい場合は、
`scripts/run_realtime_demo.sh` を実行します。デフォルトではポート `7000` と
`7001` を使用しますが、引数で変更可能です。ポートを開けておくとブラウザから
<http://localhost:7000/demo.html> にアクセスできます。

```bash
docker run --rm -it \
  -p 7000:7000 -p 7001:7001 \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/run_realtime_demo.sh
```

ポートを変更したい場合は、スクリプトの引数として指定します。例えば

```bash
docker run --rm -it \
  -p 8000:8000 -p 8765:8765 \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/run_realtime_demo.sh 8000 8765
```

WebSocket のポートを変更した場合は、`docs/site/demo.script.js` 内の
`WebSocket` 接続先も同じ値に書き換えてください。
