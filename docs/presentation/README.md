# Roameo presentation materials

A seven-minute slide deck and a one-slide landscape poster with a two-minute pitch, for Roameo
by Zhen Lu and Noctis Zhang (PEAAII AI Applications Hackathon 2026, Agentic AI, October 2026).
The story, the audiences, the numbers and their sources are in STORY_PLAN.md.

## Files

| File | What it is |
|---|---|
| STORY_PLAN.md | The plan: audiences, the one message, the arc with seconds per slide, the poster layout, the figures, every number with its source file, what not to claim, and the decisions taken after three critiques |
| slides/slides.tex | The deck (beamer, the elegant theme). The title slide and ten timed slides, then two backup slides. Speaker notes are in the note blocks |
| slides/slides.pdf | The compiled deck |
| slides/pres-note.md | The spoken script with seconds per slide (407 s planned, 420 s at most) |
| slides/loadslides.tex, slides/styles/ | The elegant theme and its package list, as in the owner's template |
| slides/figures/figstyle.tex | Shared colours and TikZ and pgfplots styles for every figure |
| slides/figures/fig_persona.tex | Alex (an illustration), the $600 budget and what has to add up |
| slides/figures/fig_story.tex | The use case as a five-beat story strip with fontawesome5 icons |
| slides/figures/fig_story_v.tex | The same story, stacked, with larger type for the poster |
| slides/figures/fig_system.tex | The hero system design: AI agents, plain-code checks, the two human checkpoints, the live services and demo mode |
| slides/figures/fig_system_body.tex, fig_system_poster.tex | The picture itself, shared by the slide version and the poster version (small labels one size larger). fig_system_body.tex is an input fragment, not compiled on its own |
| slides/figures/fig_critic.tex | pgfplots chart of the critic's six reviews in one real run, against the $600 line |
| slides/figures/fig_results.tex | pgfplots chart of the test results by category, demo mode and AI mode |
| slides/figures/fig_results_poster.tex | The same chart with larger type for the poster |
| slides/figures/fig_limits.tex | Six known limits with icons |
| slides/figures/fig_deploy.tex | Try it, deploy it, go live one key at a time |
| slides/figures/fig_qr.tex | Vector QR codes to the live demo and the repository (poster header) |
| screenshots/ | Crops of docs/screenshots at native resolution, made by tools/crop_screenshots.py |
| poster/poster.tex | The poster (beamerposter with the Gemini theme), 121.92 cm by 68.58 cm, exactly 16:9 |
| poster/poster.pdf | The compiled poster |
| poster/poster-note.md | The two-minute pitch with seconds per part (113 s planned, 120 s at most) |
| poster/beamerthemegemini.sty, poster/LICENSE-gemini.md | The Gemini theme and its license |
| poster/beamercolorthemeroameo.sty | A neutral colour theme (teal on white, no rules, no institution colours). It replaces the copied university colour theme, because no affiliation is confirmed |
| tools/check_writing.py | Checks both PDFs, both scripts, this README and STORY_PLAN.md for dashes, double hyphens and semicolons |
| tools/timing.py | Counts the spoken words of a script and estimates its time at 140 words per minute |
| tools/sync_notes.py | Copies the spoken text of slides/pres-note.md into the note blocks of slides/slides.tex |
| tools/crop_screenshots.py | Makes the screenshot crops |
| .gitignore | Keeps LaTeX build files out of git (the compiled PDFs are kept) |

## Rebuild

TeX Live 2026, with `/usr/local/texlive/2026/bin/x86_64-linux` on the PATH. From this directory:

```bash
python3 tools/crop_screenshots.py
cd slides/figures
for f in fig_*.tex; do [ "$f" = fig_system_body.tex ] || latexmk -pdf -interaction=nonstopmode "$f"; done
cd ..
python3 ../tools/sync_notes.py
latexmk -pdf -interaction=nonstopmode slides.tex
cd ../poster
latexmk -pdflatex='lualatex -interaction nonstopmode' -pdf poster.tex
cd ..
python3 tools/check_writing.py
python3 tools/timing.py slides/pres-note.md
python3 tools/timing.py poster/poster-note.md
```

To see the speaker notes in the deck, uncomment the `show notes` line in slides/slides.tex.

## Where the numbers come from

Every number is from the repository. The test results are from docs/evaluation_results.md and
.json (demo mode, one run) and docs/evaluation_results_llm.md and .json (AI mode, three runs per
test). Alex's run is the app's own screenshot docs/screenshots/03_over_budget_escalation.png.
Deployment facts are from README.md, the Dockerfile, render.yaml and backend/app.py. The list,
and the places where sources disagree, are in STORY_PLAN.md, section 7.

## Credits

- Slides: the elegant beamer theme by Lars Spreng, licensed under Creative Commons Attribution
  4.0 International (CC BY 4.0), as noted in slides/loadslides.tex and slides/slides.tex.
- Poster: the Gemini beamerposter theme by Anish Athalye, MIT License, see
  poster/LICENSE-gemini.md.
- Icons: Font Awesome 5 Free through the fontawesome5 LaTeX package. QR codes: the qrcode
  LaTeX package.
- Screenshots: the Roameo app, cropped from docs/screenshots.
