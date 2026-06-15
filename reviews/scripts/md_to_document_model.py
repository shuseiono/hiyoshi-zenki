#!/usr/bin/env python3
"""Convert Claude research markdown into a reviewable HTML document model."""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\u3040-\u30ff\u3400-\u9fff-]+", "-", text.strip().lower())
    return cleaned.strip("-") or "section"


def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def convert_table(lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    parts = ["<table><thead><tr>"]
    parts.extend(f"<th>{md_inline(cell)}</th>" for cell in head)
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>")
        parts.extend(f"<td>{md_inline(cell)}</td>" for cell in row)
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def convert_block(text: str) -> str:
    lines = text.splitlines()
    parts: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            table_html = convert_table(table_lines)
            if table_html:
                parts.append(table_html)
            continue
        if line.strip().startswith("```"):
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(html.escape(lines[i]))
                i += 1
            if i < len(lines):
                i += 1
            parts.append(f"<pre><code>{chr(10).join(code_lines)}</code></pre>")
            continue
        if line.strip().startswith(">"):
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].lstrip("> ").strip())
                i += 1
            parts.append(f"<blockquote><p>{md_inline(' '.join(quote_lines))}</p></blockquote>")
            continue
        if re.match(r"^\s*[-*]\s+", line):
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip())
                i += 1
            parts.append("<ul>" + "".join(f"<li>{md_inline(item)}</li>" for item in items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip())
                i += 1
            parts.append("<ol>" + "".join(f"<li>{md_inline(item)}</li>" for item in items) + "</ol>")
            continue
        if line.strip():
            para_lines = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("#", "|", ">", "```", "-", "*")) and not re.match(r"^\s*\d+\.\s+", lines[i]):
                para_lines.append(lines[i].strip())
                i += 1
            parts.append(f"<p>{md_inline(' '.join(para_lines))}</p>")
            continue
        i += 1
    return "\n".join(parts)


def split_sections(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title = "概要"
    current_lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
            continue
        if line.startswith("# "):
            continue
        current_lines.append(line)
    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))
    return sections


def build_model(
    *,
    source_path: Path,
    title: str,
    document_id: str,
    review_focus: str,
) -> dict[str, Any]:
    markdown = source_path.read_text(encoding="utf-8")
    blocks: list[dict[str, Any]] = [
        {
            "id": "review-focus",
            "type": "callout",
            "title": "レビュー観点",
            "callout_title": "レビューしてほしいこと",
            "level": "info",
            "content": review_focus,
            "review_required": True,
        },
        {
            "id": "negotiation-flow",
            "type": "diagram",
            "title": "交渉の4局面と3転換点",
            "content": "交渉ダイナミクスの全体像",
            "diagram": {
                "kind": "mermaid",
                "source": (
                    "flowchart TD\n"
                    "  A[局面① 前文交渉] --> T1[転換点① 保守ブロック内部分裂]\n"
                    "  T1 --> B[局面② 実質条項の攻防]\n"
                    "  B --> T2[転換点② 先住民族論点の自己矛盾]\n"
                    "  T2 --> C[局面③ SRHR迂回表現]\n"
                    "  C --> T3[転換点③ CSW59正面衝突からCSW61迂回へ]\n"
                    "  T3 --> D[局面④ 政策空間条項の最終攻防]\n"
                    "  D --> E[コンセンサス採択]"
                ),
            },
            "review_required": True,
        },
    ]

    for index, (section_title, section_body) in enumerate(split_sections(markdown), start=1):
        body_html = convert_block(section_body)
        if not body_html:
            continue
        blocks.append(
            {
                "id": f"section-{index}-{slugify(section_title)[:40]}",
                "type": "html",
                "title": section_title,
                "heading_level": 2,
                "content": f"<h2>{html.escape(section_title)}</h2>\n{body_html}",
                "review_required": section_title in {
                    "2. 模擬国連の設計方針",
                    "3. 会議テーマの前提に埋め込まれた深層的緊張",
                    "4. 交渉ダイナミクスの設計：4局面と3つの転換点",
                    "5. 代表団設計",
                    "6. 最終成果文書の設計",
                },
            }
        )

    return {
        "schema_version": "1.0",
        "document_id": document_id,
        "title": title,
        "summary": "Claudeリサーチ成果物のレビュー用HTML。会議設計の史実根拠・交渉設計・代表団配置を確認する。",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "source": str(source_path),
            "planner": "hiyoshi-review-pipeline",
            "project": "日吉前期",
        },
        "review_settings": {"enabled": True, "mode": "standalone"},
        "blocks": blocks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--document-id", required=True)
    parser.add_argument(
        "--review-focus",
        default=(
            "史実根拠の正確性、交渉設計の実現可能性、代表団の矛盾設定、"
            "深層的緊張（発展の権利）の論理一貫性を重点的に確認してください。"
            "特に転換点①〜③の仕掛けがファシリテーター運用で機能するかも見てください。"
        ),
    )
    args = parser.parse_args()
    model = build_model(
        source_path=args.input,
        title=args.title,
        document_id=args.document_id,
        review_focus=args.review_focus,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
