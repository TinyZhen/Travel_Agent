# Audit before revision

A read-only audit of the current deck (slides/slides.pdf, 13 pages), poster (poster/poster.pdf) and project report (docs/Roameo_Project_Report.docx) against every owner requirement, done on 26 October 2026 between 13.13 and 13.30 EDT. The deliverables were last built at 12.11 and committed in 905d67f. Nothing in them was changed by this audit.

How it was done. Every page was rendered with pdftoppm and the report was unzipped and extracted paragraph by paragraph with python-docx. Empty space was measured with a script (method below). Five auditors then worked in parallel, read only, one per area. A did design and AI-slide tells, B story and the Rule of Three, C the seven questions, D the truth of every number, and E the writing rules. Two requirements came in from the run coordinator during the audit (UMass Boston identity, and plain words for a first-year student). Both are checked here as R7 and R8. Each auditor's full JSON (location, problem, evidence, fix) is kept in the audit scratch folder as findings_A.json to findings_E.json, together with writing_hits.txt and a prototype extended checker, check_writing_proposed.py.

Quoted text from the deliverables is reproduced as it is, including any colons it contains.

## The twelve biggest problems, ranked

1. **No Rule of Three anywhere (R2, all three).** No deliverable names three ideas, previews them, delivers them in order and repeats them at the close. The deck is ten assertion titles and one closing message. The poster has five section heads in three columns. The report follows the seven-section template with no thesis and no conclusion. A triad already hides in the slide 4 title ("AI agents gather, plain code checks the money, you decide twice"), but it is drawn as four steps, worded differently on the poster, and absent from the report.
2. **The report tells a different story (R1, report and slide 1).** "Alex" appears 0 times in the report. Its running example is a couple going to New York on $1,500 (1.5, 4 scenes 1 and 2, T1, 5.6, and the last paragraph of 7.1). Chicago on $600 is only demo scene 3, with no persona. The deck's own title slide shows a New York plan for two at $1,650 of $1,800, seconds before Alex's $600 is introduced.
3. **Competitors are missing from the deck and the poster (R3 Q2).** No slide, backup, poster block or spoken line names a direct or indirect competitor, although report section 7 says it "supports the business-audience presentation". In the report, the chatbot row, the indirect row and every cell of the 7.1 Expedia and ChatGPT table have no reference. Some cells overreach. The report says Expedia "does not plan the days", against its own source [3], which describes Romie as "for planning, shopping and booking". It also says Roameo "prices everything from live sources", although food and transit are flat estimates (README.md line 110). And it says Roameo "hands off booking to any site", which 5.7 lists as a future improvement.
4. **No benefit to the community, and the student benefit is only a label (R1, all three).** The word "community" appears 0 times. Students appear only as an audience ("Built for students and budget travellers on short trips"). Nothing says what changes for a student or for a club, class or the public.
5. **No acknowledgement and no sources in the deck or the poster (R3 Q6, all three).** Nobody thanks the PEAAII organisers. The Elegant slide template and the Gemini poster theme (Anish Athalye, MIT) are credited only in source comments. The data services, the AI model and the main libraries have no credit. The report has a reference list but no Acknowledgements section.
6. **The report breaks the writing rule 218 times, unchecked (R5).** tools/check_writing.py has DOCX empty and never tests ":". The report has 95 semicolons (50 of them in the pasted machine output of the 5.2 results table), 10 en dashes, 2 minus signs, 6 clock times with a colon, 108 colons in all, and 3 web addresses shown with "https://". The deck has 19 colons and the poster 13, among them the poster title and both deck backup titles. The two scripts have 12 and 10.
7. **Wrong or untraceable claims in the report (R6).** It says the origin is assumed ("Assumed departing from Boston"), but the code asks every time (intake.py lines 29 and 196, test T19, README.md line 79). The numbers in 5.6 ($1,720, $220 over $1,500, $506 per person, four repairs, 8 hotels) are not in any repository file. Section 4 plans a 2.5 minute live demo that the deck does not have. It names a branch hackathon-2026 that does not exist (only main). It also contradicts itself on airport codes and on the forecast window (15 days in the code, 16 in one place).
8. **Missing UMass Boston identity and affiliation (R7, slides, poster and report title page).** The coordinator's new requirement asks for the affiliation line, the UMass Boston logos at native resolution and the UMB colours. None of the three carries any of them. The current deck and poster deliberately use a neutral teal theme with no affiliation.
9. **A full-width empty band under the title on most slides (R4, measured).** On slides 2, 3, 5, 9, 10 and 11 the strip from 13 to about 30 percent of the page height is blank across the full width (16 to 22 percent of the content area). The two backups leave their bottom fifth to third blank (slide 13 is the worst page, 32 percent). On seven slides 25 percent or less of the content area holds any ink. The cause is a \vfill above and below every frame body, with figures sized by fixed height.
10. **Unreadable screenshots, and two report images taller than the page (R4).** Screenshot text on slides 1, 6 and 7 and in the poster's centre column is about 3 to 4 pt when shown. The images are sharp, but they are cropped too wide. In the report, Figure 2 is placed 13.40 in tall and Figure 5 10.83 in tall against a 9.0 in text block, so their text prints at about 3 pt and Word pushes them onto their own pages.
11. **Jargon a first-year student will not follow (R8).** The deck and poster show "Checkpoint 1" and "Checkpoint 2", the agent names Intake and Composer, and the service names SerpApi and OpenRouter. The report uses "LLM" 31 times, the code states awaiting_approval 20 times and needs_clarification 6 times, test ids (T1 to T25) 47 times, and "pipeline", "guardrail", "fallback", "orchestrator", "state machine", "JSON" and "tool-calling". Slide 8 explains what a test is. No deliverable says plainly what "passing" means, what "three runs" are for, or what demo mode is (practice runs with sample prices) in words a first-year student would use.
12. **Responsible use of AI is never named in the deck or on the poster (R3 Q5).** The substance is there: you approve every plan, it never books or pays, code does the money and sample data is labelled. Privacy and data flow are missing everywhere. Report 6.5 says "no stored personal data" but not that the request text goes to OpenRouter, SerpApi, Google and Ticketmaster.

