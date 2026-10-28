# Roameo presentation materials

The seven minute slide deck, the one slide poster with its two minute pitch, and the builder of the project report, for Roameo by Zhen Lu and Noctis Zhang, Department of Computer Science, University of Massachusetts Boston, and Zhen Luo, Department of Industrial Engineering, Northeastern University. PEAAII AI Applications Hackathon 2026, Agentic AI, October 2026.

All three tell one story. Alex, a student we made up, types "Chicago for 4 days, budget $600" into one real live run of the app. Three ideas carry the story, each in three parts.

1. **AI agents do the legwork.** They ask for what is missing, choose the searches, and turn plain words into changes.
2. **Code checks the money.** It adds up every total, tries one fix at a time (at most five), and shows the gap.
3. **You make the call.** You choose how to close the gap, you see every step, and nothing is final until you say OK. Roameo never books or pays.

The deck announces the ideas on slide 3, delivers them on slides 4 to 6 and repeats them on slide 11. The poster has one column per idea. The report opens with them on its one page summary and closes with them in section 8. The brief behind all of this is `REVISION_PLAN.md`, and the findings it answers are in `AUDIT_BEFORE.md`.

## Files

| File | What it is |
|---|---|
| `REVISION_PLAN.md` | The brief. Core story, the three ideas, words and colour rules, where each of the seven questions is answered, the deck slide by slide, the poster bands, the report sections, every number with its source, and what not to claim |
| `AUDIT_BEFORE.md` | The audit of the earlier deck, poster and report, with the measured empty space |
| `STORY_PLAN.md` | The earlier plan, kept for its history. It is replaced by `REVISION_PLAN.md` |
| `slides/slides.tex` | The deck, Beamer with the Elegant template. Eleven timed slides and six backup slides. Speaker notes sit in the note blocks |
| `slides/slides.pdf` | The compiled deck, 17 pages |
| `slides/pres-note.md` | The spoken script, one part per slide with its seconds. The notes in the deck are copied from it |
| `slides/loadslides.tex`, `slides/styles/` | The Elegant template and its package list |
| `slides/logos/` | The UMass Boston lockup in blue and the word mark, used at their own resolution and only scaled down |
| `slides/figures/figstyle.tex` | The shared palette, the three idea marks and the TikZ and pgfplots styles of every figure in the deck, the poster and the report |
| `slides/figures/fig_ideas.tex` | The three ideas, each with its three parts and one fact from Alex's run (slide 3, report summary) |
| `slides/figures/fig_ideas_close.tex` | The three ideas again, filled with what happened to Alex (slide 11) |
| `slides/figures/fig_price.tex` | The plan total after each of the five fixes in Alex's run, against the $600 budget (slide 5, report section 4) |
| `slides/figures/fig_results.tex` | The tests by group, each with the mark of its idea, and the two known limits (slide 7, report 5.1) |
| `slides/figures/fig_dataflow.tex` | What goes where when you use Roameo (slide 8, report 6.5) |
| `slides/figures/fig_workflow.tex` | The six helpers and the coordinator in three bands, AI or plain code (backup slide, report 2.1) |
| `screenshots/` | Crops of `docs/screenshots` at their own pixels, never scaled up, made by `tools/crop_screenshots.py`. The files that start with alex come from Alex's run |
| `poster/poster.tex` | The poster, beamerposter with the Gemini theme and the UMass Boston colour theme, 48 by 27 inches |
| `poster/poster.pdf` | The compiled poster |
| `poster/poster-note.md` | The pitch, at most 120 seconds, with a 30 second short version |
| `poster/figures/` | The poster versions of the figures, with larger type (`fig_strip`, `fig_price_poster`, `fig_dataflow_poster`) |
| `poster/logos/` | The white UMass Boston lockup for the navy header |
| `poster/beamercolorthemeumb.sty` | The UMass Boston colours. The poster turns off its headline rule and block separators, because decorative lines are not wanted |
| `poster/beamerthemegemini.sty`, `poster/LICENSE-gemini.md` | The Gemini theme and its licence |
| `poster/beamercolorthemeroameo.sty` | The earlier neutral colour theme, no longer used |
| `report/build_report.py` | Builds `docs/Roameo_Project_Report.docx` from the team's original file, which it opens as the template |
| `report/report_text.py` | The report's text, kept apart so it can be read, checked and compared |
| `report/figures/` | The report's images. The team's five images, crops of the app's screenshots, and the vector figures above rendered at 300 dpi |
| `tools/check_writing.py` | The writing check, described below |
| `tools/timing.py` | Counts the spoken words of a script and estimates its time at 140 words a minute |
| `tools/sync_notes.py` | Copies the spoken text of the script into the deck's note blocks |
| `tools/crop_screenshots.py` | Makes the screenshot crops |

The team's report as it was before this revision is kept unchanged as `docs/Roameo_Project_Report.original.docx`.

## Rebuild

TeX Live 2026 with `/usr/local/texlive/2026/bin/x86_64-linux` on the PATH, and `uv` for the report. From this folder

```bash
export PATH=/usr/local/texlive/2026/bin/x86_64-linux:$PATH
python3 tools/crop_screenshots.py
(cd slides/figures && for f in fig_*.tex; do pdflatex -interaction=nonstopmode "$f"; done)
(cd poster/figures && for f in fig_*.tex; do pdflatex -interaction=nonstopmode "$f"; done)
python3 tools/sync_notes.py
(cd slides && latexmk -pdf -interaction=nonstopmode slides.tex)
(cd poster && latexmk -pdflatex='lualatex -interaction nonstopmode' -pdf poster.tex)
(cd ../.. && uv run --no-project --with python-docx==1.1.2 python -I docs/presentation/report/build_report.py)
python3 tools/check_writing.py
python3 tools/timing.py slides/pres-note.md
python3 tools/timing.py poster/poster-note.md
```

