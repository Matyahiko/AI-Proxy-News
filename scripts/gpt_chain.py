#!/usr/bin/env python3
import os
import sys
import json
import re
from typing import Tuple, Optional
import google.generativeai as genai
from config import validate_gemini_config

if len(sys.argv) != 3:
    print("Usage: gpt_chain.py <transcript_txt> <output_dir>")
    sys.exit(1)

api_key = validate_gemini_config()
genai.configure(api_key=api_key)

transcript_path = sys.argv[1]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)
print(f"[GPT] Processing transcript '{transcript_path}'...")

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

model = genai.GenerativeModel("gemini-2.5-pro-preview-06-05")
response = model.generate_content([system_msg, user_msg])
content = response.text

with open(os.path.join(output_dir, "raw_gpt_output.md"), "w", encoding="utf-8") as f:
    f.write(content)

summary_lines, question_lines = parse_ai_response(content)

write_output_files(output_dir, summary_lines, question_lines)
if not summary_lines or not question_lines:
    print("[GPT] Warning: unable to parse expected sections. See raw_gpt_output.md for details")
print(f"[GPT] Generated article files in '{output_dir}'")


def parse_ai_response(content: str) -> Tuple[list, list]:
    """Parse AI response to extract summary and questions sections.
    
    Returns:
        Tuple of (summary_lines, question_lines)
    """
    summary_lines = []
    question_lines = []
    section = None
    
    # Try structured parsing first
    lines = content.splitlines()
    for line in lines:
        # Look for section headers
        if line.startswith("#### ") or line.startswith("##"):
            if "要約" in line or "summary" in line.lower():
                section = "summary"
            elif "追加質問" in line or "question" in line.lower() or "質問" in line:
                section = "questions"
            continue
            
        # Add content to current section
        if section == "summary":
            summary_lines.append(line)
        elif section == "questions":
            question_lines.append(line)
    
    # Fallback: try regex-based extraction if structured parsing failed
    if not summary_lines or not question_lines:
        summary_match = re.search(r'要約[\s]*[\n]+([\s\S]*?)(?=追加質問|$)', content, re.MULTILINE)
        if summary_match:
            summary_lines = [line.strip() for line in summary_match.group(1).strip().split('\n') if line.strip()]
            
        questions_match = re.search(r'追加質問[\s]*[\n]+([\s\S]*?)$', content, re.MULTILINE)
        if questions_match:
            question_lines = [line.strip() for line in questions_match.group(1).strip().split('\n') if line.strip()]
    
    return summary_lines, question_lines


def write_output_files(output_dir: str, summary_lines: list, question_lines: list) -> None:
    """Write parsed content to output files."""
    with open(os.path.join(output_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines).strip() + "\n")

    with open(os.path.join(output_dir, "follow_up.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(question_lines).strip() + "\n")

    with open(os.path.join(output_dir, "article.md"), "w", encoding="utf-8") as f:
        f.write("## 要約\n")
        f.write("\n".join(summary_lines).strip() + "\n\n")
        f.write("## 追加質問\n")
        f.write("\n".join(question_lines).strip() + "\n")