## Measured empty space

Method. Each page was rendered with pdftoppm (slides at 80 dpi, 630 by 410 px, poster at 40 dpi, 1920 by 1080 px). The background is the most common colour, RGB 252, 252, 252 on every page. A pixel is empty when no channel differs from the background by more than 12. The page is cut into a 100 by 100 grid and a cell is empty when every pixel in it is empty. The scripts (whitespace.py, ws_table.py) and the raw numbers (whitespace_table.json) are in the audit scratch folder, not in the repository.

Columns. **Empty cells** is the share of the whole page with no ink. **Ink in content** is the share of cells that hold ink inside the content area (slides 13 to 94 percent of the height and 3 to 97 percent of the width, poster 10 to 97 and 2 to 98, which leaves out the title line, footer and margins). **Largest empty rectangle** is the biggest blank rectangle in that content area, as a share of the content area, with its position as fractions of the page width (x) and height (y). **Bands** are horizontal tenths of the page, top to bottom, with the share of empty cells in each, where 1.00 is a fully blank strip across the page. Band 1 holds the space above the title and band 10 the footer, so they are blank on purpose.

| Page | Slide | Empty cells | Ink in content | Largest empty rectangle | Two emptiest bands | Empty share per band, top to bottom |
|---|---|---|---|---|---|---|
| slide 1 | Title | 0.75 | 0.35 | 0.14 (x 0.03 to 0.97, y 0.13 to 0.24) | band 1 (1.00) and band 2 (1.00) | 1.00 1.00 0.88 0.75 0.76 0.76 0.46 0.60 0.41 0.90 |
| slide 2 | Alex has $600 and one sentence | 0.85 | 0.22 | 0.22 (x 0.03 to 0.97, y 0.13 to 0.31) | band 1 (0.95) and band 3 (1.00) | 0.95 0.88 1.00 0.81 0.69 0.75 0.88 0.70 0.84 0.95 |
| slide 3 | One sentence becomes a checked plan | 0.76 | 0.33 | 0.20 (x 0.03 to 0.97, y 0.13 to 0.29) | band 1 (0.96) and band 3 (0.96) | 0.96 0.75 0.96 0.68 0.59 0.53 0.64 0.96 0.63 0.95 |
| slide 4 | AI agents gather, plain code checks | 0.72 | 0.41 | 0.10 (x 0.03 to 0.97, y 0.13 to 0.21) | band 1 (1.00) and band 10 (0.96) | 1.00 0.77 0.77 0.59 0.56 0.63 0.78 0.50 0.69 0.96 |
| slide 5 | The critic re-checks each repair | 0.85 | 0.20 | 0.18 (x 0.03 to 0.97, y 0.13 to 0.28) | band 1 (0.95) and band 3 (0.99) | 0.95 0.81 0.99 0.89 0.83 0.87 0.82 0.79 0.64 0.95 |
| slide 6 | Then it stops and asks Alex | 0.79 | 0.29 | 0.16 (x 0.03 to 0.97, y 0.13 to 0.26) | band 1 (0.96) and band 10 (0.95) | 0.96 0.79 0.91 0.67 0.70 0.63 0.87 0.75 0.65 0.95 |
| slide 7 | Plans bend to feedback, weather, season | 0.78 | 0.34 | 0.12 (x 0.03 to 0.97, y 0.84 to 0.94) | band 1 (1.00) and band 10 (0.96) | 1.00 0.82 0.62 0.68 0.70 0.60 0.64 0.95 0.82 0.96 |
| slide 8 | All 23 core tests pass | 0.82 | 0.25 | 0.16 (x 0.03 to 0.22, y 0.13 to 0.76) | band 1 (0.99) and band 10 (0.95) | 0.99 0.76 0.84 0.70 0.75 0.80 0.85 0.79 0.73 0.95 |
| slide 9 | What it cannot do yet | 0.85 | 0.24 | 0.20 (x 0.03 to 0.97, y 0.13 to 0.29) | band 1 (1.00) and band 3 (1.00) | 1.00 0.92 1.00 0.51 0.86 0.62 0.73 1.00 0.86 0.95 |
| slide 10 | One URL to deploy | 0.82 | 0.23 | 0.22 (x 0.03 to 0.97, y 0.13 to 0.31) | band 1 (0.99) and band 3 (1.00) | 0.99 0.80 1.00 0.64 0.70 0.58 0.95 0.79 0.84 0.96 |
| slide 11 | Alex still makes the call (close) | 0.83 | 0.23 | 0.22 (x 0.03 to 0.97, y 0.13 to 0.31) | band 3 (1.00) and band 9 (0.99) | 0.95 0.86 1.00 0.57 0.66 0.72 0.78 0.77 0.99 0.96 |
| slide 12 | Backup, critic repairs | 0.81 | 0.24 | 0.22 (x 0.03 to 0.97, y 0.76 to 0.94) | band 1 (1.00) and band 9 (1.00) | 1.00 0.84 0.91 0.66 0.95 0.52 0.55 0.76 1.00 0.96 |
| slide 13 | Backup, the 25 test conversations | 0.82 | 0.29 | 0.32 (x 0.03 to 0.97, y 0.68 to 0.94) | band 8 (1.00) and band 9 (1.00) | 0.99 0.83 0.55 0.82 0.58 0.71 0.76 1.00 1.00 0.96 |
| poster | Poster | 0.58 | 0.54 | 0.02 (x 0.26 to 0.28, y 0.33 to 0.97) | band 2 (0.73) and band 3 (0.69) | 0.61 0.73 0.69 0.49 0.60 0.55 0.56 0.50 0.45 0.61 |

