# Workflow

This document outlines the end-to-end process for producing a signed article using the prototype.

1. **Capture audio**: record a short interview and save it as a WAV file, e.g. `data/record.wav`.
2. **Run the demo script**: execute `./scripts/run_demo.sh data/record.wav`.
   - This performs speech-to-text with Whisper.
   - It then calls GPT-4o to generate a summary and follow-up questions.
   - The resulting `article.md` is signed with C2PA.
   - A signed copy `article_signed.md` is placed in `docs/`.
3. **Review**: open `docs/article_signed.md` and make any edits if necessary.
4. **Publish**: commit the file and push to GitHub. GitHub Pages will host the signed article.

All intermediate files remain in `output/`. You can inspect them for transparency.

