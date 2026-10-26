# Roameo presentation: story plan

Authors: Zhen Lu and Noctis Zhang. Event: PEAAII AI Applications Hackathon 2026, Agentic AI. October 2026.
Repository: https://github.com/TinyZhen/Travel_Agent. Live demo: https://roameo-l13h.onrender.com/

Items: a 7-minute slide deck (slides/slides.tex, script slides/pres-note.md) and a one-slide landscape
poster with a 2-minute spoken pitch (poster/poster.tex, script poster/poster-note.md).

Status: version 3. Version 2 was revised after three critiques (section 9 records what changed
and why). Version 3 records the final build (section 10).

## 1. Audiences

Assumed: a hackathon room of judges and visitors (the project report's title page names the PEAAII AI
Applications Hackathon 2026, Agentic AI track). Three listeners in that room:

- A **visitor** with no AI background. Needs: what it is, who it is for, one picture of it working.
- A **judge**. Needs: a real problem, a working prototype, honest evaluation, ease of deployment, why
  agents (not one prompt).
- An **agents and LLM expert**. Needs: which parts are LLM and which are code, what the tool loop and
  the critic loop do, what the tests check, and what was not tested.

## 2. The one message

**Roameo's agents do the research and the arithmetic of a budget trip, and when the money does not
work out they stop and ask you, instead of quietly going over.**

Tagline from the README: "agents plan the trip, you make the call".

## 3. The persona and the ticking constraint

- **Alex**, a fictional student (labelled "illustration" on screen), has **$600** for a long weekend
  in Chicago. Alex is referred to by name only.
- Alex's words and every number in the story come from one real run of the app, captured in
  docs/screenshots/03_over_budget_escalation.png (live data, LLM agents badge):
  request "Chicago for 4 days, budget $600", the agents ask "Where are you leaving from?" and "What
  date do you want to leave?", Alex answers "From Boston, leaving Nov 20", Research finds 8 flights,
  18 hotels and 59 events, the critic reviews $1,235, then $984, $984, $1,014, $780, $780, and the
  orchestrator asks: "The cheapest plan I can build is $780, $180 over your $600 budget. Would you
  like to raise the budget, shorten to 2 nights, or drive instead of flying?"
- **Ticking constraint**: the $600 budget. It appears as a small budget marker (wallet icon and
  amount) in the top right corner of the story slides: "$600 budget", "first plan $1,235",
  "cheapest $780", "your call". It returns in the closing callback.
- **Resolution, kept honest**: the app's repository does not record what happens after Alex
  chooses in this run, so the deck does not invent a final price. The resolution is the decision
  itself: Alex sees the gap, picks one of three options, the critic re-checks, and nothing is
  final until Alex approves (approval only exports a calendar file, nothing is booked). The tested
  path "raise the budget after the warning" is cited from the evaluation, without a price.

## 4. Arc and timings (aim 395 s, limit 420 s, about 140 spoken words per minute)

| # | Seconds | Assertion title | Evidence and figure |
|---|---|---|---|
| 1 | 13 | Roameo: agents plan the trip, you make the call | Title, one plain line, for students and budget travellers, authors, event, QR codes to the live demo and the repository, a crop of a plan in the app |
| 2 | 31 | Alex has $600 and one sentence | Persona figure (Alex as an illustration, the $600, what has to add up) beside a crop of the app's start screen, whose own example is Alex's sentence. Footnote with the 89% and 12% survey line |
| 3 | 43 | One sentence becomes a checked plan, and Alex keeps the final say | Story strip: the request, the two questions, the research, the critic, Alex's three choices. Plain definitions of agent and critic |
| 4 | 60 | AI agents gather, plain code checks the money, you decide twice | Hero system figure |
| 5 | 44 | The critic re-checks each repair, and stops after five | pgfplots chart of the six reviews of Alex's run against the $600 line, labelled with each repair. The tested $300 case ($778, $478 over) in the support line |
| 6 | 36 | Then it stops and asks Alex, instead of quietly going over | Crops of the red budget bar and of the question with its buttons, then Alex's three options and what approval does |
| 7 | 44 | Plans bend to feedback, weather and the season | Feedback chips, crops of the Michigan in December chat and of a visit guide |
| 8 | 54 | All 23 core tests pass in both modes, and in each of three AI runs | pgfplots bar chart by category, what a test is, who wrote them, sample prices, demo mode is deterministic |
| 9 | 31 | What it cannot do yet | Six limits with icons, what the tests do not judge |
| 10 | 38 | One URL to deploy, three minutes to try without keys | Deployment figure, who it is built for, the free plan's sleep |
| 11 | 13 | Alex still makes the call on the $600 | Callback: the one message, the three options, QR codes, thank you |
| | **407** | | Two backup slides after the end (not timed): the critic's repair order, what the 25 tests check |

