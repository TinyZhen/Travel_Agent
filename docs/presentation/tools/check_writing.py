"""The owner's writing-rule check for the Roameo deck, poster and report.

Every visible word of the three deliverables and their scripts must contain
  - no em dash, en dash or other typographic dash or minus sign, no "--" (nor "---"),
  - no semicolon and no colon (each colon is reported as clock, url, ratio, label or prose),
  - no visible web address scheme such as "https://" (hyperlink targets may keep it),
  - none of the AI-sounding words and none of the mechanical words of the owner's list
    (whole words, any case), and no code identifiers or helper names such as "Intake",
  - no gendered pronoun (the authors are referred to by name).
In the deck, the poster and the scripts, test numbers such as "T16" are flagged too.

What is read
  PDFs     slides/slides.pdf and poster/poster.pdf (pdftotext, every figure label included),
           plus their Title and Subject metadata
  report   ../Roameo_Project_Report.docx, the body (tables and captions too), footnotes,
           headers, footers and the core title, without runs in a monospace font or a code
           style (command lines and file paths are code, not prose) and without hyperlink
           targets and field codes
  notes    the \\note{...} blocks of slides/slides.tex
  scripts  slides/pres-note.md, slides/stage-notes-zhen.md, poster/poster-note.md and this
           directory's README.md, without
           fenced code, inline code, Markdown link targets and table rule lines
Words inside the app's screenshots are product interface, not our writing, and are not checked.
The working documents STORY_PLAN.md, AUDIT_BEFORE.md and REVISION_PLAN.md quote old wording on
purpose. Only STORY_PLAN.md is read, and only for dashes and semicolons, as before.

Prints each hit with its place, a count per file, and exits 1 when there is any.

    python3 tools/check_writing.py            (from docs/presentation)
    python3 tools/check_writing.py --summary  (counts only)
"""

import html
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # docs/presentation
PDFS = ["slides/slides.pdf", "poster/poster.pdf"]
DOCX = ["../Roameo_Project_Report.docx"]
TEX_NOTES = ["slides/slides.tex"]
SCRIPTS = ["slides/pres-note.md", "slides/stage-notes-zhen.md", "poster/poster-note.md", "README.md"]
LEGACY = ["STORY_PLAN.md"]  # dashes and semicolons only
TALK = {"slides/slides.pdf", "poster/poster.pdf", "slides/slides.tex", "slides/pres-note.md", "slides/stage-notes-zhen.md", "poster/poster-note.md"}

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MONO = re.compile(r"consolas|courier|menlo|monaco|mono", re.I)

AI_WORDS = [
    "seamless", "seamlessly", "leverage", "leverages", "leveraged", "leveraging", "robust",
    "robustly", "robustness", "delve", "delves", "harness", "harnesses", "harnessing", "empower",
    "empowers", "empowering", "cutting-edge", "state-of-the-art", "unlock", "unlocks",
    "unlocking", "elevate", "elevates", "streamline", "streamlines", "streamlined",
    "game-changer", "game changer", "revolutionize", "revolutionizes", "revolutionise",
    "transform", "transforms", "transformative", "synergy", "holistic", "tapestry", "landscape",
    "navigate", "navigates", "navigating", "realm", "paradigm", "foster", "fosters", "unleash",
    "supercharge", "supercharged", "next-level", "pivotal", "intricate", "meticulous",
    "meticulously", "embark", "journey", "journeys", "ecosystem", "innovative", "powerful",
    "effortless", "effortlessly", "smart", "smarter", "world-class", "comprehensive",
]
MECHANICAL_WORDS = [
    "gate", "gates", "gated", "arm", "arms", "pipeline", "pipelines", "orchestration layer",
    "orchestration", "checkpoint", "checkpoints", "guardrail", "guardrails", "fallback",
    "fallbacks", "fallback path", "module", "modules",
]
# Helper names and code words that the audience should never read or hear.
JARGON = [
    "intake", "composer", "orchestrator", "critic", "state machine", "llm", "llms", "json",
    "tool calling",
]


def word_rule(words):
    alternatives = "|".join(sorted((re.escape(w).replace(r"\ ", r"\s+") for w in words), key=len, reverse=True))
    return re.compile(rf"(?<![\w-])(?:{alternatives})(?![\w-])", re.I)


DASH = re.compile(r"[\u2010-\u2015\u2043\u2212\uFE58\uFE63\uFF0D]")
RULES = [
    ("dash", DASH),
    ("double_hyphen", re.compile(r"--")),
    ("semicolon", re.compile(r";")),
    ("url_shown", re.compile(r"\b[a-z][a-z0-9+.-]*://", re.I)),
    ("pronoun", re.compile(r"\b(he|she|his|her|him|hers|himself|herself)\b", re.I)),
    ("ai_word", word_rule(AI_WORDS)),
    ("mechanical_word", word_rule(MECHANICAL_WORDS)),
    ("jargon", word_rule(JARGON)),
    ("identifier", re.compile(r"\b(?!Travel_Agent\b)[A-Za-z]+_[A-Za-z_]+\b")),
]
TALK_RULES = [("test_number", re.compile(r"\bT\d{1,2}\b"))]
LEGACY_RULES = RULES[:3]


