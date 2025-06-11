# ワークフロー

このドキュメントは、プロトタイプを用いて署名済みの記事を作成するまでの流れを示します。

1. **音声を収録**: 短いインタビューを録音し、例として `data/record.mp3` などに保存します。
2. **デモスクリプトを実行**: `./scripts/run_demo.sh data/record.mp3` を実行します。
   - Google Speech-to-Text の長時間音声用 API で音声からテキストへ変換します。
   - 続いて Gemini API で要約と追加質問を生成します。
   - 生成された `article.md` に C2PA 署名を付与します。
   - 署名済みファイル `article_signed.md` が `docs/` に配置されます。
3. **確認**: `docs/article_signed.md` を開き、必要に応じて編集します。
4. **公開**: ファイルをコミットして GitHub にプッシュすると、GitHub Pages で記事が公開されます。

中間ファイルはすべて `output/` に残るため、透明性を確保できます。

