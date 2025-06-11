# AI Proxy News プロトタイプ ― 概念・技術設計

## 0. バージョン

* **v0.1** (2025‑06‑01) – 初版

---

## 1. 目的 / Why?

> 大学院生ひとりでも2週間以内に実行でき、資金提供者やメンターに示すことのできる**透明性の高い AI 支援ニュースワークフロー**を提供する。

* **透明性** ― クレド、プロンプト、生成物などを全て公開する。
* **速度とコスト** ― 既存のクラウド無料枠を利用し、手動工程も許容する。
* **拡張性** ― 将来の完全自動化や RAG、API 化へつながる基盤を作る。

## 2. スコープ (MVP)

1. **1 分間の音声インタビューを録音**（手動）
2. Google Speech-to-Text の長時間音声用 API → `transcript.txt`（自動）
3. Gemini API → *要約* + *追加質問*（自動）
4. クレドとメタデータを追加 → `article.md`（自動）
5. GitHub Pages へプッシュ → 公開 URL（手動）

## 3. ユーザーストーリー

| 立場                 | 望むこと                              | その理由                                   |
| -------------------- | ------------------------------------ | ------------------------------------------ |
| 大学院生の創業者     | 1 件の署名記事の URL を示したい        | 大阪イノベーションハブに本物だと示すため   |
| 市のインキュベータ担当 | ワンクリックで出所を確認したい        | 適合性と革新性を判断するため               |
| 早期読者             | 生の逐語録をすべて見たい               | 信頼性を検証するため                       |

## 4. ハイレベルアーキテクチャ（テキスト）

```
┌─────────────┐   record.mp3   ┌──────────────┐
│ mobile app  │──────────────►│   data/       │
└─────────────┘                └─────┬────────┘
                                     │ run_demo.sh
                                     ▼
                       upload to GCS
                                     ▼
                       (1) Google STT
                                     ▼
                       transcript.txt
                                     │
                                     ▼
                       (2) Gemini prompt chain
                                     ▼
                       summary.md + follow_up.md
                                     ▼
                       article.md
                                     │
                          git push (manual)
                                     ▼
                       GitHub Pages  public URL
```

## 5. コンポーネント一覧

| # | コンポーネント   | 技術                         | 役割                                       |
| - | --------------- | --------------------------- | ----------------------------------------- |
| 1 | **Credo**       | `credo.json` (5～6行)       | 編集方針を宣言し、プロンプトに埋め込む |
| 2 | **ASR**         | Google Speech-to-Text (長時間音声用 API)            | `wav -> txt`, 言語 = ja                   |
| 3 | **LLM チェーン** | Gemini API  | 要約 (markdown) と 次の質問リスト          |
| 4 | **静的サイト**   | GitHub Pages               | 記事を配信                         |
| 5 | **スクリプト**   | bash / python              | つなぎ処理; `secrets/.env` に API キーを保存 |

## 6. データフローとファイル

```
/data/record.mp3 (or .wav/.mp4)
gs://<bucket>/record.wav
/data/transcript.txt
/output/summary.md
/output/follow_up.md
/output/article.md           (summary + Qs + appendix)
/docs/ (gh‑pages branch) ──┐
                           └─ article.md
```

## 7. プロンプト設計（日本語）

```text
<<SYSTEM>> あなたは公共利益を最優先するAI記者です。Credo: {{credo}}
<<USER>> 次のインタビュー逐語録を要約し、追加質問を3つ出力してください:
===
{{transcript}}
===
### 出力フォーマット
#### 要約
- ...
#### 追加質問
1. ...
2. ...
3. ...
```

## 8. 手作業ステップ (v0.1)

1. 携帯で音声を録音し `data/` にコピー（mp3/mp4/wav いずれも可）
2. `bash scripts/run_demo.sh data/record.mp3` を実行
   - 音声は Google Cloud Storage にアップロードされ、URI 指定で音声認識が行われます。
3. `output/article.md` を開いて軽く校正。必要に応じて `raw_gpt_output.md` を参照
4. `git add docs/article.md && git commit -m "first article" && git push`

## 10. ローカル環境構築

```bash
# 前提: Python 3.11、ffmpeg、git
brew install ffmpeg
pip install -r requirements.txt   # google-cloud-speech, google-generativeai, python-dotenv, google-cloud-storage
export GOOGLE_APPLICATION_CREDENTIALS=secrets/credentials.json
export GEMINI_API_KEY=...
export GCS_BUCKET=<your-bucket>
./scripts/run_demo.sh data/record.mp3
```

## 11. セキュリティ・コンプライアンス

* API キーは `secrets/.env` のみに保存し、決してコミットしない。
* インタビュイーの同意を得ること（雛形は `/legal/consent_ja.md` にあり）。

## 12. 今後の予定

1. **RAG コンテクスチュアライザー** ― ローカル自治体資料をプロンプトに注入

## 13. レビュー用チェックリスト（メンター向け）

* [ ] オフラインで一連の流れを実行できるか
* [ ] モバイルで表示が読みやすいか
* [ ] インタビュイーの同意を取得したか

---

### v0.1 設計書 終わり
