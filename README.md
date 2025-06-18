# AI Proxy News プロトタイプ

このリポジトリは、透明性の高い AI 支援ニュースワークフローの最小プロトタイプです。短いインタビューを録音し、Google Speech-to-Text の長時間音声用 API で文字起こしを行い、Gemini API で要約と追加質問を生成した記事を 静的サイトとして保存し、任意の方法で公開できるようにします。

詳細な設計は `docs/spec/design.md`、手順は `docs/spec/workflow.md` を参照してください。

API キーなどの認証情報は `secrets/.env` にまとめて保存してください。

## 実行方法

### Docker Compose での実行（推奨）

1. `.env.example` を参考に `secrets/.env` を作成し、API キーと `GCS_BUCKET` を記入します。
2. 全サービスを起動します（Webサーバー: ポート12000、ASRサーバー: ポート12001）：

```bash
# 全サービスを起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d --build

# サービスを停止
docker-compose down
```

3. メインワークフローの実行：

```bash
# 音声ファイルを処理してデモを実行
docker-compose run --rm demo bash scripts/run_demo.sh data/record.mp3
```

### ローカル開発での実行

```bash
# 依存関係をインストール
pip install -r requirements.txt

# Gemini の利用可能なモデルを確認
python3 scripts/list_models.py

# メインワークフローを実行
bash scripts/run_demo.sh data/record.mp3

# デモサイトを起動（デフォルトポート12000）
bash scripts/serve_docs.sh [port]

# リアルタイム文字起こしサーバーを起動（ポート12001）
python3 scripts/realtime_server.py

# Webサーバーとリアルタイム文字起こしを同時起動
bash scripts/run_realtime_demo.sh [docs_port] [asr_port]
```

### 従来のDocker実行（レガシー）

```bash
# イメージをビルド
bash scripts/build_image.sh

# メインワークフローを実行
docker run --rm -it \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/run_demo.sh data/record.mp3
```

生成された `docs/site/article.md` をコミットし、静的サイトとして任意の方法で公開してください。

## デモサイトの表示

### Docker Compose使用時

```bash
docker-compose up --build
```

起動後、ブラウザで `http://localhost:12000/demo.html` にアクセスしてください。

### ローカル実行時

`docs/site/` ディレクトリにはデモ用の `demo.html` が含まれています。
`scripts/serve_docs.sh` を実行すると、プロジェクトルートの `data/` ディレクトリ
にある動画ファイルを自動で読み込み、簡易 HTTP サーバーを起動します。

```bash
bash scripts/serve_docs.sh [ポート番号]
```

ポート番号を省略すると `12000` で起動します。ブラウザで `http://localhost:12000/demo.html` を開いて確認できます。

### リアルタイム文字起こしを試す

別のターミナルで WebSocket サーバー `scripts/realtime_server.py` を起動すると、
`demo.html` 再生時に動画の音声が Google Speech-to-Text へ送信され、右側の
"リアルタイム文字起こし" パネルに逐次表示されます。

```bash
python3 scripts/realtime_server.py
```

`ASR_PORT` 環境変数で待ち受けポートを変更できます（デフォルト: 12001）。

#### 従来のDockerコンテナで同時に起動する

HTTP サーバーとリアルタイム文字起こしサーバーを一度に立ち上げたい場合は、
`scripts/run_realtime_demo.sh` を実行します。デフォルトではポート `12000` と
`12001` を使用しますが、引数で変更可能です。

```bash
docker run --rm -it \
  -p 12000:12000 -p 12001:12001 \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/run_realtime_demo.sh 12000 12001
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
