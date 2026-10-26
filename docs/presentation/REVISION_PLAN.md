# Revision plan for the deck, the poster and the report

Written on 26 October 2026 between 13.24 and 13.50 EDT, from AUDIT_BEFORE.md and the audit0 findings (findings_A to E in the audit scratch folder). This is the brief for whoever rebuilds slides.tex, poster.tex, the two scripts, check_writing.py and the report. A first draft went to three critics in parallel: a non-technical visitor, a hackathon judge, and an expert in AI agents and responsible AI. This version already includes their changes. Section 13 records what each critic said and what was decided. Where an earlier section and section 13 seem to disagree, section 13 wins.

This file is a working document. It quotes forbidden words and old titles on purpose, so it stays outside the checker's scope, like AUDIT_BEFORE.md.

## 1. The core story

### 1.1 The use case

Alex is a Boston college student we made up for this talk. Alex is always labelled as an illustration. The run itself is real. It is one run of the app with live flight and hotel prices and the AI turned on (docs/screenshots/03_over_budget_escalation.png, "LLM agents" badge and "Live data, google flights, google hotels, google maps", STORY_PLAN.md line 35).

1. **Setup.** Alex has $600 for a long weekend and types one sentence, "Chicago for 4 days, budget $600".
2. **Roameo asks.** Alex did not say where from or when, so Roameo asks. Alex answers "From Boston, leaving Nov 20".
3. **The AI agents go to work.** They compare 8 flights, 18 hotels and 59 events. Past years' weather for those dates says cold, with a 67 percent chance of rain. So they also look for indoor places, holiday markets and ice skating.
4. **Code adds up the money.** The first plan costs $1,235. Plain code tries five fixes, one at a time, and gets to $780. That is still $180 over.
5. **The moment of tension.** Roameo does not hide the gap. It stops and asks, "Would you like to raise the budget, shorten to 2 nights, or drive instead of flying?"
6. **The ending.** The choice is Alex's. Our tests replay Alex's exact sentence (test T16, sample prices). When the budget is raised, Roameo rebuilds the plan and checks it again. The plan fits and no question is left open. Alex says OK and gets a calendar file. Alex then books the trip on a site Alex trusts. Roameo never books or pays.

The spoken version for a visitor at the poster runs about 80 words, about 30 s.

> Alex, a student we made up, has 600 dollars for four days in Chicago and types one sentence. Roameo asks where from and when. Then its AI agents compare flights, hotels and events. Plain code adds up the prices. The first plan costs 1,235 dollars. Five fixes bring it to 780, still 180 over. So Roameo stops and asks Alex. Raise the budget, stay two nights, or drive? Nothing is booked until Alex says OK.

### 1.2 The novelty it reveals

One line, used in all three deliverables.

> A chat reply can tell you a plan fits your budget with nobody checking the sum. In Roameo, AI agents do the searching, plain code adds up every total, and when the money does not work it stops and asks you.

A shorter form for titles and the poster is "Roameo treats your budget as a limit, not a wish." The new part is not any single piece. It is the clear split of who decides what. The AI decides what you meant, what to ask and which searches to run. Code decides prices, totals and fixes. You decide the gap and the final OK. That split is the three main ideas.

### 1.3 Who benefits, in plain words

- **Students.** One sentence instead of many open tabs. A total added up by code, with live prices for the flight and hotel and clearly marked estimates for the rest. The final say on your own money stays yours. There is no user study, so no claim of time saved.
- **The community.** "A club planning a trip for four sees 2 rooms and the cost per person before anyone pays" (test T14). "A class can read the code to see an AI that asks before it spends." The code is free for anyone to copy and run. The demo runs free with no sign-ups or paid accounts in about three minutes (README.md line 16), with sample prices for 8 cities. A shared club link with live prices covers about 80 plans a month on the free search plan (README.md). An optional access code and a limit of 60 requests per address per hour help that free quota last. All of this is said as "can", never as "is used by". The first group to reach is student clubs.

## 2. The three main ideas

The tagline, used on the title slide, the preview, the close, the poster header and the report's first page:

> **AI agents do the legwork. Code checks the money. You make the call.**

Under it, everywhere it first appears: "An agent here is an AI helper with one job." This stops "agents" being heard as travel agents.

The three ideas are three actors, and each idea says what that actor decides.