Worst areas, ranked.

1. Slide 13, backup on the 25 test conversations. The bottom third is blank across the full width (y 0.68 to 0.94), 32 percent of the content area. Bands 8 and 9 are fully empty.
2. Slides 2, 10 and 11. A blank full-width strip between the title and the first content (y 0.13 to 0.31), 22 percent of the content area. Band 3 is fully empty on each. Slide 11 also has a blank band 9 under the thanks block.
3. Slide 12, backup on the critic's repairs. Blank from y 0.76 to 0.94 across the full width, 22 percent of the content area.
4. Slides 3, 5 and 9. The same strip under the title (16 to 20 percent). Slide 9 also has a fully blank band 8 between the limits grid and its closing sentence. On slide 5 the climax chart ($1,235 to $780) spans only about 52 percent of the slide width.
5. Slide 1. The top fifth is blank (bands 1 and 2 fully empty, from a \vspace{1.25cm} at slides.tex line 74). The hero screenshot is small.
6. Slide 8. A tall blank column to the left of the results chart (x 0.03 to 0.22, y 0.13 to 0.76).
7. Ink density. On slides 2, 5, 8, 9, 10, 11 and 12, 25 percent or less of the content area holds any ink. The figures and type are small, so most of each slide is background even where there is no single big hole.
8. The poster is dense. Its largest blank rectangle is the gutter between the left and centre columns (2 percent), and no band is more than 73 percent empty. Auditor A found the loosest spots at the bottom of the centre column (about 1.9 in blank under the dashed demo-mode box) and between the five steps of the left story column.

