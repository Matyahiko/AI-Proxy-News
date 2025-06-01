# AI Proxy News プロトタイプ ― 概念・技術設計

## 0. バージョン

* **v0.1** (2025‑06‑01) – 初版

---

## 1. 目的 / Why?

> 大学院生ひとりでも2週間以内に実行でき、資金提供者やメンターに示すことのできる**透明性の高い C2PA 署名付き AI 支援ニュースワークフロー**を提供する。

* **透明性** ― クレド、プロンプト、生成物などを全て公開する。
* **速度とコスト** ― 既存のクラウド無料枠を利用し、手動工程も許容する。
* **拡張性** ― 将来の完全自動化や RAG、API 化へつながる基盤を作る。

## 2. スコープ (MVP)

1. **1 分間の音声インタビューを録音**（手動）
2. Google Speech-to-Text → `transcript.txt`（自動）
3. Gemini API → *要約* + *追加質問*（自動）
4. クレドとメタデータを追加 → `article.md`（自動）
5. **C2PA 署名** → `article_signed.md`（自動）
6. GitHub Pages へプッシュ → 公開 URL（手動）

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
                       (1) Google STT
                                     ▼
                       transcript.txt
                                     │
                                     ▼
                       (2) Gemini prompt chain
                                     ▼
                       summary.md + follow_up.md
                                     │
                                     ▼
                       (3) C2PA sign (c2patool)
                                     ▼
                       article_signed.md
                                     │
                          git push (manual)
                                     ▼
                       GitHub Pages  public URL
```

## 5. コンポーネント一覧

| # | コンポーネント   | 技術                         | 役割                                       |
| - | --------------- | --------------------------- | ----------------------------------------- |
| 1 | **Credo**       | `credo.json` (5～6行)       | 編集方針を宣言し、プロンプトと C2PA マニフェストに埋め込む |
| 2 | **ASR**         | Google Speech-to-Text            | `wav -> txt`, 言語 = ja                   |
| 3 | **LLM チェーン** | Gemini API  | 要約 (markdown) と 次の質問リスト          |
| 4 | **署名ツール**   | CAI `c2patool`             | マニフェストに credo のハッシュとソース SHA を含める |
| 5 | **静的サイト**   | GitHub Pages               | 署名済み記事を配信                         |
| 6 | **スクリプト**   | bash / python              | つなぎ処理; `.env` に API キーを保存        |

## 6. データフローとファイル

```
/data/record.mp3 (or .wav/.mp4)
/data/transcript.txt
/output/summary.md
/output/follow_up.md
/output/article.md           (summary + Qs + appendix)
/output/article_signed.md    (C2PA)
/docs/ (gh‑pages branch) ──┐
                           └─ article_signed.md
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

## 8. C2PA マニフェストテンプレート（YAML 抜粋）

```yaml
credentials:
  credo_url: https://github.com/<user>/ai-proxy-news/blob/main/credo.json
  transcript_sha256: <auto-calc>
  llm_model: gemini-pro
  asr_model: google-speech-to-text
```

## 9. 手作業ステップ (v0.1)

1. 携帯で音声を録音し `data/` にコピー（mp3/mp4/wav いずれも可）
2. `bash scripts/run_demo.sh data/record.mp3` を実行
3. `output/article_signed.md` を開いて軽く校正
4. `git add docs/article_signed.md && git commit -m "first article" && git push`

## 10. ローカル環境構築

```bash
# 前提: Python 3.11、ffmpeg、git
brew install ffmpeg
pip install -r requirements.txt   # google-cloud-speech, google-generativeai, python-dotenv
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export GEMINI_API_KEY=...
./scripts/run_demo.sh data/record.mp3
```

## 11. セキュリティ・コンプライアンス

* API キーはリポジトリのルートに置いた `.env` にのみ保存し、決してコミットしない。
* C2PA マニフェストには **個人情報は含まない**。ハッシュと公開クレド URL のみ。
* インタビュイーの同意を得ること（雛形は `/legal/consent_ja.md` にあり）。

## 12. 今後の予定

1. **Streamlit 署名 GUI** ― CLI の手間を排除
2. **RAG コンテクスチュアライザー** ― ローカル自治体資料をプロンプトに注入
3. **リモート実行** ― GitHub Actions で自動署名・デプロイ
4. **マルチモーダル** ― 画像キャプチャ + C2PA サイドカー追加

## 13. レビュー用チェックリスト（メンター向け）

* [ ] オフラインで一連の流れを実行できるか
* [ ] Credo → マニフェストのハッシュ検証済みか
* [ ] モバイルで表示が読みやすいか
* [ ] インタビュイーの同意を取得したか

---

### v0.1 設計書 終わり
