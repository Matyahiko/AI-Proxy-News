# AI Proxy News Prototype – Concept & Technical Design

## 0. Version

* **v0.1** (2025‑06‑01) – initial draft

---

## 1. Purpose / Why?

> Deliver a **transparent, C2PA‑signed, AI‑assisted news workflow** that a solo graduate student can run end‑to‑end within two weeks and show to funding/mentoring bodies.

* **Transparency** – expose editorial credo, prompts, and raw artifacts.
* **Speed & Cost** – leverage existing cloud free tiers; manual steps accepted.
* **Extensibility** – lay foundation for future full‑automation, RAG and API.

## 2. Scope (MVP)

1. Record **1‑minute audio interview** (manual).
2. Whisper ASR → `transcript.txt` (auto).
3. GPT‑4o → *summary* + *follow‑up questions* (auto).
4. Append credo & metadata → `article.md` (auto).
5. **C2PA sign** → `article_signed.md` (auto).
6. Push to GitHub Pages → public URL (manual push).

## 3. User stories

| As a…                  | I want…                           | So that…                                              |
| ---------------------- | --------------------------------- | ----------------------------------------------------- |
| Graduate founder       | to show ONE signed article URL    | I can convince Osaka Innovation Hub that this is real |
| City incubator officer | to verify provenance in one click | I can judge compliance & innovation                   |
| Early reader           | to see full raw transcript        | I can audit trustworthiness                           |

## 4. High‑level architecture (textual)

```
┌─────────────┐   record.wav   ┌──────────────┐
│ mobile app  │──────────────►│   data/       │
└─────────────┘                └─────┬────────┘
                                     │ run_demo.sh
                                     ▼
                       (1) Whisper  ASR
                                     ▼
                       transcript.txt
                                     │
                                     ▼
                       (2) GPT‑4o  prompt chain
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
                       GitHub Pages  public URL
```

## 5. Component breakdown

| # | Component       | Tech                        | Responsibility                                                   |
| - | --------------- | --------------------------- | ---------------------------------------------------------------- |
| 1 | **Credo**       | `credo.json` (5‑6 lines)    | Declares editorial values; injected into prompts & C2PA manifest |
| 2 | **ASR**         | whisper.cpp CLI             | `wav -> txt`, language = ja                                      |
| 3 | **LLM Chain**   | OpenAI GPT‑4o via LangChain | summary (markdown) & next‑question list                          |
| 4 | **Signer**      | CAI `c2patool`              | embeds manifest incl. credo hash & SHA of sources                |
| 5 | **Static site** | GitHub Pages                | serves signed article                                            |
| 6 | **Scripts**     | bash / python               | glue logic; `.env` for API key                                   |

## 6. Data flow & files

```
/data/record.wav
/data/transcript.txt
/output/summary.md
/output/follow_up.md
/output/article.md           (summary + Qs + appendix)
/output/article_signed.md    (C2PA)
/docs/ (gh‑pages branch) ──┐
                           └─ article_signed.md
```

## 7. Prompt design (Japanese)

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

## 8. C2PA manifest template (YAML excerpt)

```yaml
credentials:
  credo_url: https://github.com/<user>/ai‑proxy‑news/blob/main/credo.json
  transcript_sha256: <auto‑calc>
  llm_model: gpt‑4o‑2025‑04‑preview
  asr_model: whisper‑large‑v3
```

## 9. Manual steps (v0.1)

1. Record WAV (phone) & copy to `data/`.
2. Run `bash scripts/run_demo.sh data/record.wav`.
3. Open `output/article_signed.md` → quick proofread.
4. `git add docs/article_signed.md && git commit -m "first article" && git push`.

## 10. Local setup

```bash
# Prereq: Python 3.11, ffmpeg, git
brew install whisper‑cpp ffmpeg
pip install -r requirements.txt   # LangChain, openai, c2patool, python‑dotenv
export OPENAI_API_KEY=sk‑…
./scripts/run_demo.sh data/record.wav
```

## 11. Security / compliance notes

* Store API key only in local `.env`; never commit.
* C2PA manifest contains **no personal data**; only hashes & public credo URL.
* Interviewee must consent to recording (template in `/legal/consent_ja.md`).

## 12. Future backlog

1. **Streamlit signer GUI** – eliminate CLI friction.
2. **RAG contextualiser** – inject local gov docs into prompt.
3. **Remote execution** – GitHub Actions CI to auto‑sign & deploy.
4. **Multi‑modal** – add image capture + C2PA sidecar.

## 13. Review checklist (for mentors)

* [ ] Can run end‑to‑end offline?
* [ ] Credo ‑> manifest hash verified?
* [ ] Output readable on mobile?
* [ ] Interviewee consent collected?

---

### End of v0.1 design