Cause. The deck is top-aligned (class option t), but almost every frame body sits between two \vfill, which centres it, and the figures are included at fixed heights (6.25 to 8.55 cm on a 13 cm slide) instead of filling the space left under the title.

## Findings per requirement

### R1. One central story on one use case, novelty, benefit to students and community

- Deck and poster share one strong case (Alex, a student, Chicago for 4 days on $600, from Boston on Nov 20, first plan $1,235, five repairs, $780, $180 over, three options), and the deck closes on it. Keep it. All the numbers match docs/screenshots/03_over_budget_escalation.png.
- The report does not use it (problem 2). The deck's title image shows a different trip (B5).
- Alex leaves the deck for slides 7 to 10, about 167 of the 407 seconds, and the $600 marker disappears there (B7). Slide 7 shows a Michigan trip and a New York guide.
- The novelty is never said in one line on a slide or on the poster (B10). The plain comparison exists only in report 7.1.
- The community benefit is missing everywhere and the student benefit is only a label (problem 4).

### R2. The Rule of Three

- There are no three named ideas, no preview, no three-idea close, and different wordings in each deliverable (problem 1, B1, B3, B9, B11 to B13). The pictures count five steps (story strip) and four steps (system figure), never three (B8).
- Auditor B's proposal, true to the repository, is one three-beat tagline, "Agents plan the trip. Code checks the money. You make the call."
  - **Agents plan the trip.** They ask before they guess. They search live flights, hotels and events. They plan around the weather and your interests.
  - **Code checks the money.** Every price comes from a tool and every total from code. The critic repairs one step at a time, up to five times. When the plan cannot fit, it says so.
  - **You make the call.** You choose how to close the gap. You change the plan in plain words. Nothing is final until you approve, and nothing is booked.
- B also mapped Alex's facts and the test categories to each idea (findings_B.json, key notes). For the report, it proposes threading the ideas through 1.1, 1.3, 1.5, the section 2 agent grouping, a three-scene section 4, and a closing 7.2 "Three ideas, one trip", without breaking the template.

### R3. The seven questions

| | Q1 problem | Q2 competitors | Q3 market | Q4 how it works | Q5 evaluation and responsible AI | Q6 sources and thanks | Q7 anything else | Students | Community |
|---|---|---|---|---|---|---|---|---|---|
| Deck and script | strong (slide 2) | **missing** | weak (one line, slides 1 and 10) | strong (slides 3 to 7) | weak (tests strong on slide 8, responsible AI never named) | weak (tool names on slide 4 only, no thanks) | weak (how to try is strong, no next steps or ask) | weak | **missing** |
| Poster and pitch | weak (problem never stated) | **missing** | weak (small line, bottom left) | strong | weak | weak (no theme credit, no references) | weak | weak | **missing** |
| Report | strong (1.3, sourced) | strong but partly unsourced (7, 7.1) | strong on who (1.4), no size | strong | strong (5, 6.5), privacy gaps | weak (no Acknowledgements) | strong (5.7, 6.2, 6.4) | weak | **missing** |