def colon_kind(line: str, i: int) -> str:
    pre, post = line[:i], line[i + 1:]
    if re.search(r"\d{1,2}$", pre) and re.match(r"\d{2}(?!\d)", post):
        return "colon_clock"
    if post.startswith("//"):
        return "colon_url"
    if re.search(r"\d$", pre) and re.match(r"\d", post):
        return "colon_ratio"
    head = re.split(r"[.!?]\s|[|\u2022]", pre)[-1].strip()
    if not post.strip() or len(head.split()) <= 5:
        return "colon_label"
    return "colon_prose"


def hits_in(line: str, rules, colons=True):
    for name, rx in rules:
        for m in rx.finditer(line):
            if name == "pronoun" and re.search(r"\b[A-Z] ?$", line[:m.start()]):
                continue  # small capitals split by pdftotext, such as "T HE"
            yield name, m.start()
    if colons:
        for m in re.finditer(":", line):
            yield colon_kind(line, m.start()), m.start()


# Readers, each yields (place, text).
def pdf_lines(path: Path):
    text = subprocess.run(["pdftotext", str(path), "-"], check=True, capture_output=True, text=True).stdout
    for page, body in enumerate(text.split("\f"), 1):
        for n, line in enumerate(body.splitlines(), 1):
            yield f"p{page}:{n}", line
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout
    for key in ("Title", "Subject"):
        m = re.search(rf"^{key}:[ \t]*(.*)$", info, re.M)
        if m and m.group(1).strip():
            yield f"metadata {key}", m.group(1)


def markdown_lines(path: Path):
    fence = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence or re.fullmatch(r"\s*\|[ :|-]+\|\s*", line):
            continue
        line = re.sub(r"`[^`]*`", "", line)
        line = re.sub(r"\]\([^)]*\)", "]()", line)  # link targets may keep https://
        yield f"line {n}", line


def run_is_code(run, styles_mono) -> bool:
    rpr = run.find(W + "rPr")
    if rpr is None:
        return False
    fonts = rpr.find(W + "rFonts")
    if fonts is not None and any(MONO.search(v or "") for v in fonts.attrib.values()):
        return True
    style = rpr.find(W + "rStyle")
    return style is not None and (style.get(W + "val", "") in styles_mono or "code" in style.get(W + "val", "").lower())


def para_text(p, styles_mono) -> str:
    style = p.find(W + "pPr/" + W + "pStyle")
    if style is not None and (style.get(W + "val") in styles_mono or "code" in style.get(W + "val", "").lower()):
        return ""
    out = []
    for run in p.iter(W + "r"):
        if run_is_code(run, styles_mono):
            continue
        for t in run:
            if t.tag == W + "t":
                out.append(t.text or "")
            elif t.tag == W + "tab":
                out.append("\t")
    return "".join(out)


def docx_lines(path: Path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        styles_mono = set()
        if "word/styles.xml" in names:  # a style whose font is monospace counts as code
            for st in ET.fromstring(archive.read("word/styles.xml")).iter(W + "style"):
                fonts = st.find(f"{W}rPr/{W}rFonts")
                if fonts is not None and any(MONO.search(v or "") for v in fonts.attrib.values()):
                    styles_mono.add(st.get(W + "styleId"))
        parts = ["word/document.xml"] + sorted(
            n for n in names if re.fullmatch(r"word/(footnotes|endnotes|header\d*|footer\d*)\.xml", n))
        for part in parts:
            root = ET.fromstring(archive.read(part))
            heading = "(start)"
            for n, p in enumerate(root.iter(W + "p"), 1):
                style = p.find(W + "pPr/" + W + "pStyle")
                text = para_text(p, styles_mono)
                if style is not None and style.get(W + "val", "").startswith("Heading") and text.strip():
                    heading = text.strip()[:40]
                if text.strip():
                    yield f"{part.split('/')[-1]} para {n} [{heading}]", html.unescape(text)
        core = archive.read("docProps/core.xml").decode("utf-8")
        for value in re.findall(r"<dc:(?:title|subject|description)>(.*?)</dc:", core, re.S):
            yield "core.xml metadata", html.unescape(value)


def tex_note_lines(path: Path):
    src = path.read_text(encoding="utf-8")
    for m in re.finditer(r"\\note\{", src):
        i, depth, j = m.end(), 1, m.end()
        while depth and j < len(src):
            depth += {"{": 1, "}": -1}.get(src[j], 0)
            j += 1
        body = re.sub(r"(?m)(?<!\\)%.*$", "", src[i:j - 1])
        yield f"\\note at line {src[:m.start()].count(chr(10)) + 1}", re.sub(r"\s+", " ", body)


def main() -> int:
    summary = "--summary" in sys.argv
    sources = [(p, pdf_lines) for p in PDFS] + [(p, docx_lines) for p in DOCX]
    sources += [(p, tex_note_lines) for p in TEX_NOTES] + [(p, markdown_lines) for p in SCRIPTS + LEGACY]
    total = 0
    for name, reader in sources:
        path = (HERE / name).resolve()
        if not path.exists():
            print(f"missing: {name}")
            continue
        legacy = name in LEGACY
        rules = LEGACY_RULES if legacy else RULES + (TALK_RULES if name in TALK else [])
        counts = Counter()
        for place, line in reader(path):
            for kind, pos in hits_in(line, rules, colons=not legacy):
                counts[kind] += 1
                if not summary:
                    print(f"{name} {place} {kind}: ...{line[max(0, pos - 40):pos + 40].strip()}...")
        total += sum(counts.values())
        print(f"== {name}: {sum(counts.values())} hits {dict(sorted(counts.items()))}")
    print(f"{total} hits in total")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
