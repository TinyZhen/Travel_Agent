"""Copy the spoken text of slides/pres-note.md into the \\note{...} blocks of slides/slides.tex.

Each timed slide's note becomes "(Ns, ends m:ss) <spoken text>", in slide order. Backup slides
(after \\appendix) keep their notes.

    python3 tools/sync_notes.py      (from docs/presentation)
"""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def main() -> None:
    script = (HERE / "slides/pres-note.md").read_text(encoding="utf-8")
    parts = re.split(r"^## ", script, flags=re.M)[1:]
    notes, elapsed = [], 0
    for part in parts:
        _, _, body = part.partition("\n")
        seconds = int(re.search(r"^_about (\d+) seconds_", body, re.M).group(1))
        elapsed += seconds
        spoken = " ".join(
            line.strip() for line in body.splitlines()
            if line.strip() and not line.lstrip().startswith((">", "_", "#"))
        )
        spoken = spoken.replace("$", "\\$").replace("%", "\\%")
        notes.append(f"\\textbf{{({seconds}s, ends {elapsed // 60}:{elapsed % 60:02d})}} {spoken}")
    tex_path = HERE / "slides/slides.tex"
    tex = tex_path.read_text(encoding="utf-8")
    main_part, sep, backup = tex.partition("\\appendix")
    blocks = list(re.finditer(r"\\note\{\n(.*?)\n  \}", main_part, re.S))
    assert len(blocks) == len(notes), (len(blocks), len(notes))
    out, last = [], 0
    for block, note in zip(blocks, notes):
        out.append(main_part[last:block.start()])
        wrapped = re.sub(r"(.{1,92})(\s+|$)", r"    \1\n", note).rstrip("\n")
        out.append("\\note{\n" + wrapped + "\n  }")
        last = block.end()
    out.append(main_part[last:])
    tex_path.write_text("".join(out) + sep + backup, encoding="utf-8")
    print(f"{len(notes)} notes written, {elapsed} s in total")


if __name__ == "__main__":
    main()