- The 7-minute script has 949 spoken words, 407 s planned against 420 s, so only 13 s are free. Slides 3 and 5 tell the same critic story ($1,235 to $780) in 87 s together, which is the obvious place to free time (C4).
- No market size appears anywhere, and none is invented. The survey figures (89 and 12 percent [2], 10, 22 and 29 percent [5] to [7]) are cited. The report calls 10 to 22 percent a range and then adds 29 percent (D12).
- Reference [4] is a vendor review that the report itself labels opinion. [6] and [7] have no date (C11).

### R4. Design and AI-slide tells

Strengths to keep. There are no \item bullets in the deck or poster and no \rule, \hline or booktabs. The Gemini headline rule and block separators are off. Both QR codes are vector. Every raster is sharp (deck 297 to 633 ppi, poster 124 to 143 ppi at print size, report 318 to 643 ppi). The palette is teal, burnt orange and green on grey, not a teal monotone.

Problems, ranked.

1. Empty bands under the titles and blank bottoms on the backups (measured above, A2, A11).
2. The slide 5 climax chart is half the slide width (A3).
3. Screenshot text is about 3 to 4 pt on slides 1, 6 and 7 and the poster centre (A4, A10). Crop to the two or three lines that carry the point and scale them up.
4. The report's Figure 2 (13.40 in) and Figure 5 (10.83 in) are taller than the 9.0 in text block (A1). Use the deck's tight crops.
5. The crops leave stray grey vertical and horizontal lines, a dot and a cut-off chat bubble, which read as decorative rules (A5).
6. The report uses decorative rules. All 10 tables have full grids (312 cell borders), and two callouts carry a thick teal vertical bar (A6).
7. The report is bullet-heavy. There are 59 list paragraphs, 24 of them in 5.4, which reads as a log (A7).
8. The report's Figure 1 has its own five-hue palette, a baked-in title and colliding labels, and calls the Composer and Critic agents while the deck calls the critic plain code (A8).
9. Slides 9, 10, 12 and 13 are bullet lists dressed as icon or number tiles (A9). The same numbered teal circles and outlined chips recur on every content slide (A13).
10. A dashed border on the demo-mode callout and a dashed rule in the results chart (A14). Faint grey \scriptsize captions (A16). Hand-typed report captions with no Caption style and no table captions (A15). Mixed British and American spelling (travellers, travelers, behaviours) (A17).
11. Caution for the next steps. The new poster/beamercolorthemeumb.sty, added by the coordinator at 13.17, turns on an orange "headline rule" and block separators. Those are the decorative lines the owner forbids. Set them to none if that theme is adopted.

### R5. Writing rules

Counts of visible hits (auditor E, verified by the prototype checker check_writing_proposed.py, 392 hits in all).

| File | Em dash | En dash | Other dash or minus | "--" | ";" | ":" | Clock with ":" | Visible https:// | Total |
|---|---|---|---|---|---|---|---|---|---|
| slides.pdf | 0 | 0 | 0 | 0 | 0 | 19 | 0 | 0 | 19 |
| pres-note.md | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 12 |
| slides.tex note blocks (not rendered) | 0 | 0 | 0 | 0 | 0 | 18 | 11 | 0 | 18 |
| poster.pdf | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 13 |
| poster-note.md | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 10 |
| Roameo_Project_Report.docx | 0 | 10 | 2 | 0 | 95 | 108 | 6 | 3 | 218 |
| README.md | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 9 |
| STORY_PLAN.md | 0 | 0 | 0 | 0 | 0 | 91 | 0 | 2 | 93 |

