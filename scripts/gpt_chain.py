#!/usr/bin/env python3
import os
import sys
import json
import google.generativeai as genai
from dotenv import load_dotenv

if len(sys.argv) != 3:
    print("Usage: gpt_chain.py <transcript_txt> <output_dir>")
    sys.exit(1)

load_dotenv(os.path.join("secrets", ".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

transcript_path = sys.argv[1]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)

with open("credo.json", encoding="utf-8") as f:
    credo = json.load(f)

with open(transcript_path, encoding="utf-8") as f:
    transcript = f.read()

system_msg = f"あなたは公共利益を最優先するAI記者です。Credo: {json.dumps(credo, ensure_ascii=False)}"
user_msg = (
    "次のインタビュー逐語録を要約し、追加質問を3つ出力してください:\n==="
    + transcript
    + "\n===\n### 出力フォーマット\n#### 要約\n- ...\n#### 追加質問\n1. ...\n2. ...\n3. ..."
)

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content([system_msg, user_msg])
content = response.text

summary_lines = []
question_lines = []
section = None
for line in content.splitlines():
    if line.startswith("#### "):
        if "要約" in line:
            section = "summary"
        elif "追加質問" in line:
            section = "questions"
        continue
    if section == "summary":
        summary_lines.append(line)
    elif section == "questions":
        question_lines.append(line)

with open(os.path.join(output_dir, "summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines).strip() + "\n")

with open(os.path.join(output_dir, "follow_up.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(question_lines).strip() + "\n")

with open(os.path.join(output_dir, "article.md"), "w", encoding="utf-8") as f:
    f.write("## 要約\n")
    f.write("\n".join(summary_lines).strip() + "\n\n")
    f.write("## 追加質問\n")
    f.write("\n".join(question_lines).strip() + "\n")