To see the speaker notes in the deck, uncomment the line with `show notes` in `slides/slides.tex`. The report builder renders the vector figures again whenever a figure PDF is newer than its picture.

## The writing check

`tools/check_writing.py` reads the text of both PDFs and their title, the deck's note blocks, both scripts, this README and the report (body, tables, captions, footnotes, headers, footers and title). It flags dashes, double hyphens, semicolons, every colon (sorted into clock, address, ratio, label and prose), a visible "https" scheme, the AI sounding words and the mechanical words of the owner's list, helper names and code words, code identifiers with underscores, test numbers in the deck and the poster, and gendered pronouns. Monospace text in the report (command lines and file names) and words inside the app's screenshots are not checked. `AUDIT_BEFORE.md` and `REVISION_PLAN.md` quote old wording on purpose and are not read. `STORY_PLAN.md` is read for dashes and semicolons only, as before.

## Where the numbers come from

Every number comes from the repository or from the report's cited sources. Test results are from `docs/evaluation_results.md` and `.json` (demo mode, one run) and `docs/evaluation_results_llm.md` and `.json` (with the AI, three runs). Alex's run is the app's own screenshot `docs/screenshots/03_over_budget_escalation.png`. Facts about running and sharing the app are from the main README, `backend/app.py`, `backend/llm.py` and `render.yaml`. The full list is in `REVISION_PLAN.md`, section 9.

Where sources disagree, the results files and the code win. These disagreements are recorded here and in report section 5.5.

- The main README says 18 test scenarios. The results files have 25, of which 23 are core tests and 2 are known limits.
- The main README says 7 demo cities. The sample data has 8, Detroit included.
- The main README says 16 forecast days. The code uses 15, then past years' weather.
- The main README lists 7 agents. The truthful count is 6 helpers and a coordinator, which is plain code.
- The main README says live airport codes exist only for the built in cities. The code finds the nearest airport for any city, so the written expectation of the Paris test is out of date too.
- The results files do not name the AI model. Claude Haiku 5.5 through OpenRouter comes from `backend/llm.py`, `render.yaml` and the main README.
- The team's first report said the starting city is assumed. The code always asks when it is missing.
- The team's first report gave New York live run numbers that are in no repository file. They are gone.
- A typed reply that starts with words such as "approve" or "looks good" counts as approval in both modes (`backend/agents/feedback.py`, line 40), and with the AI on the AI can also read a reply as approval. The calendar file still downloads only after approval.
- The repository has no licence file, so the deck, the poster and the report say the code is public on GitHub, not that anyone may copy it.

## Checks at the last build

Run on 26 October 2026 with the commands above.

- The writing check finds 0 hits in all eight files it reads.
- The deck has 17 pages and 0 Overfull boxes, the poster 1 page and 0 Overfull boxes, and every figure builds with 0 errors and 0 Overfull boxes.
- The script runs about 383 seconds at 140 words a minute (384 planned, 420 at most). The poster pitch runs about 113 seconds (120 at most).
- Empty space, measured with the audit's method (the largest empty rectangle as a share of the content area). Before the revision the slides ranged from 0.10 to 0.32 and the poster was 0.02. Now every slide is at 0.084 or less, and the poster is 0.013. The 0.084 on the weather backup is white space inside a screenshot.
- The team's original report is unchanged, with sha256 0d9d2572 at the start.

## UMass Boston identity

The owner asked for the UMass Boston look. The affiliation line "Department of Computer Science, University of Massachusetts Boston" sits under the names on the title slide, in the poster header and on the report's title page. The logos are used at their own resolution and only scaled down. The palette is near black type on white, UMB blue #005A8B for structure, the slides' primary #08457E for titles, dark navy #132245 only for the poster header, UMB orange #FF791F only for the $180 gap, and green #2E7D32 only for a passed test or an approved plan. Roameo's teal appears only inside screenshots. This reverses the earlier rule of no institution names or logos, so the owner should confirm it. The logos show the authors' affiliation and do not mean the university endorses Roameo.

## Team actions before the event

These cannot be done by the build and are also listed in the poster pitch.

1. Record a 30 to 40 second screen capture of a live run of Alex's sentence, as a backup at the poster table. It needs the team's own keys.
2. Open the free live demo a minute before judging so it is awake.
3. Scan both QR codes with a phone. If an access code is set on the live demo, give it at the stand.
4. Bring a laptop that shows the app at the poster.

## Credits

- Thanks to the organizers of the PEAAII AI Applications Hackathon 2026.
- Slides use the Elegant Beamer template by Lars Spreng, CC BY 4.0, as noted in `slides/loadslides.tex` and `slides/slides.tex`.
- The poster uses the Gemini beamerposter theme by Anish Athalye, MIT License, see `poster/LICENSE-gemini.md`.
- Logos of the University of Massachusetts Boston, for the authors' affiliation only.
- Icons from Font Awesome 5 Free through the fontawesome5 package. QR codes from the qrcode package. Fonts are TeX Gyre Heros and Helvetica clones from TeX Live.
- Data in the app comes from Google Flights, Google Hotels, Google Events and Google Maps through SerpApi, Ticketmaster Discovery, Open-Meteo and OpenStreetMap. The AI model is Claude Haiku 5.5 by Anthropic, through OpenRouter.
- Screenshots are of the Roameo app, cropped from `docs/screenshots`.