The colon column includes the clock times and URL schemes. The report's monospace command lines (Consolas runs) are excluded as code.

- The worst block is report 5.2, where the "Actual" column holds machine output in body font ("status=...; total=$...; revisions=N; asked: ..."), with 50 semicolons, 13 label colons and 3 clock times (E1). Either set the column as code or rewrite each cell as prose.
- Colons in titles include the poster title "Roameo: agents plan the trip, you make the call" (also the PDF title of both files), the deck backup titles "Backup: ...", and the report headings 2.6 and 5.2 and its file title (E9, E10, E12, E13).
- Report clock times 17:02, 16:44, 10:00 and 08:30 should read 17.02, 16.44, 10 am and 8.30 am (E5). The en dashes are ranges ("18–30", "Nov 2 – Dec 12") and should read "to" (E3). The minus signs are "−5°C" and a diff line "− Museum of Modern Art" (E4).
- The title page and section 3 show "https://github.com/TinyZhen/Travel_Agent" and "https://roameo-l13h.onrender.com/" (E6). The reference list already shows addresses without the scheme.
- No gendered pronouns in any deliverable. The one hit, "T HE", is pdftotext splitting small capitals (E11).
- The checker (E19). FORBIDDEN lacks ":", DOCX is empty, and visible URLs, clock times, PDF metadata, \note text and pronouns are not checked. findings_E.json (key checker_extension) and check_writing_proposed.py give the exact extension. Turn on the report (document.xml, footnotes, endnotes, headers, footers, core.xml title), exempt runs in monospace fonts by font and not only by style, exempt hyperlink targets but not display text, and classify each ":" as clock, URL, ratio, label or prose.
- Text inside the app screenshots ("Heads-up:") is product UI and is not seen by any checker. It is arguably exempt (E20).

### R6. Truth

Confirmed against the repository (23 claims). 25 tests (23 core and 2 known limits). 23 of 23 core tests pass in demo and AI mode with 51 of 51 checks, and all 23 pass in each of 3 AI runs. Known limits 1 of 2 (demo) and 2 of 2 (AI). Category counts 10, 4, 4, 4 and 1. At most 5 repairs (orchestrator.py line 34) and 8 research steps (research.py line 19). 60 requests per visitor per hour (app.py line 28). Start without keys in about 3 minutes, 7 demo cities, approval exports a calendar file and books nothing. The $300 test gives $778, $478 over. Every number in Alex's run matches 03_over_budget_escalation.png. The deck, poster and report agree on all test numbers.

Findings, ranked.

1. D1, high, report. The origin is "assumed" in 1.6 and 2.4, but the code, T19 and the README ask for it every time.
2. D2, high, report. The 5.6 live-run numbers are not backed by any file. The only New York screenshot (04_plan.png) shows $1,800, $1,650, $317 per person, 11 hotels and 1 repair.
3. D3, medium, report. Section 4 plans a 2.5 minute live demo that the deck does not have, and its scene 1 numbers differ from 04_plan.png.
4. D4, medium, report. It says any city gets its nearest airport (true, tools/__init__.py line 71), then twice that only the seven built-in cities have airport codes.
5. D5, medium, deck script and pitch. "Most tests are about asking you and taking feedback" is wrong. That group is 10 of 23 core tests, the largest group but not most.
6. D6, medium, report. "branch hackathon-2026" does not exist. Only main does.
7. D7, medium, report 7.1. Unsourced and overreaching competitor cells (problem 3).
8. D8 to D13, low. The report says "six agents" but its table has 7 rows with the Orchestrator. The forecast window is 15 days, not 16. The attractions source leaves out Google Maps via SerpApi. "Any OpenRouter model" leaves out that it must support tool calling. The market range wording is wrong. The history numbers in 5.4 (6 of 16, T5 0/3 and others) are kept in no results file.

Disagreements to record (the results files and code win).