The script (slides/pres-note.md) is 950 words, 407 s at 140 words per minute (928 words and 398 s before the audit, see section 11). Backup slides are not timed.

## 5. Poster layout (landscape 16:9, 121.92 cm by 68.58 cm, read from two metres)

Final layout (built):
- Header: title "Roameo: agents plan the trip, you make the call", one plain line ("An AI trip
  planner that does the research and the math, and asks before it goes over your budget"), the
  authors, the event and the date. Two QR codes at the right, labelled "Try it" and "Code". No
  logos and no institution.
- Left column: "Alex has $600 and one sentence", the story in its stacked poster variant, the
  provenance line (one real run, Alex is an illustration) and who it is for.
- Centre column: "Over budget? It stops and asks you" with the two escalation crops and "Your
  call" with the three options, then the hero system figure, then one line on why agents and not
  one prompt.
- Right column: "All 23 core tests pass in both modes" with the results chart (poster variant)
  and what a test is, then "Try it, deploy it" with the limits.
- The critic chart is on the slides only. The story already carries $1,235 to $780 after five
  repairs, and the visitor critique asked for a less dense poster.
- Type at poster scale (measured from the scale factors): the hero figure's smallest labels
  about 24 pt and its boxes about 24 pt, the story about 24 pt and more, the results chart about
  28 pt, body text larger.

The 2-minute pitch (poster/poster-note.md) is 262 words, 112 s estimated, 113 s planned (258 words, 111 s and 116 s before the audit).

## 6. Figures

| File | What | Used in |
|---|---|---|
| slides/figures/figstyle.tex | Shared colours and TikZ and pgfplots styles | all figures |
| slides/figures/fig_persona.tex | Alex, the $600, what has to add up | slide 2 |
| slides/figures/fig_story.tex | Story strip (horizontal) | slide 3 |
| slides/figures/fig_story_v.tex | Story strip (stacked poster variant, larger type) | poster |
| slides/figures/fig_system.tex | Hero system design (the picture is in fig_system_body.tex) | slide 4 |
| slides/figures/fig_system_poster.tex | Same picture, small labels one size larger | poster |
| slides/figures/fig_critic.tex | Critic reviews chart (pgfplots) | slide 5 |
| slides/figures/fig_results.tex | Test results chart (pgfplots) | slide 8 |
| slides/figures/fig_results_poster.tex | Same, larger type | poster |
| slides/figures/fig_limits.tex | Six limits with icons | slide 9 |
| slides/figures/fig_deploy.tex | Try it, deploy it, go live one key at a time | slide 10 |
| slides/figures/fig_qr.tex | QR codes for the poster header | poster |
| screenshots/*.png | Seven crops of docs/screenshots at native resolution (tools/crop_screenshots.py, no scaling) | slides 1, 2, 6, 7, poster |

## 7. Numbers and their sources

| Number | Source |
|---|---|
| 25 scripted scenarios: 23 core and 2 known-limitation cases | docs/evaluation_results.json and _llm.json (25 results, `known_limitation` flag) |
| Demo mode: 23 of 23 core scenarios pass, 51 of 51 checks | docs/evaluation_results.md and .json |
| LLM mode: 23 of 23 core pass, 51 of 51 checks, 3 runs per case, all 23 core cases pass in 3 of 3 runs | docs/evaluation_results_llm.md and .json (`runs: 3`, `consistency` 1.0) |
| Known limitations: demo 1 of 2 behaved ideally, LLM 2 of 2 (3 of 3 runs each) | same files |
| Core scenarios by category: 10 human in the loop, 4 failure handling, 4 real-world adaptation, 4 functional (one of them end to end), 1 safety and oversight | same files, `category` |
| LLM used for the LLM runs: Claude Haiku 5.5 through OpenRouter | README.md (link text), project report 5.1, render.yaml default `LLM_MODEL` |
| Tools used sample data in both evaluation modes | project report 5.1. Most totals are identical in both results files. Two differ (local day trip $138 and $183, more museums $1,049 and $1,036) because the agents' choices differ |
| Critic: at most 5 repairs per plan, in a fixed order | backend/agents/orchestrator.py `MAX_REPAIRS = 5`, backend/agents/critic.py `next_repair` |
| Research: tool-calling loop of at most 8 steps plus a guardrail | backend/agents/research.py `MAX_STEPS = 8`, `required_tools` |
| Tested escalation: $300 budget, cheapest plan $778, $478 over, 5 revisions | docs/evaluation_results.md and _llm.md, infeasible budget case |
| Alex's run: $600, $1,235, $984, $984, $1,014, $780, $780, $180 over, 8 flights, 18 hotels, 59 events, Nov 20, 3 nights | docs/screenshots/03_over_budget_escalation.png (agent trace and chat) |
| Rate limit 60 requests per visitor per hour by default, access code | backend/app.py, render.yaml, README.md |
| About 3 minutes keyless local start | README.md |
| Free Render plan sleeps after 15 minutes idle | README.md |
| About 3 SerpApi searches per plan, roughly 80 plans a month on the free plan | README.md |
| Demo data covers 7 cities | README.md |
| 89% want AI in trip planning, 12% comfortable with AI deciding alone | project report 1.3, citing Booking.com Global AI Sentiment Report 2025 |

Sources that disagree, and the choice made:
- README says "18 scripted scenarios". The results files report 25 (23 core and 2 known limitation).
  The deck uses the results files.
- README says weather forecasts are used up to 16 days ahead, the code comment says 15 days. The deck
  gives no number.
- README says live mode knows airport codes only for the 7 built-in cities. The report (5.4) says any
  city now gets its nearest airport, and the code has a nearest-airport lookup. The deck makes no
  claim either way.
- The results files do not name the model. The README and the report name Claude Haiku 5.5.

## 8. What not to claim

- No booking or payment, ever (the app exports a calendar file after approval only).
- Not "always within budget": the point is that it says so when it cannot.
- Not "works for any city": demo data covers 7 cities.
- Not a user study: there was none. The scenarios were written by the team.
- Not "LLM is reliable": 3 runs per case is a small sample, and demo mode's 100% consistency is
  expected because it is deterministic.
- No live price accuracy claims: the evaluation used sample data. Alex's run used live data once.
- No final price for Alex after the choice: the repository does not record one.
- No affiliation, institution or logo.

## 9. Critiques and decisions

Three critique agents read version 1 of this plan in parallel: a non-technical visitor, a
hackathon judge and an agents and LLM expert (the expert and the judge also read the code and
results files). Decisions:

| Critique | Decision |
|---|---|
| Visitor: after 30 seconds I would not know what it is or who it is for | Title slide gets one plain line and "for students and budget travellers" |
| Visitor: jargon (agent, critic, orchestrator, LLM, demo mode, scenario) | Each term is explained in plain words the first time it is spoken: agent "an AI helper with one job", critic "a checker that adds up the cost", language model "the AI that reads and writes text", demo mode "runs without any accounts or keys", scenario "a scripted test conversation". "Orchestrator" becomes "the coordinator" |
| Visitor: the ending without a final price feels like a cliffhanger | Kept honest (no invented price). The escalation slide shows the three choices as buttons and says what happens next: the plan is rebuilt, checked again, and waits for Alex's approval. The closing callback returns to the $600 |
| Visitor and judge: the 89% and 12% statistic is a weak opener | Moved to a small footnote on slide 2. The deck opens on the $600 sentence |
| Visitor and judge: two slides for "it asks" (questions and escalation) | Merged: the questions live in the story strip, the separate questions slide is dropped. The escalation slide gets the large crop |
| Visitor: the one picture I want is the red budget bar | Large crop on slide 6 and in the poster centre |
| Visitor: poster too dense from two metres | The poster leads with the title, one plain line, the large escalation crop and QR codes. Other figures are secondary |
| Judge: no "why agents and not one prompt" | One line on slide 4 and in the script: one chat reply adds the prices itself and is never checked. Here the steps depend on live results, the total is re-computed after every change, and the code checks it |
| Judge: the critic chart is one live run, the reproducible test is the $300 case | Chart labelled "one live run". The tested $300 case ($778, $478 over) is cited on the same slide |
| Judge: headline "$600 was still out of reach" reads as a failure | Title reframed as intended behaviour: the critic checks every repair and stops after five, then asks |
| Judge and expert: "six agents" while composer and critic are plain code | The hero figure separates language-model agents from deterministic code, and the deck says "AI agents and plain code", not a count |
| Judge: "identical totals" is false | Fixed in section 7 (two totals differ) |
| Judge: README still says 18 scenarios | The README is outside this task's scope and is not changed. The disagreement is reported |
| Judge: say what pass means, sample data, deterministic demo mode, small sample | Results slide and script say: a scenario is a scripted conversation, pass means every check on the final state holds (51 checks), the team wrote them, tools used sample data, demo mode is deterministic so its consistency is expected, 3 LLM runs is a small sample |
| Judge: deployment friction (access code, sleep after 15 minutes) | Slide 10 and its script say the free plan sleeps after 15 minutes idle and needs a minute to wake, and that the access code and the rate limit protect the paid search quota |
| Judge: live-demo fallback | Not built here (no networked calls allowed). Flagged in the report: record a short screen capture before the event |
| Expert: which parts use the language model | Intake (reading the request), research (choosing tool calls, at most 8 steps, then a guardrail re-runs any required tool that was skipped), feedback (reading change requests), guide (visit guides) and the plan summary. Composer, critic and coordinator are code. Every language-model step has a rule-based fallback |
| Expert: second checkpoint is review, escalate, approve | Hero figure labels it that way. Escalation covers over budget, no flight, no hotel, light days and cold weather |
| Expert: the run stopped at the five-repair limit, so "cheapest" may not be the true floor | Chart caption says "stopped at the limit of five repairs". The script says the cheapest plan it built, not the cheapest possible |
| Expert: the $984 to $1,014 step | Described as: each repair rebuilds the plan, so one step went up. No cause is claimed |
| Expert: keyless is not offline (weather and city lookup use Open-Meteo, which needs no key) | Hero figure marks Open-Meteo as "no key needed". Demo mode means no keys, not no network |
| Expert: consistency means the fraction of 3 runs that passed, not identical plans | Results slide says "passed in each of three runs" |
| Expert: the evaluation does not test plan quality, live prices, visit guides, the calendar export, speed or real users | Said on the limits slide and in the script, briefly |
| Expert: a language-model failure falls back to rules silently, so some LLM-mode passes may use the rule path | Recorded here and in the backup slide note. Not claimed either way on the main slides |

## 10. Final build and checks

- Colours: near-black type on white, the app's teal (#0F766E) as the brand, one warm accent
  (#C2410C) only for the budget gap, green (#4D7C0F) only for approval and passed tests.
- The critic slide shows the chart only. A crop of the app's agent log was tried beside it, but
  its text was too small to read at slide size, so the caption names the log as the source.
- Commands in the deployment figure were replaced by plain words, because file names are
  mechanical ids.
- Checks: tools/check_writing.py reports 0 hits. Both PDFs build with 0 overfull boxes. Every
  slide and the poster were rendered to PNG and inspected.

## 11. Audit, 26 October 2026

Four auditors read the rebuilt deck and poster in parallel (design against the owner's ICML
figures, storytelling for a visitor and a judge, accuracy against the repository, writing rules
and timing). Each finding was checked against the renders, the code and the results files
before anything changed.

Fixed:

- Demo mode has no visit guides (backend/agents/guide.py needs the language model, README marks
  the guide "Not available" in demo mode). The hero figure, the deploy figure and the slide 4
  script now say the same steps run on rules, all but the visit guides. Slide 7's script says
  the guides come with the AI on.
- The weather in Alex's run was typical for those dates (2023 to 2025), not a forecast
  (screenshot 03). The story strip now says "rain and cold likely" (the app's own words), the
  poster and the script say typical for those dates.
- Sights in Alex's run came from the curated list and Google Maps via SerpApi. Google Places is
  an optional key (backend/tools/__init__.py). The hero figure shows Google Maps via SerpApi,
  the deploy figure marks Google Places as optional.
- One SerpApi key covers flights, hotels and events, so "each live on its own key" became "each
  switching to live data on its own", as README.md says.
- The limits figure said 3 AI runs each for all 25 tests. It now says 1 demo run, 3 AI runs.
- The backup slide lists six repairs against a limit of five, and Alex's weather swap came last.
  It now says the last repair may never run, and when the weather swap runs.
- The results charts separate the known limits from the 23 core tests with a dashed line and the
  label "known limits, not in the 23".
- The hero figure names checkpoint 1 and checkpoint 2, as the title promises. The slide 4 script
  says "the second checkpoint". "Tool calling" became "any model that can call tools".
- Footer page numbers count the title, so they match the script's slide numbers.
- Colour: the closing tag is ink, not green, and "Your call" on the poster is ink, not the budget
  orange. The poster's limits line is body colour, not grey.
- Slide 2's problem statement is bold body size. The poster's "why agents" line now leads into
  the system figure. "Alex is a student, and an illustration" became "Alex, a student (an
  illustration)". The access code line is clearer.
- Scripts: slide 5 names the fifth repair (indoors for the rainy day), slide 9 names the in-memory
  trips, "paid search quota" became "search quota", "Be careful with this" was cut. The pitch
  uses the poster's terms (demo mode, AI mode, shorten to two nights) and states its planned
  time. Talk 950 words, 407 s planned (limit 420). Pitch 262 words, 113 s planned (limit 120).
- The poster PDF's author field now holds the authors, not the tagline.
- tools/check_writing.py also catches U+2010, U+2011, U+2043, U+FE58, U+FE63 and U+FF0D. The
  README rebuild loop skips fig_system_body.tex, which is an input fragment.

Not changed, with the reason:

- The hero figure stays dense on the slide (about 7 to 8 pt labels). Splitting it would cost a
  slide in a timed talk. The script walks through it in four numbered steps.
- Screenshot text on slide 6 and in the poster centre is small. The crops are native pixels and
  the key words ($180 over, the three options) are typeset large beside them.
- "Cheapest it built" stays: it is literally the cheapest plan the run built, and slide 5 says
  the limit of five repairs stopped it.
- Icons on the limits and deploy slides stay. They label categories, and each sits beside text.