| Idea | Part a | Part b | Part c |
|---|---|---|---|
| **1. AI agents do the legwork** (what the AI decides) | **They read your sentence and ask for what is missing.** Roameo never guesses where you leave from or when. If either is missing, it asks. It assumes one traveler and the number of nights if you do not say, and shows that ("Assumed 1 traveler"). Why ask? A guessed date or city gives a useless plan. | **They choose which searches the trip needs.** For Alex, flights, hotels, sights, events and weather. They compared 8 flights, 18 hotels and 59 events. When the weather looks cold, Roameo also looks for indoor places, holiday markets and ice skating. Searches the plan cannot do without are run even if the AI skipped them. | **They turn your plain words into changes.** "Make it cheaper", "more museums", "skip this place", "slower pace". Roameo edits the plan instead of starting over, and lists what changed. With the AI on, each stop also gets a visit guide. |
| **2. Code checks the money** (what plain code decides) | **Code adds up every total.** The flight ($278) and hotel ($162) come from live searches. Food ($280) and local transit ($60) are flat daily estimates, labelled as estimates. Code adds them to $780. The sum is exact for the prices shown. | **Code tries one fix at a time, at most five.** In Alex's run, a cheaper hotel, the cheapest flight, no paid events, free sights plus two that match Alex's interests, and indoor stops on the rainy day. Not every fix saves money, so code checks the total after each one. $780 is the cheapest plan it built in five fixes, not the cheapest trip possible. | **Code shows the gap, never hides it.** "$180 over your $600 budget", in red. Why code and not the AI? The total is checked again after every change, six times in Alex's run. Code gives the same exact sum every time, and we can test it. An AI model's answer can change from run to run. |
| **3. You make the call** (what you decide) | **You choose how to close the gap.** "Raise the budget, shorten to 2 nights, or drive instead of flying" (the app's own words). When Alex raises the budget, the plan is rebuilt and checked again (test T16). | **You see every step and every assumption.** The "What the agents did" list shows all 25 steps of Alex's run. The plan says "Assumed 1 traveler", which prices are live and which are estimates. | **Nothing is final until you say OK, and you book it yourself.** Saying OK only downloads a calendar file, and the download works only after approval. Why never book? Paying is a decision a person should make, on a site they trust. |

**How Alex threads through all three.** Idea 1 is the first half of Alex's run (the question, the searches, the cold weather). Idea 2 is the price chart of the same run ($1,235 to $780, $180 over). Idea 3 is the question Alex gets at the end, the step list Alex can read, and the OK that is Alex's. The evaluation then shows the tests behind each idea. The competitor slide compares who else does the searching and who checks the money. The close returns to Alex.

**Opening (announce).** Slide 3 and the script line "Roameo rests on three simple ideas. AI agents do the legwork. Code checks the money. You make the call. Let me show you each one with Alex's trip."

**Close (repeat).** Slide 11 and the script line "So, three ideas. AI agents did the legwork for Alex. Code checked the money and found the 180 dollar gap. And Alex made the call." The poster's bottom right block and the report's new section 8 say the same three sentences.

**The six helpers, said truthfully.** Roameo has six helpers and a coordinator. Four use the AI model, the request reader, the researcher, the change reader and the guide. The planner and the checker are plain code. The planner uses the AI only to write the friendly summary, and the checker never uses it. The coordinator is plain code. In demo mode, simple rules stand in for the AI everywhere (backend/llm.py lines 23 to 26). Sources are intake.py line 163, research.py line 133, feedback.py line 76, guide.py line 55, composer.py lines 440 to 447, and critic.py, which has no model call.

## 3. Words and style rules for everyone who writes

- **Plain names.** "AI agent" or "AI helper" on first use, defined as "an AI helper with one job". "The checker" for the critic. "The planner" for the composer. "The request reader" for intake. "The change reader" for feedback. "The coordinator" for the orchestrator. "Asks you" for a checkpoint. "The AI model" for LLM. "Fix" is the one word for a repair, a trim or a cut. "No sign-ups or paid accounts" for "no keys". "Demo mode" stays because the app's badge says it. The first time, it is explained as "practice runs with sample prices, so anyone can try it without sign-ups or paid accounts".
- **Never in what the audience reads or hears.** Intake, Composer, Critic as a name, Orchestrator, awaiting_approval, needs_clarification, state machine, pipeline, guardrail, fallback, gate, arm, module, checkpoint, harness, JSON, tool calling, T-numbers in the deck or poster, Render, rate limit. Service names appear only in credits ("data from Google Flights, Hotels, Events and Maps through SerpApi") and in report sections 2.3, 6.2 and 6.3.
- **Report exception, decided here.** Report 2.2 and section 6 may show file paths (backend/agents/critic.py) in monospace, as code, for judges who want depth. They never show state names or function names. Test ids may appear in the report's section 5 tables, always with the test's plain title.
- **What a test is.** Said once in each deliverable. "A test is a conversation we wrote in advance, typed into Roameo, with code that checks the answer, for example that it asks for a missing date, or that it reports the gap instead of hiding it." Passing means every check in that conversation came out right. "3 runs" means we ran the same tests three times with the AI on, because the AI can answer differently each time.
- **Writing rules.** Owner rule 5 and the plain-wording lists apply to every visible word, every script line and every \note block. Clock times read "5 pm" or "17.00". Ranges read "18 to 30". Web addresses appear without "https://". Avoid naming places whose names contain a banned word, such as Cloud Gate.
- **Colour.** Near-black type (#1A1A1A) on white. UMB blue #005A8B for structure (axes, figure strokes, the three idea marks). The slides' primary #08457E for slide titles. Dark navy #132245 only for the poster header band and the deck's title band. One warm accent, UMB orange #FF791F, only for the moment of tension, meaning the $180 gap, the over-budget bars in the chart and the frame of the escalation crop. Green (#2E7D32) only for an approved plan or a passed test. Roameo's app teal appears only inside screenshots. No decorative rules, no dashed boxes, no outlined chips, no numbered circles repeated on every slide.
- **Idea marks.** The three ideas get one small mark each, the same in deck, poster and report: a magnifier for AI agents, a sum sign for code, a hand or check for you. They are drawn in UMB blue, not in three colours.
- **Logos.** At native resolution and only scaled down. The deck title slide uses slides/logos/Blue-UMB-logo-lockup.png at about 3.2 cm wide. Content slides use Umass_boston_textlogo.png at about 1.6 cm wide in the footer. The poster header uses poster/logos/White-UMB-logo-lockup.png on the navy band at 8.5 in wide (269 ppi). The report title page uses the blue lockup at 2.2 in wide.
- **Affiliation line.** Word for word under the names: "Department of Computer Science, University of Massachusetts Boston".
- **Empty space.** No \vfill above a frame body. Figures are sized to the height left under the title, using \includegraphics with width, height and keepaspectratio. The target, measured with the audit's whitespace.py, is a largest empty rectangle of at most 8 percent of the content area on every slide and at most 3 percent on the poster.
- **Readable screenshots.** Crop each one to the two or three lines that carry the point. Text inside a crop must show at least 9 pt tall on a slide and at least 24 pt tall on the poster.

## 4. Where each of the seven questions is answered

| Question | Deck (slide, spoken) | Poster | Report |
|---|---|---|---|
| 1. What problem? | Slide 2. Alex's one sentence, and everything has to add up. The 89 and 12 percent survey [2] on the slide and in the spoken line. | The use case strip starts with the problem sentence. | 1.3 Problem statement, told through Alex, keeping [1] and [2]. |
| 2. Direct and indirect competitors | Slide 9. Three direct groups and one indirect line, with what each says it is for, and where Roameo differs. Backup B3 holds the sourced table. | Bottom band, left block. | 7.2, with a source for every cell, modest wording, and a direct and indirect split. |
| 3. Target market | Slide 9, lower line, with three groups (students on short trips, budget travelers, small groups who split the cost) and the first group to reach (student clubs). | Bottom band, left block. | 1.4 Target users and 7.1 Who it is for. No market size, only cited survey figures. |
| 4. How does it work? | Slides 3 to 6, the three ideas on Alex's run. Backup B1 shows the six helpers, AI or code. | The three columns. | 1.5, section 2 (template headings kept, with an AI-or-code column and an idea column), section 3. |
| 5. Evaluation and responsible AI | Slide 7 covers the tests, what a test is, passing, 3 runs, demo mode, honest caveats, and what the AI adds. Slide 8 covers responsible use, what goes where, what can be wrong, and what it cannot do yet. | Each column ends with "How we tested it". Bottom band, middle block "Responsible use and limits". | Section 5, with prose instead of machine output and the full caveats. 6.5 Responsible use of AI covers data flow, privacy and failure modes. |
| 6. Key sources and acknowledgement | Slide 11, a bottom strip with thanks to the PEAAII organisers and the credits. Backup B6 holds the full source list. | Bottom band, right block "Thanks and sources". | A new Acknowledgements section. References gain the data services, the model, the template and the theme. |
| 7. Anything else | Slide 10 covers trying it free, sharing one link, what comes next (a pilot with 5 to 10 students measuring overspend and time to a plan) and the ask. | Bottom band, right block, next steps and the QR codes. | New 7.4 What comes next, 5.7 Possible improvements, 8 Conclusion. |
| Students and community benefit | Slide 10 and the close. | Bottom band, left block, and the header tagline. | New 7.3 How students and the community benefit. |

## 5. The deck, slide by slide

The page is 566.9 by 368.5 pt, in the Elegant theme as now. The pace is 140 spoken words a minute, checked with tools/timing.py. The main slides total **373 s planned** (about 870 spoken words), which leaves room for handovers under the 420 s cap. Each title is one full sentence without a colon. Each slide has one visual and at most two short supporting lines. Speakers alternate by idea. Zhen Lu opens and takes ideas 1 and 2. Noctis Zhang takes idea 3, the market and the close. The team can change this split.

| # | Title (full sentence, no colon) | The one visual | Supporting lines (at most two) | Spoken gist | s |
|---|---|---|---|---|---|
| 1 | Roameo plans your trip and lets you decide on the money | A navy band at the top, then the blue UMB lockup on white beside the title, the tagline in large type, "An agent here is an AI helper with one job", the names, the affiliation line, "PEAAII AI Applications Hackathon 2026, Agentic AI", and two QR codes (try it, code) | The tagline | Names, affiliation, Roameo in one line, the tagline. | 12 |
| 2 | Alex has $600 for four days in Chicago and types one sentence | On the left, Alex as a simple drawn figure with "a student we made up". On the right, the start.png crop of the typed sentence, large. Under it, the cost as five small boxes (flights, hotel, sights, food, transit) adding up to "?" against $600 | "Everything has to add up, and again after every change." "89% of travelers want AI help planning, but only 12% are happy to let it decide alone [2]." | The problem. A chat reply can do the sum itself and say it fits, with nobody checking. Most people want help, not an AI that decides for them. | 32 |
| 3 | Roameo rests on three simple ideas | Three wide panels across the slide, one per idea. Each has its mark, its name, its three parts as three short phrases, and one fact from Alex's run (asked where from, $1,235 to $780, "raise the budget, 2 nights, or drive") | None beyond the panels | The preview. Name the three ideas and the three actors (AI, code, you). We follow Alex through them. This slide also answers "how does it work" at a glance. | 20 |
| 4 | AI agents ask first, then choose what to search | Three panels. (a) The crop of Roameo asking "Where are you leaving from? What date?" from Alex's run, large. (b) The crop of the step list rows where the researcher chose its searches, with three big counts (8 flights, 18 hotels, 59 events). (c) The quick-reply buttons from Alex's run ("more museums", "slower pace", "make it cheaper", "different hotel") with one line on how a plain-word change becomes an edit | "An agent here is an AI helper with one job." "It never guesses where you leave from or when." | Idea 1 and its three parts. Why it asks. The AI picks the searches, and that is the agent part. Cold weather adds indoor searches. Your words become edits, not a restart. | 42 |
| 5 | Code adds up every price and tries five fixes, from $1,235 to $780 | The price chart across the full slide width. Six bars ($1,235, $984, $984, $1,014, $780, $780), each fix named under its bar in plain words, the $600 line in UMB blue, the $180 gap in orange. Beside it a small cost line from the app ($278 flight, $162 hotel, $280 food estimate, $60 transit estimate) | "Not every fix saves money, so code checks the total after each one." "The AI never adds up the money." | Idea 2, parts a and b. Live prices and labelled estimates, summed by code. One fix at a time, at most five. Why code. The chart is labelled "one live run". | 45 |
| 6 | Still $180 over, Roameo stops and asks Alex what to do | The escalation crop, large. The red bar and the question with its three choices are readable, framed in orange. This is the moment of tension | "Raise the budget, stay two nights, or drive." "Nothing is final until Alex says OK, and Roameo never books or pays." | Idea 2 part c turns into idea 3. Alex chooses. Our tests replay this exact sentence, and when the budget is raised the plan is rebuilt, checked and fits. Alex sees every step in the list. Saying OK only downloads a calendar file. Why it never books. | 40 |
| 7 | All 23 tests of what Roameo should do pass, with and without the AI | One chart of the five test groups from the results file in plain names (asking you and following your changes 10, unclear or bad input 4, adapting to weather, season and what you love 4, planning basics 4, nothing final without your OK 1), each bar full and green, each tagged with its idea mark. One example per idea beside it. A small note on the 2 known limits | "A test is a conversation we wrote in advance, with code that checks the answer." "We wrote them ourselves, on sample prices, and ran them three times with the AI." | What a test is, what passing means, demo mode, why 3 runs. Every core test passed in each of the 3 runs. What the AI adds, since only the AI understood "first weekend of December". The honest caveats, which are self-written tests, sample prices and weather in both modes, a small sample and no user study. | 50 |
| 8 | Roameo never books or pays, and says what it cannot do yet | On the left, two thirds wide, a "what goes where" drawing (section 10). On the right, four short "not yet" items in a small plain grid (8 cities in demo mode, food and local transit are estimates, AI-written summaries and visit tips can be wrong or out of date, no user study) | "No accounts. Your trip stays in the server's memory until it restarts." | Responsible use of AI, named out loud, in three parts that echo the ideas (the AI asks and its jobs are narrow, code shows its math and labels sample prices, you decide and book yourself). Privacy in one sentence. What can be wrong. | 38 |
| 9 | Other apps plan or sell trips, Roameo treats your budget as a limit | Three columns of direct competitors, each with what it says it is for and a source mark. (1) General chat assistants such as ChatGPT and Gemini. (2) Assistants inside a booking site, such as Expedia's Romie, which helps plan, shop and book inside Expedia [3]. (3) AI trip planner apps such as Mindtrip, Layla and Wonderplan, each described from its own site with the date accessed, or from [4] labelled "a review". Under them, one row "Also used instead" (spreadsheets and group chats, a travel agency, TripIt and Google Travel for keeping bookings). Under that, "Built for", with three groups and "first, student clubs" | "We have not tested the others. This is what each says it is for." | Q2 and Q3, said modestly. Roameo is not a booking site and not a chat window. It is the planning step in between, and it could sit on top of either. No market size. | 38 |
| 10 | Anyone can try Roameo free, and a club can share one link | On the left, three steps as a picture: a laptop (demo mode, 8 cities, about three minutes, no sign-ups), one shared link for a club (optional access code), then live prices one service at a time. On the right, the two QR codes, large | "Free code anyone can copy and run." "Next, a pilot with 5 to 10 students." | The student benefit, the community benefit (the club of four, the class reading the code), what comes next (the pilot measuring overspend and time to a plan, links to booking sites with you still the one who books, more AI runs) and the ask, which is to try it and tell us where it goes wrong. | 32 |
| 11 | AI did the legwork, code checked the money, and Alex made the call | The three idea panels from slide 3 again, each now filled with Alex's result, and the QR code. A bottom strip with the thanks and credits in small but readable type | "Thanks to the PEAAII organisers. Data from Google through SerpApi, Ticketmaster, Open-Meteo and OpenStreetMap. AI model Claude Haiku 5.5 through OpenRouter. Elegant slide template." | Repeat the three ideas in Alex's words, then the novelty line, the thanks, and "scan to try it". | 24 |
| | | | | **Total** | **373** |

**Backups.** These come after slide 11 and are not timed. Their titles have no colon, for example "Backup, the checker's fixes in a fixed order".

- **B1. How it works inside.** The six helpers and the coordinator on the three-band figure, each marked "uses the AI" or "plain code". Why six and not one prompt: each AI step has a narrow job, and code checks its output. Activities are kept to an allowed list (intake.py line 166). A trip fact changes mid-conversation only if your own words state it (intake.py lines 168 to 174). Searches the plan needs are re-run if the AI skipped them (research.py lines 89 to 93). The researcher stops after 8 steps (research.py line 19). Why not more helpers: a separate agent per search would add hand-offs without adding decisions.
- **B2. The checker's fixes in order.** A weather problem is fixed first when one is found. Then come a cheaper hotel (which can drop two levels and use two of the five fixes), the cheapest flight, no paid events, and free sights (critic.py lines 44 to 52). Alex's actual order is shown beside it. Say that, under the cap of five, the free-sights fix may never run.
- **B3. The competitor table.** Every cell has a source, taken from report 7.2.
- **B4. The 25 tests.** Each in plain words, in the results file's five groups plus the 2 known limits, filled to the bottom of the slide.
- **B5. Weather and season.** The Detroit in December crop (it asks which city in Michigan, uses past years' weather for those dates, puts indoor stops first) and the visit guide crop.
- **B6. Sources and acknowledgement in full.**

**Script (pres-note.md).** Rewrite it to fit the table above.
- Remove "Most tests are about asking you". The 10 of 23 in that group are the largest group, not most.
- Explain demo mode, a test, passing and 3 runs in the words of section 3.
- Name responsible use of AI.
- Say the competitor line modestly.
- Thank the organisers.
- Write numbers as they are spoken.
- Regenerate every \note block in slides.tex from pres-note.md with tools/sync_notes.py.

**Not in the deck.** There is no live demo inside the 7 minutes, because no slot fits it. Slides 4 to 6 use crops of the real run. Section 12 lists what the team should prepare instead.

## 6. The poster

The poster is landscape, 48 by 27 in (3456 by 1944 pt) as now. It uses the Gemini theme with beamercolorthemeumb.sty, but with the headline rule, block separators and alerted separators set to white or none, because they are decorative lines. Credit "Poster theme Gemini by Anish Athalye" in the thanks block. Body type is at least 28 pt, column heads 48 pt, the title 90 pt.

| Band | Height | Content | Figures and sizes |
|---|---|---|---|
| Header, navy #132245 | 4.0 in | On the left, White-UMB-logo-lockup.png 8.5 in wide. In the centre, the title "Roameo plans your trip and lets you decide on the money", the tagline and "An agent here is an AI helper with one job", the names, the affiliation line, and "PEAAII AI Applications Hackathon 2026, Agentic AI". On the right, two QR codes 3.2 in each, labelled "Try it" and "Code", with the addresses without https | The logo and the vector QR codes |
| Use case strip, white | 4.5 in | Alex's trip as one strip in eight steps, left to right. (1) "Alex, a student we made up, $600, Chicago, 4 days". (2) It asks where from and when. (3) 8 flights, 18 hotels, 59 events, cold and rain likely. (4) $1,235. (5) Five fixes to $780. (6) $180 over, in orange. (7) "Raise the budget, 2 nights, or drive?" (8) The budget is raised, the plan is checked and fits, Alex says OK, in green, marked "from our tests". On the far right, the novelty line in two lines | A redrawn story figure, 46 in by 4.2 in, vector, with the start crop and the escalation crop at the two ends, 3.8 in tall |
| Three columns, one per idea | 14.5 in | Column 1 is "AI agents do the legwork", column 2 "Code checks the money", column 3 "You make the call". Each column holds its three parts as three stacked panels (one figure and one or two sentences each), then a short panel "How we tested it" with that idea's test examples. Each column is 15.2 in wide, with 0.5 in gutters | **Column 1.** (a) The "where are you leaving from, what date" crop, 13 in wide. (b) The step list rows of the chosen searches with the three counts, 13 in wide. (c) The quick-reply buttons crop, 13 in wide. **Column 2.** (a) The app's cost line ($278 + $162 + $0 + $280 estimate + $60 estimate = $780), 13 in wide. (b) The price chart, 14.5 in by 6 in, vector. (c) The red "$180 over" crop, 13 in wide, in an orange frame. **Column 3.** (a) The three choices crop, 13 in wide. (b) The plan's own notes crop ("Assumed 1 traveler", "Live data, google flights, google hotels, google maps", "est." prices), 13 in wide. (c) The "Approve plan" button and the "Waiting for your approval" badge from Alex's run, with a green calendar mark. All crops come from Alex's run |
| Bottom band, three blocks | 3.6 in | **Left**, "Who it is for, and who else helps plan trips". The three user groups, the three competitor groups with source marks, the indirect line, and "first, student clubs". **Middle**, "Responsible use and limits". It never books or pays, labels sample prices, shows every step, plus what goes where, what can be wrong, the four "not yet" items, and "a small, honest check, not a user study". **Right**, the close "Three ideas, one trip" in three sentences, thanks to the PEAAII organisers, the credits, the sources [1] [2] [3] [4] in short form, and the ask | Text, with one small data-flow drawing in the middle block, 5 in by 2.6 in |

Every area is filled. The use case strip and the three columns use the full width. Re-measure with whitespace.py after the build. The target is a largest blank of at most 3 percent.

**The pitch (poster-note.md).** It opens with the 30-second version from 1.1, then one sentence per idea while pointing at its column, then the competitor line and the ask. The full pitch is about 90 s, with the 30-second version marked as the short one.

## 7. The report

### 7.1 Edit in place or rebuild

**Decision. Rebuild with a python-docx builder, and keep the team's file.**

Why. The report has 218 writing hits, 95 semicolons inside table cells, hand-typed captions, two figures taller than the page and full table grids. These are easier to fix once in code than run by run in Word. A builder also lets check_writing.py read the same text that goes into the docx.

- Copy the team's file first to docs/Roameo_Project_Report.original.docx, byte for byte, and check it with sha256sum. Never edit the original.
- Put the builder at docs/presentation/report/build_report.py. Run it as `uv run --no-project --with python-docx==1.1.2 python -I docs/presentation/report/build_report.py`. The text lives in docs/presentation/report/report_text.py, or in a plain text file the builder reads, so it can be checked and diffed. The output is docs/Roameo_Project_Report.docx.
- Open the original as the template with python-docx Document(original), clear the body, and keep the styles, headers, footers, page settings and numbering. Afterwards check that page size, margins, heading numbering and the contents list survived. If the original's "Contents" is a field, insert a fresh contents field and set updateFields so Word fills it on opening. If it is plain text, write the list by hand. The footer reads "Roameo, PEAAII AI Applications Hackathon 2026, page N", with no middle dot.
- Figures come from the original docx media and from docs/screenshots, cropped like the deck. Save them under docs/presentation/report/figures/. Each is at most 6.0 in tall and never upscaled. Use real Word captions (Caption style) for figures and tables. Tables have no inner grid, only a light shaded header.
- Use American spelling throughout (travelers, behaviors), since the team mostly wrote American.
- Word count target is 6,000 to 6,800, close to the team's 6,400.

### 7.2 Section by section

| Section | Keep | Change |
|---|---|---|
| Title page | Event line, Roameo, the members in order | The tagline becomes the three-idea line. Add the blue UMB lockup at 2.2 in wide, and the affiliation line under the names. Write "Team Roameo" and "Zhen Lu and Noctis Zhang", without "Team:" and "Members:". Addresses without https. Date "October 2026". |
| New "Roameo in one page" (unnumbered, before the contents) | | Alex's story in six steps, the three ideas with their three parts as a 3 by 3 table, the novelty line, and the headline result (all 23 core tests pass in both modes and in each of the 3 AI runs). |
| 1 Project Overview | 1.1 to 1.6 headings | 1.1 is the title sentence without a colon. 1.2 is the team table, with the affiliation added. 1.3 tells the problem through Alex, keeping [1] and [2]. 1.4 gives the target users plus the three groups, with ranges as "18 to 30" and "1 to 4 nights". 1.5 gives the solution as the three ideas and their parts, with Alex replacing the New York couple as the running example. 1.6 keeps the "why agentic AI" table in plain words, with the origin row fixed (it asks when origin or date is missing, and shows its other assumptions). |
| 2 Agentic AI Design | **All six template headings, worded as the template has them** (2.1 Overall workflow, 2.2 Agent responsibilities, 2.3 Tools and external resources, 2.4 Context and information required, 2.5 Human-in-the-loop decisions, 2.6 with its colon removed, "Architecture choice, why six agents and not more") | 2.1 opens with the three ideas and how they divide the work. Figure 1 is redrawn to match the deck's three-band figure, exported from the TikZ source as a 300 dpi PNG. 2.2 is a table with columns for helper (plain name), file (monospace), AI or code, what it decides, inputs, what happens if it fails, and the idea it serves. 2.3 lists tools and sources. Service names are allowed here. Google Events covers about the next 10 days, the forecast covers 15 days and then past years' weather, attractions also come from Google Maps through SerpApi, and any city gets its nearest airport. 2.4 keeps the context content, fixed. 2.5 keeps the human decisions table, fixed (it asks when origin or date is missing, and adds that in AI mode a typed reply such as "looks good" can also count as approval, because the change reader may mark it as approval, feedback.py lines 80 to 82, checked). 2.6 explains why six and not one prompt, and why not more (as in B1). The words state machine, pipeline, guardrail, fallback and orchestrator come out, and no state names appear. |
| 3 Working Prototype | Repository, live demo, two modes, Figure 2 | Remove "branch hackathon-2026". Explain demo mode in plain words, with 8 cities. Figure 2 becomes a crop of Alex's plan, at most 6 in tall. |
| 4 Demo | Three scenes | The three scenes are the three ideas on Alex's run, the same as the deck, plus the tested ending. The 2.5-minute live-demo table goes, since the deck has none. Add a note on the poster-table demo and a recorded backup (section 12). Figures 3 to 5 are cropped. The New York revised plan and the approved screen may appear only with the caption "another trip, New York". |
| 5 Evaluation | 5.1 to 5.7 | 5.1 explains what a test is, passing, demo mode and the 3 runs, in plain words. 5.2 is the results table in the results file's own groups, with an idea column, and "Expected" and "What happened" written as short prose (no semicolons, no machine output). The results file's labels give 10, 4, 4, 3, 1 and 1 ("Functional" 3 and "Functional / E2E" 1 shown apart). 5.3 is what went well. 5.4 covers failures found during development, turned from 24 bullets into a short table of the five most useful lessons, with numbers kept in no results file marked "from the team's development notes". 5.5 gives the limits and the caveats in full (section 11). 5.6 Live-data check is rewritten around Alex's live run, which has its numbers in the repository, and drops the old New York numbers. 5.7 covers possible improvements. |
| 6 Project Documentation | 6.1 to 6.5 | 6.2 keeps the command lines in monospace (exempt). 6.3 adds to the tools table that the model must support tool calling. 6.4 fixes the version history and the branch. 6.5 Responsible use of AI is expanded in three parts that echo the ideas, plus the data-flow and privacy paragraph from section 10 and the failure modes (AI-written summaries, tips and exhibition details can be wrong, only exhibition links are checked, web text read by the guide could try to steer the AI). The team's own disclosure of AI coding assistants is kept. "Harness" is removed. |
| 7 Market Context | Competitor table, survey figures, the honest position | 7.1 Who it is for gives the three groups, why students, and the first group (student clubs), with no market size. 7.2 covers direct and indirect competitors. Every cell has a source or is worded as Roameo's own design. Expedia is "planning, shopping and booking" [3]. "Prices everything from live sources" and "hands off booking" are gone. The three survey figures are given as three separate cited numbers, not as a range. The old 7.1 question table is kept inside 7.2, fixed. 7.3 covers how students and the community benefit. 7.4 covers what comes next and what we ask. |
| New 8 Conclusion, "Three ideas, one trip" | | The three ideas repeated with Alex, the novelty line, and one honest limit. |
| New Acknowledgements | | Thanks to the PEAAII AI Applications Hackathon 2026 organisers. Credits for the data services (Google Flights, Hotels, Events and Maps through SerpApi, Ticketmaster Discovery, Open-Meteo, OpenStreetMap), the AI model (Claude Haiku 5.5 by Anthropic, through OpenRouter), the Elegant slide template, the Gemini poster theme by Anish Athalye, and the open-source libraries (FastAPI, React, Vite, Tailwind CSS, Leaflet). |
| References | [1] to [8] | Kept, with dates. Add entries for the data services, the model, the template and the theme, and the competitors' own pages if they are used. [6] and [7] get an access date. Addresses without https. |

## 8. Figures to draw or keep

All screenshot crops for the story come from Alex's run, docs/screenshots/03_over_budget_escalation.png (2880 by 6966 px), unless noted.

| Figure | Used in | Action | Source |
|---|---|---|---|
| Title band with the UMB lockup | Deck 1 | New | slides/logos/Blue-UMB-logo-lockup.png |
| Alex and the sum | Deck 2, poster strip | Redraw fig_persona as a cleaner figure, vector | Alex's sentence from Alex's run |
| start.png crop | Deck 2, poster strip | Keep, crop tighter | presentation/screenshots/start.png (803 by 550) |
| Three idea panels | Deck 3 and 11, report one-page summary | New TikZ figure fig_ideas.tex | Section 2 of this plan |
| The question crop | Deck 4, poster column 1 | New crop | Alex's run, the chat rows "Where are you leaving from? What date..." |
| Chosen searches with counts | Deck 4, poster column 1 | New crop of the step list rows plus vector counts | Alex's run, the "What the agents did" Research rows |
| Quick-reply buttons | Deck 4, poster column 1 | New crop | Alex's run, under the chat |
| Cost line | Deck 5, poster column 2 | New crop | Alex's run, the cost chips under the budget bar |
| Price chart | Deck 5, poster column 2, report 2.5 | Rework fig_critic to full width, orange only for the gap | Alex's run, the Critic rows of the step list |
| Escalation crop | Deck 6, poster columns 2 and 3, report 4 | Keep esc_budget.png and esc_question.png, crop to the bar and the question | presentation/screenshots/ |
| Plan notes crop | Poster column 3 | New crop | Alex's run, "Assumed 1 traveler" and the live-data line |
| Approve button and badge | Poster column 3 | New crop | Alex's run |
| Test groups chart | Deck 7, report 5.2 | Rework fig_results with the five plain group names and idea marks, green bars | docs/evaluation_results.json and _llm.json |
| What goes where | Deck 8, poster bottom middle, report 6.5 | New TikZ figure fig_dataflow.tex | Section 10 of this plan |
| Competitor columns | Deck 9, poster bottom left, report 7.2 | New, text in three columns | Report references [3] [4], the products' own pages |
| Try it and share it | Deck 10 | Rework fig_deploy, without the word Render on the slide | README.md lines 16 and 61, backend/app.py lines 26 to 43 |
| QR codes | Deck 1, 10 and 11, poster header | Keep fig_qr (vector) | The live demo and repository addresses |
| Workflow figure | Report 2.1, deck B1 | Redraw as the three-band figure | backend/agents/ |
| Visit guide, Detroit in winter | Deck B5, report 4 | Keep, crop to at most 6 in tall | docs/screenshots/07_visit_guide.png, 08_winter_detroit.png |
| Revised and approved New York screens | Report 4 only | Crop, caption "another trip, New York" | docs/screenshots/05_revised.png, 06_approved.png |

Retire fig_story (five steps), fig_system (four steps) and the fig_limits tiles. The three-idea figures replace them.

## 9. Every number and its source

| Number | Source | Note |
|---|---|---|
| $600, Chicago, 4 days, from Boston, Nov 20, 3 nights, 1 traveler assumed | docs/screenshots/03_over_budget_escalation.png | Live prices, AI on (STORY_PLAN.md line 35) |
| 8 flights, 18 hotels, 59 events | Same screenshot, step list | Roameo keeps at most 8 flights (tools/__init__.py line 164), so say "compared 8". The events came from Ticketmaster |
| Cold, 67 percent chance of rain on Nov 20 and 21, light snow on the 21st | Same screenshot, day headers, "typical for these dates (2023 to 2025)" | Past years' weather, not a forecast |
| Indoor places, holiday markets, ice skating searched | Same screenshot, step list, and research.py lines 113 to 123 | A rule in the researcher, not the AI |
| $1,235, $984, $984, $1,014, $780, $780, five fixes, $180 over, the three options in the app's words | Same screenshot | One live run, say so |
| $780 = flight $278 + hotel $162 + activities $0 + food estimate $280 + local transit estimate $60 | Same screenshot, cost chips | $340 of the $780 is flat estimates |
| 25 steps in the step list | Same screenshot, "hide (25 steps)" | |
| At most 5 fixes | backend/agents/orchestrator.py line 34 | |
| $300 test gives $778, $478 over | docs/evaluation_results.md and _llm.md, T6 | Report and backups only |
| The budget raised after the question, the plan then fits, no question open | backend/eval/run_eval.py lines 120 to 124, results T16 | Sample prices, and only the "raise the budget" path is tested |
| 25 tests, 23 core, 2 known limits | docs/evaluation_results.json and _llm.json | README.md line 94 says 18, which is stale. Record it |
| 23 of 23 core pass in demo and AI mode, 51 of 51 checks | docs/evaluation_results.md line 4, _llm.md line 4 | |
| Every core test passed in each of the 3 AI runs | docs/evaluation_results_llm.json, runs 3 | "Consistency" is the share of runs that passed (run_eval.py line 213). Only the first run's details are saved (line 234). Never say "same result every time" |
| Known limits 1 of 2 in demo, 2 of 2 with the AI | Same files, line 5 | The AI understood "first weekend of December" (T18), the rules did not |
| Groups 10, 4, 4, 3 + 1, 1 | Same files, category field | Plain names in section 5 |
| About 3 minutes to start in demo mode | README.md line 16 | Time it once if possible, otherwise cite the README |
| 8 cities in demo mode | backend/fixtures/demo_data.py lines 8 to 15 (Detroit included) | README.md line 108 says 7. The code wins. Record it |
| 60 requests per address per hour, optional access code | backend/app.py lines 26 to 43, render.yaml | The limit counts an address the client reports, and the access code is off unless set |
| The free plan sleeps after 15 idle minutes | README.md line 61 | Report and team notes only |
| Forecast 15 days, then past years' weather (2023 to 2025) | backend/tools/__init__.py lines 507 to 518 and 544 | README says 16. Record it |
| Google Events covers about the next 10 days | backend/tools/__init__.py lines 395 to 398 | |
| About 3 searches per plan, about 80 plans a month on the free search plan | README.md | Deck slide 10 spoken and the report |
| AI model Claude Haiku 5.5 through OpenRouter | backend/llm.py line 17, render.yaml, README.md | The results files do not name the model. Record it |
| 89% want AI in trip planning, 12% comfortable with AI deciding alone | Report reference [2] | |
| 303 minutes, 277 pages (US 524 minutes) | Report reference [1] | Report only |
| 10%, 22%, 29% use generative AI for trip planning | References [5], [6], [7] | Three separate surveys, not a range |
| Amadeus closed its portal on July 17, 2026 | Reference [8] | Report 2.3 and 6.4 |
| First prototype July 2025, rebuild October 2026 | git log | Report 6.4 |

**Disagreements to record.** These go in report 5.5 as a short note and in the docs/presentation README.
- The README says 18 scenarios. The results files have 25.
- The README says live airport codes exist only for the built-in cities. The code finds the nearest airport for any city.
- The README says 16 forecast days. The code uses 15.
- The README says 7 demo cities. The sample data has 8.
- The README lists 7 agents. The truthful wording is 6 helpers plus a coordinator, which is code.
- The results files do not name the model.
- The report's old "origin assumed" contradicts the code.
- The old 5.6 numbers are in no repository file.

## 10. What goes where, and privacy (for deck slide 8, the poster's middle block and report 6.5)

These are the truthful statements, checked by the AI-agent critic against the code. The slide uses the short forms in bold. The report may use all of them.

1. **In AI mode, what you type goes to the AI model through OpenRouter.** In demo mode nothing goes to an AI model (intake.py line 163, feedback.py line 76, llm.py lines 17 to 26).
2. The AI model also gets the trip details (origin, dates, travelers, budget, interests), the first six search results per search, and the plan facts for the summary (research.py lines 80 and 131 to 132, composer.py lines 443 to 447).
3. **The searches get the city, the dates and airport codes, not your sentence or your budget.** The flight search gets airport codes, dates and one adult. The hotel search gets the city, the dates and at most 2 adults (tools/__init__.py lines 145 to 146 and 190 to 191).
4. Google Maps through SerpApi gets "top sights in" the city, plus any place you name when you ask to add it. Google Events gets "Events in" the city. Ticketmaster gets the city and a date window (tools/__init__.py lines 228, 270, 399, 442 to 446).
5. For museums, the visit guide sends the place, city and month to a Google web search, then to the AI model (guide.py lines 36 and 55 to 58).
6. Open-Meteo gets coordinates and dates, and the typed city name for cities outside the built-in list (tools/__init__.py lines 60 to 61 and 528 to 552).
7. **Your browser loads the map and the street routes from OpenStreetMap** (AttractionsMap.tsx lines 24 and 80).
8. **No accounts. Trips stay in the server's memory until it restarts** (orchestrator.py line 329). While the server runs they do not expire, and search results are cached in memory.
9. Addresses are kept in memory for one hour for the request limit (app.py lines 29 to 43). The access code, if set, is saved in your browser.
10. Roameo writes no log of its own. The web server's standard access log records addresses and paths, not message text. **Never claim "nothing is logged" or "no data leaves your computer".**
11. **API keys stay on the server.** The health check only reports whether each key is set (llm.py lines 26 and 33, app.py lines 53 to 55).
12. **The calendar file downloads only after you approve, and nothing is booked or paid** (app.py line 97, backend/tests/test_roameo.py lines 22 to 30, orchestrator.py lines 17 and 164).
13. **Sample prices are labelled** with a "Demo mode, sample prices" badge, "sample price" on each item, and "est." on built-in sight prices (TravelAgent.tsx lines 103, 246 to 247, 344, 457).
14. **Every step is shown in the list** (orchestrator.py lines 46 to 47). Visit guides exist only in AI mode.
15. **What can be wrong.** The AI writes the plan summary from the computed facts, and nothing checks what it writes. Visit tips and highlights are AI-written and labelled "Written by the Guide agent". For exhibitions, only the link is checked against the search results, not the title or dates. Web text read by the guide goes into the AI's prompt and could try to steer it (composer.py lines 437 to 447, guide.py lines 52 to 64, TravelAgent.tsx line 438).

## 11. What not to claim

- No user study. So no time saved, no satisfaction, no "students love it", no plan-quality score.
- No market size and no invented numbers. Only the cited survey figures.
- Not "most tests are about asking you".
- No regrouping of the tests that looks curated. Use the results file's own groups, with idea marks.
- No competitor weakness stated as fact. Say what each says it is for, with a source, and "we have not tested the others".
- Not "every price comes from a search", not "prices everything from live sources", and not "the total is always right". Food and local transit are flat estimates ($340 of Alex's $780). Built-in sight prices are estimates. Many events have no listed price and count as $0. Say "exact for the prices shown".
- Not "hands off booking to any site". Booking links are a future idea.
- Not "assumes your origin", and not "always asks". It asks when origin or date is missing, and it shows its other assumptions.
- Not "any OpenRouter model". Any model there that supports tool calling.
- Not that Alex is real or a user. Alex is made up, the run is real, and the ending comes from a test with sample prices.
- Not that Alex chose two nights or driving. Only raising the budget is tested.
- Not the old 5.6 New York numbers ($1,720, $220 over, $506), and not the branch hackathon-2026.
- Not "works for any city". Demo mode has 8 cities. Live mode looks up the nearest airport.
- Not "a forecast" for Alex's weather. It was past years' weather for those dates.
- Not "same result every time". Say "every core test passed in each of the 3 runs".
- Not "the AI runs tested live data". Both modes used the same sample prices and weather, so the AI runs test how the AI reads requests and picks searches.
- Not that the rainy-day test proves the rainy-day rule. On sample weather the rain chance never goes above 50 percent, and the rule starts at 60, so T9 passes without the rule firing (tools/__init__.py line 502, run_eval.py lines 86 to 91). The rule did fire in Alex's live run. Say both in report 5.5.
- Not "a test checks the total is the sum of its parts". No test checks the sum on its own.
- Not that T13 tests the calendar download. It tests that the plan only counts as approved after you say OK. The download guard is tested in backend/tests/test_roameo.py.
- Not "the AI is reliable". 3 runs is a small sample, and demo mode is the same every time by design.
- Not UMass Boston endorsement. Only the authors' affiliation.
- Not "nothing is logged", not "no data leaves your computer", and not "keeps no data".
- No adoption claims for the community benefit. Say "can".

## 12. Checker, tools and team actions

- **tools/check_writing.py** is extended from the audit's check_writing_proposed.py.
  - It flags ":" and classifies each one as clock, URL, ratio, label or prose (all are counted). It also flags em and en dashes, "---", "--", ";", the minus sign, visible "https://" and "http://", the AI-sounding word list and the mechanical word list from the owner's request (whole words, case-insensitive), and gendered pronouns for the authors.
  - It reads the slides.pdf and poster.pdf text, the PDF title metadata, the slides.tex \note blocks, pres-note.md, poster-note.md, and the report docx (document.xml, footnotes, headers, footers and the core title). It skips runs in a monospace font and hyperlink targets.
  - It must end at 0 hits. Words inside app screenshots are product UI and are not checked.
- **timing.py** stays, with a target of 373 s.
- **crop_screenshots.py** gets the new crops from Alex's run.
- **sync_notes.py** regenerates the \note blocks from pres-note.md.
- **The docs/presentation README.** Update its line "no institution colours" for the UMB identity, and record the disagreements from section 9.
- **Team actions, which the build workers cannot do, listed in the README and the pitch notes.**
  1. Before the event, record a 30 to 40 s screen capture of a live run of Alex's sentence, as a backup at the poster table. It needs the team's own keys.
  2. Open the free live demo a minute before judging so it is awake.
  3. Scan both QR codes with a phone. If an access code is set on the live demo, give it at the stand, or put "?code=" in the QR address.
  4. Bring a laptop showing the app at the poster.

## 13. Critique and decisions

Three critics read the first draft in parallel on 26 October 2026, between 13.29 and 13.33 EDT: a non-technical visitor, a hackathon judge, and an expert in AI agents and responsible AI. Their main points and the decisions follow. The expert's file and line claims were spot-checked: demo_data.py has 8 cities including Detroit, sample rain never exceeds 50 percent (tools/__init__.py line 502) while T9 tests days at 60 percent or more, the critic never calls the model, and the AI is called in intake, research, feedback, guide and the composer's summary.

### What the critics found, and what changed

| # | Critic | Finding | Decision |
|---|---|---|---|
| 1 | Judge, expert | "Agents plan the trip" gives the AI credit for the planner's work, which is plain code. The draft also called the checker an AI helper, which undoes "Code checks the money". | **Changed the tagline** to "AI agents do the legwork. Code checks the money. You make the call." The three ideas are now three actors and what each decides. The six helpers are stated truthfully: four use the AI, the planner and the checker are plain code. |
| 2 | Expert, visitor | "Every price comes from a search" and "the total is always right" are false. $340 of the $780 is flat estimates, built-in sight prices are estimates, and unpriced events count as $0. | Idea 2a now names live prices and labelled estimates, and says "exact for the prices shown". Added to section 11. |
| 3 | Visitor | The story stops at the question, so there is no ending. | **Added a tested ending.** T16 replays Alex's exact sentence. When the budget is raised, the plan is rebuilt, checked and fits. It is labelled as coming from a test with sample prices, and only that path is claimed. A new live run was not made, because the build may not make paid calls. |
| 4 | Visitor | The poster's column 3 crops (05_revised, 06_approved) show a different trip to New York. | All story crops now come from Alex's run (the quick-reply buttons, the plan notes, the Approve button and badge). The New York screens appear only in the report, captioned "another trip, New York". |
| 5 | Visitor | "Agents" sounds like travel agents. | "An agent here is an AI helper with one job" goes under the tagline on slide 1, slide 3 and the poster header. Slide 9 says "a travel agency". |
| 6 | Judge, expert | The 12, 4, 7 grouping looks curated, and T10 and T13 were misplaced. | **Dropped the regrouping.** The deck shows the results file's own five groups in plain names, each with an idea mark and one example per idea. |
| 7 | Expert | The caveats were incomplete. The AI runs used the same sample prices and weather. "Same result every time" is overstated. T9 passes without the rain rule firing. T13 does not test the download. | All added to slide 7's spoken gist, report 5.1 and 5.5, and section 11, with the wording fixed. |
| 8 | Judge | The deck never shows what the AI adds, since demo mode passes everything without it. | Slide 7 says the AI understood "first weekend of December" where the rules did not (T18). Slide 4 shows the step list where the AI chose its searches. |
| 9 | Judge | The slide 5 chart contradicts a title about cutting, since the price rises once and stays flat twice. | New title "Code adds up every price and tries five fixes, from $1,235 to $780", plus the line "Not every fix saves money, so code checks the total after each one". |
| 10 | Judge | 395 s is too tight once handovers are counted. | The plan is now 373 s (slide 3 down to 20 s, slide 11 to 24 s, slides 4 to 9 trimmed). |
| 11 | Judge | Source [4] is a vendor review, which breaks the "in its own words" rule. | Planner apps are described from their own sites with the date accessed if web access is available, otherwise from [4] labelled "a review". Roameo's difference is stated as its own design: "treats your budget as a limit, not a wish". |
| 12 | Judge | "Free" mixes up demo mode and live prices. | The wording now separates the free demo (sample prices, 8 cities) from a shared live link (about 80 plans a month on the free search plan). The first group named is student clubs, and the pilot says what it will measure. |
| 13 | Judge | Reorganising report section 2 risks breaking the template and loses depth. | **Kept all six section 2 headings** as the template has them, with only the 2.6 colon removed. The ideas come in through an idea column and the 2.1 opening. File paths in monospace are allowed in 2.2 and section 6 for depth. The builder must check page settings, numbering and the contents list. |
| 14 | Expert | The privacy statements were too vague. The draft's "nothing is stored" was risky. AI-written text is not fully grounded. | Section 10 now lists 15 checked statements with file and line numbers, including what can be wrong. "Nothing is logged" and "no data leaves your computer" are banned. |
| 15 | Expert | Demo mode has 8 cities, not 7. The rate limit counts an address the client reports, not a person, and the access code is off unless set. | 8 cities everywhere, recorded as a README disagreement. "60 requests per address per hour", with "optional access code". |
| 16 | Expert | "An AI can add wrongly" is fair but weak. | The reason given first is that the total is checked again after every change (six times for Alex), and code gives the same exact sum every time and can be tested. |
| 17 | Visitor | Titles are too long, and jargon remains (keys, Render, idle, runs, a vendor review). | Titles shortened. "No sign-ups or paid accounts" replaces keys. Render is off the slides. "Fix" is the one word for repairs. |
| 18 | Visitor | The community benefit reads like server settings. | Uses the visitor's own two sentences (the club of four, the class reading the code). |
| 19 | Visitor | A visitor wants to know if it is free, how to book, and whether their data is safe. | Slide 8's supporting line and the poster's middle block answer all three. |
| 20 | Judge | There is no demo. The QR code may hit the access code. | There is no demo slot in 7 minutes. Team actions in section 12 cover a recorded backup, waking the demo, testing the QR and a laptop at the poster. |

### Advice not taken

- **Add new checks to the tests** ("the total equals the sum", "each price matches a search result"). Not taken, because the build may not change app code, and backend/eval is app code. Section 11 instead says no test checks the sum on its own. The report lists this check as a possible improvement in 5.7.
- **Replace slides 4 to 6 with a sped-up screen recording.** Not taken, because a live recording needs the team's keys and paid calls, and a demo-mode recording would show different numbers from Alex's live run. It is listed as a team action, as a backup at the poster table.
- **One dated try of Alex's sentence in a general chat assistant, as a backup.** Not taken, because one try would be read as a test of a competitor, which section 11 forbids.

### Final decisions

1. The core story is Alex, a made-up student, on one real live run, plus one tested ending.
2. The tagline is "AI agents do the legwork. Code checks the money. You make the call." The three ideas are three actors, each with three parts.
3. The deck has 11 slides planned at 373 s, and six untimed backups.
4. The poster has a navy UMB header, the Alex strip, three idea columns and a bottom band of three blocks.
5. The report is rebuilt with python-docx from a text source, keeps the team's styles and section 2 headings, and adds a one-page summary, 7.3, 7.4, 8 Conclusion and Acknowledgements. The original is kept as docs/Roameo_Project_Report.original.docx.
6. The evaluation uses the results file's own groups, and its caveats are full and honest.
7. The privacy and data-flow statements are only those in section 10.
8. The checker is extended to cover colons, both word lists and the report, and must end at 0 hits.
9. The owner should confirm one open item: the reversal of the earlier "no institution names or logos" rule. This plan follows the newer UMass Boston identity request.