- README.md line 94 says 18 scripted scenarios, but the results files have 25. All deliverables correctly use 25.
- README.md line 115 and eval/run_eval.py line 170 say only the 7 built-in cities have airport codes. The code finds the nearest airport for any city.
- The README says the forecast covers 16 days, the code 15, and the report says both.
- The README lists 7 agents including the Orchestrator. The report and deck say 6.
- The results files do not name the AI model. Claude Haiku 5.5 comes only from README.md, backend/llm.py line 17 and render.yaml.
- The report says the origin is assumed. The code, the README and T19 say it is always asked.
- The report's 5.6 run differs from the only New York screenshot.
- The report gives Google Places as the only attractions source. The code also uses Google Maps through SerpApi.

### R7. UMass Boston identity and affiliation (added by the run coordinator during the audit)

The coordinator's message reverses the original "no institution names or logos" line. That is recorded here, and the owner should confirm it. The requested elements are the affiliation line (Department of Computer Science, University of Massachusetts Boston), the logos at native resolution, and the UMB palette (blue #005A8B, navy #132245, the slides' primary #08457E, orange #FF791F only for tension).

| Deliverable | Now | What to change |
|---|---|---|
| Slides | No affiliation and no logo. The neutral teal palette (README.md says "no institution colours, because no affiliation is confirmed"). | Add the affiliation line under the names on slide 1 and slide 11. Place slides/logos/Blue-UMB-logo-lockup.png (6600 by 5100 px) on the title slide and Umass_boston_textlogo.png (2222 by 1132 px) small in the footer, scaled down, never up. Move figstyle.tex and the theme to UMB blue, navy and #08457E, keeping orange for the over-budget moments only. |
| Poster | No affiliation, no logo, the teal beamercolorthemeroameo.sty. | Add the affiliation to the author line. Put poster/logos/White-UMB-logo-lockup.png (2289 by 1094 px) on a navy header band beside the QR codes. Switch to beamercolorthemeumb.sty, but with its headline rule and block separators turned off (R4 item 11). |
| Report title page | "Team: Roameo" and "Members: Zhen Lu, Noctis Zhang", no affiliation. The 1.2 table lists the major as Computer Science only. | Add "Department of Computer Science, University of Massachusetts Boston" under the names on the title page, without a colon, and optionally the blue lockup at native resolution. |

The logo files were checked for presence and pixel size only. They are not yet used anywhere.

### R8. Plain words for a first-year student (added by the run coordinator during the audit)

Counted with a word list on the visible text (words.py and words.json in the audit scratch folder).

| Deliverable | AI-sounding words | Mechanical words and code identifiers |
|---|---|---|
| Deck (slides.pdf) | 0 | "Checkpoint 1" and "Checkpoint 2" (slide 4), agent names Intake and Composer, SerpApi 5, OpenRouter 2, "repo" 1 |
| Script (pres-note.md) | 0 | "checkpoint" 2, OpenRouter 2 |
| Poster | 0 | "Checkpoint 1:" and "Checkpoint 2:", Intake, Composer, SerpApi 4, OpenRouter 2 |
| Pitch (poster-note.md) | 0 | OpenRouter 1 |
| Report | "harness" 2 ("evaluation harness", 6.1 and 6.4) | LLM 31, awaiting_approval 20, needs_clarification 6, test ids T1 to T25 47, scenario(s) 15, backend 7, SerpApi 6, spec 5, parser 5, API(s) 6, checkpoints 3, fallback 3, geocoding 4, orchestrator 3, state machine 2, JSON 2, tool-calling 2, pipeline 2, assertions 2, guardrail 1, search_flights and four other tool function names in 2.3, uvicorn 1, FastAPI 2 |

Explanations a first-year student needs.

