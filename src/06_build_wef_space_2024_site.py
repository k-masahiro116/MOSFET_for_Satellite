from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import re
from urllib.request import urlopen

from pypdf import PdfReader


PDF_URL = "https://www3.weforum.org/docs/WEF_Space_2024.pdf"
PDF_PATH = Path("data/raw/WEF_Space_2024.pdf")
HTML_PATH = Path("docs/research/pages/research/wef_space_2024_page_digest.html")
MARKDOWN_PATH = Path("docs/research/papers/wef_space_2024_page_digest.md")


@dataclass
class PageDigest:
    page: int
    heading: str
    summary: str
    excerpt: str
    words: int
    chars: int


def ensure_pdf(url: str, out_path: Path) -> None:
    if out_path.exists() and out_path.stat().st_size > 0:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=90) as response:
        out_path.write_bytes(response.read())


def normalize_text(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text: str) -> list[str]:
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def guess_heading(page_number: int, text: str) -> str:
    if not text:
        return f"Page {page_number}: (No extractable text)"
    raw_head = text[:140]
    raw_head = re.sub(r"[\n\r]+", " ", raw_head).strip(" -:;,.")
    words = raw_head.split()
    if len(words) > 16:
        raw_head = " ".join(words[:16]).rstrip(" -:;,.") + "..."
    return f"Page {page_number}: {raw_head}"


def summarize(text: str) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return "Text could not be extracted from this page."
    picked: list[str] = []
    total = 0
    for sentence in sentences:
        if len(sentence) < 40:
            continue
        if total + len(sentence) > 420 and picked:
            break
        picked.append(sentence)
        total += len(sentence)
        if len(picked) >= 3:
            break
    if not picked:
        picked = [sentences[0][:420].rstrip() + ("..." if len(sentences[0]) > 420 else "")]
    return " ".join(picked)


def build_digest(pdf_path: Path) -> list[PageDigest]:
    reader = PdfReader(str(pdf_path))
    digests: list[PageDigest] = []
    for index, page in enumerate(reader.pages, start=1):
        text = normalize_text(page.extract_text() or "")
        excerpt = text[:1100].strip()
        if len(text) > 1100:
            excerpt += " ..."
        words = len(text.split()) if text else 0
        digests.append(
            PageDigest(
                page=index,
                heading=guess_heading(index, text),
                summary=summarize(text),
                excerpt=excerpt or "(No extractable text)",
                words=words,
                chars=len(text),
            )
        )
    return digests


def write_markdown(digests: list[PageDigest], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# WEF Space 2024 - Page-by-Page Digest",
        "",
        f"- Source PDF: {PDF_URL}",
        f"- Total pages: {len(digests)}",
        "",
    ]
    for item in digests:
        lines.extend(
            [
                f"## {item.heading}",
                f"- Words: {item.words}",
                f"- Characters: {item.chars}",
                f"- Summary: {item.summary}",
                "",
                "### Excerpt",
                "",
                item.excerpt,
                "",
            ]
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_html(digests: list[PageDigest], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    toc_items = "\n".join(
        f'<li><a href="#p{item.page}">P{item.page}</a></li>' for item in digests
    )
    cards = []
    for item in digests:
        cards.append(
            f"""
    <article class="page-card" id="p{item.page}">
      <h3>{html.escape(item.heading)}</h3>
      <p class="meta">Words: {item.words} | Characters: {item.chars}</p>
      <p><strong>Summary:</strong> {html.escape(item.summary)}</p>
      <details>
        <summary>Extracted excerpt</summary>
        <pre>{html.escape(item.excerpt)}</pre>
      </details>
    </article>
""".rstrip()
        )

    document = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WEF Space 2024 Page Digest | MOSFET for Satellite</title>
  <link rel="stylesheet" href="../../styles.css">
  <style>
    .hero {{
      margin-bottom: 14px;
    }}
    .source {{
      color: #26495f;
      font-size: 0.94rem;
    }}
    .source a {{
      color: #11557e;
      text-decoration: none;
      border-bottom: 1px solid rgba(17, 85, 126, 0.35);
    }}
    .toc {{
      background: rgba(255, 255, 255, 0.9);
      border: 1px solid #d7e2ee;
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 14px;
    }}
    .toc ul {{
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 8px 0 0;
      padding: 0;
    }}
    .toc a {{
      display: inline-block;
      text-decoration: none;
      color: #0f4a68;
      background: #edf5fb;
      border: 1px solid #d2e3f2;
      border-radius: 999px;
      padding: 3px 10px;
      font-size: 0.86rem;
    }}
    .page-grid {{
      display: grid;
      gap: 12px;
    }}
    .page-card {{
      background: rgba(255, 255, 255, 0.93);
      border: 1px solid #d7e2ee;
      border-radius: 14px;
      box-shadow: 0 8px 24px rgba(10, 38, 58, 0.08);
      padding: 14px 16px;
    }}
    .page-card h3 {{
      margin: 0 0 8px;
      color: #0f3a56;
      font-size: 1rem;
    }}
    .meta {{
      margin: 0 0 8px;
      color: #4d6a7f;
      font-size: 0.85rem;
    }}
    .page-card p {{
      margin: 0 0 8px;
      color: #27485e;
      line-height: 1.7;
    }}
    details {{
      margin-top: 8px;
    }}
    summary {{
      cursor: pointer;
      color: #145b82;
      font-weight: 600;
    }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 0.79rem;
      color: #1f3f55;
      background: #f5f9fc;
      border: 1px solid #dce7f2;
      border-radius: 10px;
      padding: 10px;
      margin-top: 8px;
      max-height: 320px;
      overflow-y: auto;
    }}
  </style>
</head>
<body class="content-page">
  <main class="page-body">
    <section class="hero">
      <h2>WEF Space 2024 - ページ別ダイジェスト</h2>
      <p class="source">
        Source:
        <a href="{html.escape(PDF_URL)}" target="_blank" rel="noopener noreferrer">Space: The $1.8 Trillion Opportunity for Global Economic Growth (World Economic Forum, April 2024)</a>
      </p>
      <p>Python（pypdf）でPDFをページごとに読み取り、各ページの要約・抜粋・文字量を整理しています。</p>
    </section>

    <section class="toc" aria-label="Page index">
      <strong>Page Index ({len(digests)} pages)</strong>
      <ul>
        {toc_items}
      </ul>
    </section>

    <section class="page-grid">
      {"\n".join(cards)}
    </section>
  </main>
</body>
</html>
"""
    out_path.write_text(document, encoding="utf-8")


def main() -> None:
    ensure_pdf(PDF_URL, PDF_PATH)
    digests = build_digest(PDF_PATH)
    write_markdown(digests, MARKDOWN_PATH)
    write_html(digests, HTML_PATH)
    print(f"generated: {HTML_PATH}")
    print(f"generated: {MARKDOWN_PATH}")
    print(f"pages: {len(digests)}")


if __name__ == "__main__":
    main()
