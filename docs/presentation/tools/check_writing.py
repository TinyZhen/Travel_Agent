"""The owner's writing-rule check for the Roameo presentation materials.

The slide deck and the poster (pdftotext, which includes every figure label), the two spoken
scripts, this directory's README.md and STORY_PLAN.md must contain no em dash, no en dash (nor
any other typographic dash or minus sign), no "--" and no semicolon. In the Markdown files, code
blocks and inline code are skipped because they hold command lines and identifiers, not prose.
Prints each hit with its file and line, and exits 1 when there is any.

    python3 check_writing.py
"""

import html
import re
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # docs/presentation
PDFS = ["slides/slides.pdf", "poster/poster.pdf"]
DOCX: list[str] = []  # no Word document in this set
SCRIPTS = ["slides/pres-note.md", "poster/poster-note.md"]
READMES = ["README.md", "STORY_PLAN.md"]
FORBIDDEN = re.compile(r"[\u2010-\u2015\u2043\u2212\uFE58\uFE63\uFF0D]|--|;")


def pdf_text(path: Path) -> str:
    return subprocess.run(
        ["pdftotext", "-layout", str(path), "-"], check=True, capture_output=True, text=True
    ).stdout


def docx_text(path: Path) -> str:
    """The document's prose: every paragraph and the core properties, without the text in the
    two monospace code styles (paragraph style "Code", character style "Inline Code"), which hold
    command lines and identifiers rather than writing."""
    lines = []
    with zipfile.ZipFile(path) as archive:
        parts = [n for n in archive.namelist() if re.fullmatch(r"word/(document|header\d*|footer\d*)\.xml", n)]
        document = "".join(archive.read(name).decode("utf-8") for name in sorted(parts))
        for paragraph in re.findall(r"<w:p[ >].*?</w:p>", document, re.S):
            if '<w:pStyle w:val="Code"/>' in paragraph:
                continue
            runs = [
                "".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", run, re.S))
                for run in re.findall(r"<w:r[ >].*?</w:r>", paragraph, re.S)
                if '<w:rStyle w:val="InlineCode"/>' not in run
            ]
            lines.append(html.unescape("".join(runs)))
        core = archive.read("docProps/core.xml").decode("utf-8")
        lines += [html.unescape(v) for v in re.findall(r"<dc:[a-z]+>(.*?)</dc:[a-z]+>", core, re.S)]
    return "\n".join(lines)


def markdown_prose(path: Path) -> str:
    """A Markdown file without its fenced code blocks, inline code and table rule lines."""
    text = re.sub(r"^```.*?^```", "", path.read_text(encoding="utf-8"), flags=re.S | re.M)
    text = re.sub(r"^\|[ :|-]+\|$", "", text, flags=re.M)
    return re.sub(r"`[^`]*`", "", text)


def main() -> int:
    hits = 0
    checked = 0
    sources = [(p, pdf_text) for p in PDFS] + [(p, docx_text) for p in DOCX]
    sources += [(p, lambda f: f.read_text(encoding="utf-8")) for p in SCRIPTS]
    sources += [(p, markdown_prose) for p in READMES]
    for name, read in sources:
        path = HERE / name
        if not path.exists():
            print(f"missing: {name}")
            continue
        checked += 1
        for number, line in enumerate(read(path).splitlines(), 1):
            if FORBIDDEN.search(line):
                hits += 1
                print(f"{name}:{number}: {line.strip()}")
    print(f"{checked} files checked, {hits} lines with a forbidden character")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