- What a test is. The deck says it once on slide 8 ("A test is a scripted conversation with checks on the result"). The poster says it in its right column. The report says "25 scripted conversations ... with explicit assertions" (5.1). Simpler wording would be "a conversation written in advance, with code that checks the answer".
- What passing means. No deliverable says it plainly ("every check in that conversation came out right").
- What "3 runs" means. The deck and pitch say AI mode "ran three times" but not why (the AI can answer differently each time, so each test was repeated three times to see whether it stays right).
- What demo mode is. The deck and poster say "No keys? Demo mode. The same steps run on rules". A first-year student needs "practice runs with sample prices, no accounts or keys needed".
- The reasons for the design choices are present for the critic ("so the arithmetic is always correct") and for asking (never guess a city or date). They are missing for six agents rather than one prompt (only report 2.6 and a small poster line), for stopping after five repairs, and for never booking.

## Ranked list per deliverable

### Slides and script

1. No three ideas, no preview, no three-idea close (R2).
2. No competitors, no acknowledgement, no community benefit, responsible AI never named (R3, R1).
3. Missing UMass Boston identity (R7).
4. A blank strip under the title on most slides, blank backup bottoms, and a half-width climax chart (R4, measured).
5. Unreadable screenshot text on slides 1, 6 and 7, and a title screenshot of a different trip (R4, R1).
6. 19 visible colons (both backup titles, figure labels like "Checkpoint 1:"), 12 in the script, 18 in the unrendered note blocks, and the PDF title (R5).
7. "Most tests are about asking you" is wrong (10 of 23) (R6).
8. Jargon (Checkpoint 1/2, Intake, Composer, SerpApi, OpenRouter), and "passing", "3 runs" and demo mode are not explained (R8).
9. Only 13 s of slack. Slides 3 and 5 repeat the critic story, and Alex vanishes on slides 7 to 10 (R1, R3).
10. Icon-tile lists on slides 9, 10, 12 and 13, repeated teal circles and chips, and faint captions (R4).

### Poster and pitch

1. No three ideas. The three columns are not the ideas, there are five heads, and there is no closing band (R2).
2. No competitors, no problem statement, no community benefit, no acknowledgement or theme credit (R3, R1).
3. Missing UMass Boston identity, and the new UMB colour theme has decorative rules switched on (R7, R4).
4. 13 visible colons, including the title, "Your call:", "Checkpoint 1:", "Limits:" and "No keys:", and 10 in the pitch (R5).
5. The centre column screenshots are unreadable at poster distance (R4).
6. "Most tests ..." in the pitch is wrong, and "any OpenRouter model" leaves out tool calling (R6).
7. Jargon and missing explanations as in the deck (R8).
8. Space is well used (largest blank 2 percent). Only the bottom of the centre column and the gaps in the left story column are loose (R4).

### Report

1. Not Alex's story. New York on $1,500 runs through 1.5, 4, 5.6 and 7.1, and there is no conclusion (R1, R2).
2. 218 writing-rule hits, none seen by the checker (R5).
3. Untrue or untraceable claims. The origin is said to be assumed, the 5.6 numbers have no source, the demo plan does not match the deck, the branch does not exist, and the airport and forecast statements contradict each other (R6).
4. The 7 and 7.1 competitor table is partly unsourced and overreaching (R3, R6).
5. No Acknowledgements section, no community benefit, privacy and data flow missing from 6.5 (R3, R1).
6. No UMass Boston affiliation on the title page (R7).
7. Figures 2 and 5 are taller than the page, Figure 1 does not match the deck, all tables have full grids, and two callouts have teal bars (R4).
8. 59 bullets, 24 of them in 5.4 (R4).
9. Heavy jargon. LLM 31 times, code states 26 times, test ids 47 times, "pipeline", "guardrail", "harness" (R8).
10. Captions typed by hand, no table captions, mixed spelling (R4).

## What the auditors confirmed is already right

- One persona and one set of numbers across the deck and the poster, all traceable to one real run.
- All test numbers are identical in the three deliverables and match the results files.
- No invented market figures. Survey figures are cited.
- No em dashes, en dashes, "--" or semicolons in the deck, poster, scripts, README or STORY_PLAN.
- No \item bullets, no LaTeX rules, vector QR codes, and every raster sharp.
- No gendered pronouns anywhere.
- Strong, honest evaluation (report 5.4 failure cases, the "small, honest check, not a user study" line on the poster).
