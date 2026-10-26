"""The text of the revised project report, read by build_report.py.

Each block is a tuple. ("h1", text), ("h2", text), ("h3", text), ("p", text), ("bullets", [..]),
("numbers", [..]), ("code", [..]), ("figure", file, caption[, max width, max height]),
("table", dict(widths, header, rows, caption)), ("pagebreak",), ("contents",), ("title", dict).
Inline marks are **bold**, `code` (monospace, for file paths and command lines only) and
[shown text](link target). A table row that is a plain string is a group row across the table.

The writing rules apply to every visible word here. No dashes, no semicolons, no colons, web
addresses shown without the scheme, plain words, and no code names outside monospace.
"""

DOC_TITLE = "Roameo project report"
DOC_SUBJECT = "PEAAII AI Applications Hackathon 2026, Agentic AI"
NOT_IN_CONTENTS: set[str] = set()

DEMO = "https://roameo-l13h.onrender.com/"
CODE = "https://github.com/TinyZhen/Travel_Agent"

TITLE = {
    "lines": [
        ("PEAAII AI Applications Hackathon 2026, Agentic AI", 12, True, "umb", 10),
        ("Roameo", 40, True, "navy", 4),
        ("AI agents do the legwork. Code checks the money. You make the call.", 16, False, "ink", 6),
        ("An agent here is an AI helper with one job.", 11, False, "grey", 40),
        ("Team Roameo", 12, True, "ink", 2),
        ("Zhen Lu and Noctis Zhang", 12, False, "ink", 2),
        ("Department of Computer Science, University of Massachusetts Boston", 11, False, "grey", 28),
        (f"Try it at [roameo-l13h.onrender.com]({DEMO})", 11, False, "ink", 2),
        (f"Code at [github.com/TinyZhen/Travel_Agent]({CODE})", 11, False, "ink", 2),
        ("October 2026", 11, False, "ink", 0),
    ]
}

Q = "“"   # opening quotation mark
E = "”"   # closing quotation mark
A = "’"   # apostrophe

BLOCKS = [
    ("title", TITLE),
    ("pagebreak",),

    # ------------------------------------------------------------------ one page
    ("h1", "Roameo in one page"),
    ("p", "Roameo is a trip planner for students and budget travelers. You type one sentence. AI "
          "helpers ask what is missing and run the searches, plain code adds up every price, and when "
          "the money does not work, Roameo stops and asks you. It never books or pays."),
    ("numbers", [
        f"**Alex types one sentence.** Alex is a Boston student we made up. The run is real, with live "
        f"prices and the AI on. Alex types {Q}Chicago for 4 days, budget $600{E}.",
        f"**Roameo asks** where from and when. Alex answers {Q}From Boston, leaving Nov 20{E}.",
        "**The AI helpers search.** They compare 8 flights, 18 hotels and 59 events. Past years" + A +
        " weather says cold and likely rain, so they also look for indoor places.",
        "**Code adds up the money.** The first plan costs $1,235. Five fixes bring it to $780, still "
        "$180 over.",
        f"**Roameo stops and asks.** {Q}Would you like to raise the budget, shorten to 2 nights, or drive "
        f"instead of flying?{E}",
        f"**Alex decides.** Our tests replay Alex{A}s sentence with sample prices. When the budget is "
        "raised, the plan is rebuilt, checked and fits. Alex says OK, gets a calendar file and books on a "
        "site Alex trusts.",
    ]),
    ("table", dict(
        widths=[1.55, 1.65, 1.65, 1.65],
        header=["Idea", "Part one", "Part two", "Part three"],
        rows=[
            ["1. AI agents do the legwork", "They read your sentence and ask for what is missing",
             "They choose which searches the trip needs", "They turn your plain words into changes"],
            ["2. Code checks the money", "Code adds up every total",
             "Code tries one fix at a time, at most five", "Code shows the gap and never hides it"],
            ["3. You make the call", "You choose how to close the gap",
             "You see every step and every assumption",
             "Nothing is final until you say OK, and you book it yourself"],
        ],
        caption="The three ideas of Roameo. Each idea is one actor and what that actor decides.",
        bold_first_col=True)),
    ("p", "**What is new.** A chat reply can tell you a plan fits your budget with nobody checking the "
          "sum. In Roameo, AI agents do the searching, plain code adds up every total, and when the "
          "money does not work it stops and asks you. Roameo treats your budget as a limit, not a wish."),
    ("p", "**The headline result.** All 23 core tests pass in demo mode and with the AI on, and every "
          "core test passed in each of the 3 runs with the AI (section 5)."),
    ("pagebreak",),
    ("contents",),
    ("pagebreak",),

    # ------------------------------------------------------------------ 1
    ("h1", "1. Project Overview"),
    ("h2", "1.1 Project title"),
    ("p", "Roameo, a multi-agent trip planner that researches, budgets and revises a short trip, and "
          "only finalizes it when the traveler approves."),
    ("h2", "1.2 Team members"),
    ("table", dict(
        widths=[1.6, 2.4, 2.5],
        header=["Name", "Major and department", "Main contribution"],
        rows=[["Zhen Lu", "Computer Science, UMass Boston", "Agent framework and backend"],
              ["Noctis Zhang", "Computer Science, UMass Boston", "Market research"]],
        caption="Team Roameo, Department of Computer Science, University of Massachusetts Boston.")),
    ("h2", "1.3 Problem statement"),
    ("p", f"**Question 1, what problem do we solve?** Planning even a short trip is a scattered chore. In "
          f"Expedia{A}s 2023 Path to Purchase study, travelers spent about 303 minutes with travel content "
          "in the 45 days before booking, and US travelers spent 524 minutes viewing an average of 277 "
          "pages [1]. The hard part is not finding information but combining it. The flight has to match "
          "the hotel dates, the total has to stay under the budget, the sights have to fit around events "
          "and weather, and all of it has to be redone when one piece changes."),
    ("p", "Take Alex, who has $600 for four days in Chicago. Flights, a hotel, sights, food and transit "
          "all have to add up, and again after every change. A general chat assistant can suggest an "
          "itinerary, but it adds the prices up itself, so it can say a plan fits with nobody checking the "
          f"sum. Fully automatic booking goes to the other extreme. Booking.com{A}s 2025 Global AI "
          "Sentiment Report (more than 37,000 people in 33 markets) found that 89% of travelers want AI "
          "help planning trips, but only 12% are comfortable with AI deciding on its own [2]."),
    ("p", "**In one sentence.** Travelers on a budget want AI to do the tedious research and arithmetic, "
          "but they do not want to hand over the final decision."),
    ("h2", "1.4 Target users"),
    ("p", "**Question 3, who is the target market?** Three groups."),
    ("bullets", [
        "**Students on short trips.** College students and young professionals, roughly 18 to 30, in a "
        "city like Boston, taking trips of 1 to 4 nights by plane or car, with a hard budget and little "
        "planning time.",
        "**Budget travelers.** Anyone for whom the total matters more than the name of the hotel.",
        "**Small groups who split the cost.** Friends, clubs and families, where the cost per person and "
        "the number of rooms matter.",
    ]),
    ("p", "They want to stay within budget, get a realistic plan for each day, see why each choice was "
          "made, and change the plan in plain words. The first group we want to reach is student clubs. We give "
          "no market size, only the cited survey figures in section 7."),
    ("h2", "1.5 Proposed solution"),
    ("p", "**Question 4, how does it work?** Roameo rests on three ideas, each one actor and what it "
          "decides (Figure 1)."),
    ("figure", "fig_ideas.png", f"The three ideas, with one fact from Alex{A}s run under each."),
    ("p", "**1. AI agents do the legwork.** An agent here is an AI helper with one job. The request "
          "reader turns your sentence into a city, dates, a budget and interests, and asks for anything "
          "missing. It never guesses where you leave from or when, because a guessed city or date gives a "
          f"useless plan. It assumes one traveler if you do not say, and shows it ({Q}Assumed 1 "
          f"traveler{E}). The researcher chooses the searches. For Alex it compared 8 flights, 18 hotels "
          "and 59 events, and because the weather looked cold it also searched for indoor places, holiday "
          f"markets and ice skating. The change reader turns words like {Q}make it cheaper{E} or {Q}more "
          f"museums{E} into edits, so the plan is revised, not rebuilt. With the AI on, the guide writes a "
          "visit guide for each stop."),
    ("p", f"**2. Code checks the money.** The planner and the checker are plain code. In Alex{A}s plan, "
          "the flight ($278) and hotel ($162) came from live searches, and food ($280) and local transit "
          "($60) are flat daily estimates, labeled as such. Code adds them to $780, exact for the prices "
          "shown. When the plan is over budget, the checker applies one fix, the planner rebuilds, and the "
          "checker looks again, at most five times. When it still does not fit, code shows the gap. Why "
          "code and not the AI? The total is checked again after every change, six times for Alex. Code "
          "gives the same exact sum every time and can be tested. An AI model can answer differently "
          "from run to run."),
    ("p", "**3. You make the call.** When the plan does not fit, Roameo offers to raise the budget, "
          f"shorten the stay or drive, and waits. The {Q}What the agents did{E} list shows every step (25 "
          "for Alex), and the plan shows every assumption and which prices are estimates. Saying OK only "
          "lets you download a calendar file. Roameo never books or pays, because paying is a decision a person "
          "should make, on a site they trust."),
    ("h2", "1.6 Why agentic AI is appropriate"),
    ("table", dict(
        widths=[1.9, 4.6],
        header=["What makes it agentic", "Where it appears in Roameo"],
        rows=[
            ["Understanding a goal", "Free text becomes a trip. It asks when the origin or date is missing "
             "and shows its other assumptions."],
            ["Planning several steps", "Search, plan, check, fix, then revise after feedback."],
            ["Using outside tools", "Five kinds of search, for flights, hotels, events, attractions and "
             "weather."],
            ["Deciding from what it finds", "The checker picks the next fix from the priced plan. Rainy or "
             "cold days put indoor stops first."],
            ["Helpers working together", "Six helpers share one trip record, passed between them by a "
             "coordinator in plain code."],
            ["Asking a person when needed", "Before planning, when facts are missing. Before finishing, for "
             "approval or a budget trade-off."],
            ["Checking its own result", f"Each fix is checked again, and {Q}cheaper{E} must really lower "
             "the price."],
        ],
        caption="Where agentic AI shows up in Roameo.",
        bold_first_col=True)),

    # ------------------------------------------------------------------ 2
    ("h1", "2. Agentic AI Design"),
    ("h2", "2.1 Overall workflow"),
    ("p", "The three ideas divide the work. AI helpers decide what you meant, what to ask and which "
          "searches to run. Plain code decides prices, totals and fixes. You decide the gap and give the "
          "final OK (Figure 2)."),
    ("figure", "fig_workflow.png", "How Roameo works inside. Four helpers use the AI model. The planner, "
               "the checker and the coordinator are plain code. Two decisions belong to you."),
    ("p", "The coordinator is plain code that tracks where each conversation stands. A new request goes "
          "to the request reader, and a message during review goes to the change reader. A plan counts as "
          "approved only after you approve it. In demo mode, simple rules stand in for the AI everywhere."),
    ("h2", "2.2 Agent responsibilities"),
    ("table", dict(
        widths=[1.3, 1.05, 2.2, 1.55, 0.4],
        header=["Helper and file", "AI or code", "What it decides, and from what", "When something goes wrong", "Idea"],
        rows=[
            [["Request reader", "`intake.py`"], "AI model, rules in demo mode",
             "The trip from your sentence (city, dates, nights, travelers, budget, interests, transport) and "
             "what must be asked.",
             "Rules take over if the AI fails. Trip facts change later only if your words state them.", "1"],
            [["Researcher", "`research.py`"], "AI model",
             "Which searches to run, with what details, from the trip.",
             "Stops after 8 steps. Needed searches run even if the AI skipped them.", "1"],
            [["Planner", "`composer.py`"], "Plain code, the AI writes only the summary",
             "The flight, the hotel, each day with travel times and meals, and every price, from the search "
             "results and your limits.",
             "No AI in the sums. The summary may use only the computed facts.", "2"],
            [["Checker", "`critic.py`"], "Plain code",
             "Over budget, missing flight or hotel, wrong dates, repeats, outdoor stops on rainy days, and "
             "the one next fix, from the priced plan.", "After five fixes it stops and asks you.", "2"],
            [["Change reader", "`feedback.py`"], "AI model and word rules",
             "Edits from your reply (more museums, slower pace, skip a place, cheaper, another hotel).",
             f"A vague request gets a question. A higher budget wins over {Q}cheaper{E}.", "1"],
            [["Guide", "`guide.py`"], "AI model and a web search",
             "A visit guide for each stop of the plan. Museum exhibitions only from search results, with "
             "links.",
             "Code drops exhibitions whose link is not in the results.", "1"],
            [["Coordinator", "`orchestrator.py`"], "Plain code",
             "Sends each message to the right helper, runs the fix loop, keeps revisions small, asks you.",
             "Keeps existing stops first, restores the plan if nothing fits.", "3"],
        ],
        caption="The six helpers and the coordinator. Their files are in `backend/agents/`, shown in "
                "monospace for readers who want the code.")),
    ("h2", "2.3 Tools and external resources"),
    ("table", dict(
        widths=[1.0, 3.4, 2.1],
        header=["Search", "Live source", "In demo mode"],
        rows=[
            ["Flights", "Google Flights through SerpApi, round trip. Any city gets its nearest major airport. "
             "At most 8 flights are kept.", "Sample fares from real city distances, labeled."],
            ["Hotels", "Google Hotels through SerpApi, within 12 km of the center, in price levels.",
             "Five price levels per city, labeled."],
            ["Attractions", "A curated list for the built-in cities (prices marked est.), Google Maps through "
             "SerpApi for other cities and targeted searches.", "The curated list."],
            ["Events", "Google Events through SerpApi (about the next 10 days), then Ticketmaster if a key "
             "is set. With no real events, the plan shows none.", "Weekly sample events, labeled."],
            ["Weather", "Open-Meteo forecast for 15 days, then what the same dates were like in 2023 to "
             "2025, with sunset times.", "A labeled climate estimate."],
        ],
        caption="The five kinds of search.",
        bold_first_col=True)),
    ("p", "**A provider can disappear.** Our first prototype used Amadeus Self-Service, which closed on "
          "July 17, 2026 [8]. Because every search already tried the live source and otherwise used "
          "labeled sample data, the app kept working and we only swapped the provider. A real product would keep at least two sources for each kind of data. "
          "Whenever any result is sample data, the app shows a demo mode badge, so sample prices are never shown as live "
          "quotes."),
    ("h2", "2.4 Context and information required"),
    ("bullets", [
        "**From the traveler.** Destination, start date and origin are required, and Roameo asks for any "
        "that is missing. Nights, travelers, budget, interests and transport are optional, with defaults "
        "shown as assumptions.",
        "**Conversation memory.** The trip, search results, places or hotels to leave out, the plan and "
        "the list of steps.",
        f"**System context.** Today{A}s date, to read {Q}next weekend{E} and reject past dates, and the "
        "city list with airport codes.",
    ]),
    ("h2", "2.5 Human-in-the-loop decisions"),
    ("table", dict(
        widths=[2.4, 1.7, 2.4],
        header=["Decision", "Who decides", "Why"],
        rows=[
            ["A missing destination, origin or date", "You", "A guessed city or date gives a useless plan."],
            ["Defaults (nights, travelers)", "Roameo, shown as assumptions", "Low risk, easy to correct."],
            ["Which searches to run", "The AI helpers", "Routine research."],
            ["Small cost fixes", "Plain code, listed in the steps", "Easy to undo, in service of your budget."],
            ["Go over budget, shorten the trip or drive", "You", "Trade-offs that change what you get."],
            ["Approve and download the calendar file", "You", "AI support, not AI control [2]."],
            ["Book or pay", "Never automated", "You book on a site you trust."],
        ],
        caption="Who decides what.")),
    ("p", f"One honest detail. A plan is approved with the Approve button or a reply starting with words "
          f"such as {Q}approve{E} or {Q}looks good{E}, and with the AI on, the change reader may read other "
          "replies as approval too. Either way, the calendar file downloads only after approval."),
    ("h2", "2.6 Architecture choice, why six agents and not more"),
    ("p", "We considered one agent per search (flights, hotels and so on) and rejected it. Those are calls "
          "to a service, not decisions, so splitting them adds hand-offs without judgment. Each of the six "
          "helpers makes a different kind of decision. We also avoided one large prompt, because a narrow "
          "job is easier to check in code, and we kept all money arithmetic out of the AI model, because a "
          "language model should not be trusted to add up a budget."),
    ("p", "Code also keeps each AI step in bounds. Activities must come from an allowed list. A trip fact "
          "such as the dates or the budget changes in the middle of a conversation only when your own "
          "words state it. Searches the plan cannot do without are run even if the AI skipped them, and "
          "the researcher stops after 8 steps."),

    # ------------------------------------------------------------------ 3
    ("h1", "3. Working Prototype"),
    ("p", f"The code is at [github.com/TinyZhen/Travel_Agent]({CODE}) on the main branch, and a live demo "
          f"runs at [roameo-l13h.onrender.com]({DEMO}). It is a FastAPI backend in Python with a React and "
          "Tailwind frontend, in two modes."),
    ("bullets", [
        "**Demo mode.** Practice runs with sample prices instead of live ones, so anyone can try it "
        "without sign-ups or paid accounts. Simple rules replace the AI, with labeled sample data for 8 "
        "cities. It starts on a laptop in about three minutes.",
        "**Live mode.** An OpenRouter key turns on the AI helpers, and a SerpApi key turns on live Google "
        "Flights, Hotels, Maps and Events. Each search goes live on its own, and every flight and hotel "
        "card links to its source.",
    ]),
    ("figure", "alex_plan.png", f"Alex{A}s plan in the app, from one live run, with the budget bar, the "
               "cost line, the flight and hotel cards and the route map."),

    # ------------------------------------------------------------------ 4
    ("h1", "4. Demo"),
    ("p", f"The 7-minute talk has no live demo slot, so the slides walk through Alex{A}s real run, one "
          "scene per idea. At the poster, the team shows the app on a laptop, with a short recording of a "
          "live run as a backup."),
    ("h3", "Scene 1. AI agents do the legwork"),
    ("p", f"Alex types {Q}Chicago for 4 days, budget $600{E}. Roameo asks where from and when (Figure 4). "
          "Then the researcher picks its searches, 8 flights, 18 hotels, 59 events and the weather, plus "
          "indoor places, holiday markets and ice skating because the trip looks cold (Figure 5)."),
    ("figure", "alex_chat.png", f"Roameo asks before it plans. Alex{A}s run.", 4.5, 3.0),
    ("figure", "alex_steps_research.png", f"The first steps of {Q}What the agents did{E} in Alex{A}s run."),
    ("h3", "Scene 2. Code checks the money"),
    ("p", "The first plan costs $1,235. A cheaper hotel brings it to $984. The cheapest flight changes "
          "nothing. Dropping paid events raises it to $1,014, because each fix rebuilds the plan. Free "
          f"sights plus the two that best match Alex{A}s interests bring it to $780, and indoor stops for "
          "the rainy day keep it there (Figure 6). $780 is the cheapest plan built in five fixes, not the "
          "cheapest trip possible. The app shows the gap in red (Figure 7)."),
    ("figure", "fig_price.png", f"The plan total after each fix in Alex{A}s run. One live run."),
    ("figure", "alex_budget.png", "The budget bar and the cost line. Flight and hotel are live prices, "
               "food and transit are estimates."),
    ("h3", "Scene 3. You make the call"),
    ("p", f"Still $180 over, Roameo stops and asks Alex to choose (Figure 8). Our tests replay Alex{A}s "
          "sentence with sample prices, and when the budget is raised, the plan is rebuilt, checked and "
          "fits. Only that path is tested. Alex can read all 25 steps in the list before deciding. Saying OK "
          "only lets Alex download a calendar file, and Alex books on a site Alex trusts."),
    ("figure", "alex_question.png", f"The question at the end of Alex{A}s run.", 4.0, 3.2),
    ("h3", "Other trips"),
    ("p", "With the AI on, each stop gets a visit guide, and museum exhibitions come only from a web "
          f"search, with links (Figure 9). For {Q}Michigan on December 22{E}, Roameo asked which city, "
          "used past years" + A + " weather and put indoor stops first (Figure 10)."),
    ("figure", "guide_crop.png", "A visit guide from another trip, New York, with what not to miss and how "
               "to spend the 90 minutes. Written by the AI and labeled so in the app."),
    ("figure", "detroit_crop.png", "Another trip, Detroit in late December.", 4.5, 3.6),

    # ------------------------------------------------------------------ 5
    ("h1", "5. Evaluation"),
    ("h2", "5.1 Method"),
    ("p", "**What a test is.** A conversation we wrote in advance, typed into Roameo by a script, with "
          "code that checks the answer. For example, that it asks for a missing date, that the total stays "
          "within the budget, or that it reports the gap instead of hiding it. A test passes when every "
          "check comes out right, and it fails if even one check is wrong. We wrote 25 tests, 23 core tests "
          "and 2 known limits that we expect to be imperfect and report anyway. The same conversations "
          "also run as automated tests in the code, next to tests of the web interface such as "
          f"{Q}no calendar file before approval{E}."),
    ("p", "**Two modes and 3 runs.** We ran every test in demo mode, where rules stand in for the AI, and "
          "with the AI on (Claude Haiku 5.5 through OpenRouter). The AI can answer differently each time, "
          "so we ran the AI tests three times. Demo mode gives the same answer every time by design. Both "
          "modes used the same sample prices and weather, so the AI runs test how the AI reads requests "
          "and picks searches, not live data."),
    ("p", "**Results.** Demo mode passed 23 of 23 core tests (51 of 51 checks). With the AI on, 23 of 23 "
          "passed (51 of 51 checks), and every core test passed in each of the 3 runs. On the 2 known "
          f"limits, demo mode did as we would like in 1 and the AI in both, because only the AI read {Q}first "
          f"weekend of December{E} (Figure 11)."),
    ("figure", "fig_results.png", "Core tests passed per group, and the 2 known limits.", 6.5, 3.6),
    ("h2", "5.2 Test cases, expected and actual"),
    ("p", "Tests appear in the results file" + A + "s own groups. The idea column gives the main idea "
          "each test checks. Pass in the AI column means all 3 runs passed. Totals are from demo mode."),
    ("table", dict(
        widths=[0.42, 1.75, 0.4, 2.13, 1.0, 0.4, 0.4],
        header=["Test", "What it tries", "Idea", "Expected", "What happened", "Demo", "AI"],
        rows=[
            "Human-in-the-loop (10)",
            ["T2", "Missing date", "1", "Asks for a date, then plans from Nov 20.", "$1,749", "Pass", "Pass"],
            ["T3", "Missing destination", "1", "Asks where to go, invents nothing.", "Asked", "Pass", "Pass"],
            ["T6", "A $300 budget that cannot work", "2", "Tries fixes, then asks to raise, shorten or drive.",
             "$778, $478 over, asked", "Pass", "Pass"],
            ["T10", f"{Q}Cheaper{E}", "1", "The new total is lower.", "$718", "Pass", "Pass"],
            ["T11", f"{Q}Different hotel{E}", "1", "A new hotel, the old one not offered again.", "$999",
             "Pass", "Pass"],
            ["T12", "Skip a named place", "1", "The Ferry Building is removed.", "$2,034", "Pass", "Pass"],
            ["T16", "Raise the budget after Roameo asks", "3", "The plan fits, the question goes away.",
             "$1,032", "Pass", "Pass"],
            ["T19", "No origin", "1", "Asks where from, reads the answer as the origin.", "$830", "Pass", "Pass"],
            ["T21", f"{Q}More museums{E}", "1", "Revises, keeps most of the plan, reports changes.", "$1,049",
             "Pass", "Pass"],
            ["T22", f"{Q}Slower pace{E}", "1", "Fewer sights per day, later starts.", "$1,719", "Pass", "Pass"],
            "Failure handling (4)",
            ["T4", "Unknown city", "1", "Says it cannot find it and asks.", "Asked", "Pass", "Pass"],
            ["T5", "A past date", "1", "Says the date is past and asks again.", "Asked", "Pass", "Pass"],
            ["T15", "Vague feedback", "1", "No change, explains what it can change.", "$1,095", "Pass", "Pass"],
            ["T23", "A state, not a city", "1", "Asks which city in Michigan, then plans Detroit.", "$949",
             "Pass", "Pass"],
            "Real-world adaptation (4)",
            ["T9", "Rainy day", "1", "Days with 60 percent rain or more start indoors.", "Rule unused, see 5.5",
             "Pass", "Pass"],
            ["T20", "Cutting cost, museum lover", "2", "Cuts cost but keeps a museum.", "$561", "Pass", "Pass"],
            ["T24", "Winter trip", "1", "At most one outdoor stop on cold days, a warning.", "$966", "Pass", "Pass"],
            ["T25", "Seasonal closure", "1", "No river cruise in January.", "$1,323", "Pass", "Pass"],
            "Functional (3) and Functional / E2E (1)",
            ["T1", "A complete request", "2", "A priced plan within $1,500, all 5 searches, no questions.",
             "$1,350", "Pass", "Pass"],
            ["T7", "Driving", "1", "No flight search, gas and parking in the costs.", "$1,153", "Pass", "Pass"],
            ["T8", "A local day trip", "1", "No flight, no hotel.", "$138", "Pass", "Pass"],
            ["T14", "A group of 4", "2", "2 hotel rooms, family places first.", "$3,556", "Pass", "Pass"],
            "Safety / oversight (1)",
            ["T13", "Approval", "3", "Approved only after you approve.", "Approved", "Pass", "Pass"],
            "Known limitation, not in the 23 (2)",
            ["T17", "A city outside the demo data", "1", "In demo mode it asks which city.", "Asked", "Pass", "Pass"],
            ["T18", f"{Q}First weekend of December{E}", "1", "The AI should read it as Dec 4.",
             "Demo asked", "Limit", "Pass"],
        ],
        caption="All 25 tests in the results files" + A + " own groups.")),
    ("h2", "5.3 What went well"),
    ("bullets", [
        "It never invents a destination, an origin or a date. Missing or wrong inputs lead to a question.",
        "The budget is checked by arithmetic, not by the AI. If a plan still does not fit, the gap is "
        "reported, not hidden.",
        "The searches fit the trip, with no flight search for a road trip and no hotel for a day trip.",
        f"Feedback is checked. {Q}Cheaper{E} must lower the total, and a rejected hotel never returns.",
        "Demo mode passes every core test without the AI, so the AI" + A + "s value shows in what rules "
        f"cannot read, such as {Q}first weekend of December{E}.",
    ]),
    ("h2", "5.4 Failure cases found during development"),
    ("p", "Writing and running the tests found real bugs, which we fixed. The table keeps five lessons. "
          "Numbers not in the results files come from the team" + A + "s development notes."),
    ("table", dict(
        widths=[1.8, 2.5, 2.2],
        header=["What went wrong", "Why", "What we changed"],
        rows=[
            [f"{Q}Cheaper{E} made the trip cost more", "Freed time was filled by a pricier sight ($1,182 became "
             "$1,192).", "A hard target below the last total."],
            ["The AI dropped past dates (0 of 3 runs)", "The prompt said dates are never in the past.",
             "The AI copies dates, code checks them. Now 3 of 3."],
            ["It assumed you live in Boston", f"A tester said {Q}I never said I{A}m in Boston.{E}",
             "The origin is now a required question."],
            ["Cutting cost removed every museum", "The last fix dropped every paid sight.",
             "Keep the two paid sights that best match your interests."],
            [f"{Q}4 days{E} became 4 nights with the AI", "No test checked it. We saw it in a screenshot.",
             "A prompt rule and a new check."],
        ],
        caption="Five lessons from development.",
        bold_first_col=True)),
    ("h2", "5.5 Limitations"),
    ("p", "**Caveats about the tests.** We wrote the tests ourselves. Both modes used sample prices and "
          "weather. Three runs is a small sample, it does not mean the AI answers the same every time, and "
          "only the first run" + A + "s details are saved. No test checks on its own that the total equals "
          "the sum of its parts. The rainy-day test passes without its rule being used, because sample "
          "rain never goes above 50 percent and the rule starts at 60. The rule did run in Alex" + A + "s "
          "live run. The approval test checks approval, not the calendar download, which other tests "
          "cover. There was no user study, so we claim nothing about time saved or plan quality."),
    ("p", "**Limits of the app.** Demo mode covers 8 cities. Food and local transit are flat estimates "
          f"($340 of Alex{A}s $780), built-in admission prices are estimates, and unpriced events count as "
          "$0. Google Events covers only about 10 days ahead, so later trips use Ticketmaster when a key "
          "is set. The demo rules miss complex date phrases and ask instead. Visit guide tips are written by the AI and "
          "can be wrong or out of date. Live prices use the free SerpApi plan, about 80 plans a month. "
          "Trips live in server memory, with no accounts."),
    ("p", "**Disagreements we found.** The results files and the code win. The README says 18 scenarios "
          "(the results have 25), 7 demo cities (the data has 8, with Detroit), 16 forecast days (the code "
          "uses 15), 7 agents (there are 6 helpers and a coordinator), and airport codes only for built-in "
          "cities (the code finds the nearest airport for any city, and the Paris test" + A + "s written "
          "expectation is out of date too). The results files do not name the model. Our first draft said "
          "Roameo assumes the origin, and gave New York live numbers that are in no repository file."),
    ("h2", "5.6 Live-data check"),
    ("p", "Live prices change constantly, so we checked live mode with real runs. In Alex" + A + "s run, "
          "saved as a screenshot, Roameo compared 8 real flights, 18 hotels and 59 Ticketmaster events, "
          "used past years" + A + " weather (a 67 percent chance of rain), and reached $780 with a live "
          "fare of $278 and a live hotel at $54 a night. The first plan had cost $1,235. It reported $180 "
          "over and offered to raise the budget, shorten to 2 nights or drive. That is the behavior we "
          "designed for, real prices, honest arithmetic and a person making the trade-off. It is one run, "
          "not a measurement."),
    ("h2", "5.7 Possible improvements"),
    ("bullets", [
        "More AI runs per test (for example 10) and harder inputs, such as typos and conflicting limits.",
        "A check that the total equals the sum of its parts, and a rainy-day test that uses the rule.",
        "A test with 5 to 10 students, measuring overspend and time to a plan they accept.",
        "Trips to several cities, and links to booking sites with the person still the one who books.",
    ]),

    # ------------------------------------------------------------------ 6
    ("h1", "6. Project Documentation"),
    ("h2", "6.1 What was built"),
    ("p", "A web app with a chat panel, a plan panel (budget bar, cost line, flight and hotel cards, a "
          "timed plan for each day, and a map of each day" + A + f"s route) and the {Q}What the agents "
          f"did{E} panel. Every stop links out, sights to their page or Google Maps, events to their ticket "
          "page and meals to restaurants nearby. The backend has six helpers and a coordinator, visit "
          "guides, five kinds of search with live and sample versions, the scripted tests and unit tests."),
    ("h2", "6.2 How to run it"),
    ("p", "From the repository root, in two terminals."),
    ("code", [
        "cd backend && python3 -m venv venv && source venv/bin/activate",
        "pip install -r requirements.txt && uvicorn app:app --port 8000",
        "cd frontend && npm install && npm run dev      # open http://localhost:5173",
        "cd backend && ROAMEO_OFFLINE=1 ROAMEO_FORCE_DEMO=1 pytest -q",
    ]),
    ("p", "Optional keys go in `backend/.env` (see the README), `OPENROUTER_API_KEY` for the AI helpers "
          "and `SERPAPI_API_KEY` for live searches. Keys stay on the server. To share one link with a club, "
          "the repository has a Docker image and a Render blueprint (`render.yaml`). The free plan sleeps "
          "after 15 idle minutes. An optional access code and a limit of 60 requests per address per hour "
          "help the free quota last."),
    ("h2", "6.3 Major tools and technologies"),
    ("table", dict(
        widths=[1.4, 5.1],
        header=["Area", "Technology"],
        rows=[
            ["Backend", "Python 3, FastAPI, Pydantic"],
            ["AI model", "Claude Haiku 5.5 through OpenRouter, with the OpenAI-compatible SDK. It can be swapped for "
             "another OpenRouter model that can call tools."],
            ["Data services", "SerpApi (Google Flights, Hotels, Maps, Events and search), Ticketmaster "
             "Discovery, Open-Meteo, OpenStreetMap"],
            ["Frontend", "React 19, Vite, Tailwind CSS 4, Leaflet"],
            ["Quality", "pytest, the scripted tests, headless browser screenshots"],
            ["Development", "Git and GitHub. AI coding assistants helped write and review code, and the "
             "tests checked all behavior."],
        ],
        caption="Main tools and technologies.",
        bold_first_col=True)),
    ("h2", "6.4 Version history"),
    ("p", "The first prototype (July 2025) was a single agent built with the smolagents library that "
          "always ran four searches, with no checks and no approval. Its Amadeus searches stopped when "
          "Amadeus closed its portal in July 2026 [8]. The hackathon version (October 2026) added the "
          "helpers, the checker, the two moments where Roameo asks you, demo mode, the tests and the new "
          "interface. The history is on GitHub, on the main branch."),
    ("h2", "6.5 Responsible use of AI"),
    ("p", "**Question 5, responsible use of AI.** It follows the three ideas."),
    ("bullets", [
        "**The AI asks, and its jobs are narrow.** It never guesses where you leave from or when, and code "
        "checks what it returns.",
        "**Code shows its math and labels its data.** Totals come from code. Sample prices and estimates "
        "are always marked. With no real events found, the plan shows none.",
        "**You decide and you book.** Every step is listed, nothing is final until you say OK, and nothing "
        "is booked or paid.",
    ]),
    ("p", "**What goes where** (Figure 12). These statements were checked against the code."),
    ("figure", "fig_dataflow.png", "What goes where.", 6.5, 3.8),
    ("bullets", [
        "In AI mode, what you type, the trip details, the first six results of each search and the plan "
        "facts go to the AI model through OpenRouter. In demo mode, nothing goes to an AI model.",
        "The searches get the city, the dates and airport codes, not your sentence or your budget. The "
        "flight search gets one adult, and the hotel search at most 2 adults.",
        f"Google Maps gets {Q}top sights in{E} the city, plus any place you ask to add. Google Events gets "
        f"{Q}Events in{E} the city, Ticketmaster the city and a date window, and Open-Meteo coordinates "
        "and dates.",
        "For museums, the guide sends the place, city and month to a Google search, then to the AI model.",
        "Your browser loads the map and the street routes from OpenStreetMap.",
        "There are no accounts. Trips stay in server memory until it restarts. Addresses are kept for one "
        "hour for the request limit, and the access code, if one is set, is saved in your browser.",
        "Roameo writes no log of its own, but the web server" + A + "s standard access log records "
        "addresses and paths, not message text.",
        "API keys stay on the server. The calendar file downloads only after you approve.",
    ]),
    ("p", "**What can be wrong.** Nothing checks the summary the AI writes. Visit tips are written by the "
          "AI and labeled as such. For exhibitions only the link is checked, not the title or dates. Web "
          "text read by the guide could try to steer the AI."),

    # ------------------------------------------------------------------ 7
    ("h1", "7. Market Context"),
    ("h2", "7.1 Who it is for"),
    ("p", "**Question 3, the target market.** Students on short trips, budget travelers and small groups "
          "who split the cost (section 1.4). We start with students, the users we know best, and with "
          "student clubs, which plan shared trips and care about the cost per person. We give no market "
          "size. Three separate surveys report that about 10% (Qlik, US, summer 2025 [5]), 22% (Global "
          "Rescue, fall 2025 [6]) and 29% (Adobe, US [7]) of travelers use generative AI for trip "
          "planning. The gap between wanting AI help (89%) and letting AI decide alone (12%) [2] is the "
          "opening Roameo is designed for."),
    ("h2", "7.2 Direct and indirect competitors"),
    ("p", "**Question 2, who are the competitors?** We have not tested the other products. The table says "
          "what each is for, with a source where we have one, and where Roameo" + A + "s design differs."),
    ("table", dict(
        widths=[1.6, 2.6, 2.3],
        header=["Competitor", "What it is for", "Where Roameo differs"],
        rows=[
            "Direct",
            ["Chat assistants such as ChatGPT and Gemini", "Open conversation, including trip ideas.",
             "Totals in code, and it asks when the plan does not fit."],
            ["Expedia" + A + "s Romie", "An AI assistant inside Expedia (May 2024) for planning, shopping "
             "and booking [3].", "Not a booking site. You book wherever you like."],
            ["Trip planner apps such as Mindtrip, Layla and Wonderplan", "AI trip planners for inspiration "
             "and itineraries, some adding booking, per a vendor review [4].", "Built for short trips on a "
             "hard budget, with every step shown."],
            "Indirect",
            ["Spreadsheets and group chats", "Planning by hand.", "Does the searching and the math."],
            ["A travel agency", "A person plans and books for you.", "Never books, and free to try."],
            ["TripIt and Google Travel", "Keeping bookings in one place.", "Works before booking."],
        ],
        caption="Direct and indirect competitors.",
        bold_first_col=True)),
    ("h3", "Why not just use Expedia, or ask a chat assistant?"),
    ("table", dict(
        widths=[1.3, 2.6, 2.6],
        header=["", "Expedia", "A general chat assistant"],
        rows=[
            ["Best at", "Inventory, booking and loyalty points. If you know what you want, use it.",
             "Ideas and inspiration in conversation."],
            ["Live prices", "Yes, from its own inventory.", "It may search the web, but prices are not "
             "guaranteed to be current."],
            ["Whole-trip budget", "Its assistant helps plan, shop and book inside Expedia [3]. We have not "
             "tested whether it keeps a trip under a total.", "It can add up costs itself, with no separate "
             "check of the sum."],
            ["Roameo", "Plans the days around interests, events and weather, prices the flight and hotel "
             "with live searches, labels the estimates, and leaves booking to you.", "Prices come from "
             "searches and totals from code. When the plan does not fit, Roameo says so and asks."],
        ],
        caption="The two questions we expect most.",
        bold_first_col=True)),
    ("p", "**Our honest position.** We do not beat Expedia at booking or a chat assistant at conversation. "
          f"Roameo is the planning step in between, turning {Q}Chicago for 4 days, budget $600{E} into a "
          "priced, checked plan that you approve, and it could sit on top of either."),
    ("h2", "7.3 How students and the community benefit"),
    ("bullets", [
        "**Students.** One sentence instead of many tabs, a total added up by code, and the final say on "
        "their own money. We have no user study, so we claim no time saved.",
        "**Clubs.** A club planning a trip for four can see 2 rooms and the cost per person before anyone "
        "pays.",
        "**Classes.** The code is public on GitHub, so a class can read an AI that asks before it spends.",
        "**Anyone.** The demo runs free in about three minutes, with no sign-ups or paid accounts and "
        "sample prices for 8 cities. One shared live link can cover about 80 plans a month on the free "
        "search plan, and the optional access code and the limit of 60 requests per address per hour "
        "help that quota last.",
    ]),
    ("h2", "7.4 What comes next"),
    ("p", "**Question 7, anything else?** Next is a pilot with 5 to 10 students, measuring overspend and "
          "time to a plan they accept, then links to booking sites with you still the one who books. Our "
          f"ask is simple. Try Roameo at [roameo-l13h.onrender.com]({DEMO}) and tell us where it goes wrong."),

    # ------------------------------------------------------------------ 8
    ("h1", "8. Conclusion, three ideas, one trip"),
    ("p", "**AI agents did the legwork for Alex.** They asked where from and when, and compared 8 "
          "flights, 18 hotels and 59 events. **Code checked the money.** It tried five fixes from $1,235 "
          "to $780 and showed the $180 gap. **And Alex made the call.** Nothing was final until Alex said "
          "OK. A chat reply can tell you a plan fits your budget with nobody checking the "
          "sum. Roameo treats your budget as a limit, not a wish. One honest limit remains. Our own tests "
          "on sample prices cannot show that Roameo helps people plan better. Only a study with real "
          "students can."),

    # ------------------------------------------------------------------ thanks and references
    ("h1", "Acknowledgements"),
    ("p", "**Question 6, key sources and acknowledgement.** We thank the organizers of the PEAAII AI "
          "Applications Hackathon 2026. Roameo uses data from Google Flights, Hotels, Events and Maps "
          "through SerpApi, Ticketmaster Discovery, Open-Meteo, and OpenStreetMap and its contributors. "
          "The AI model is Claude Haiku 5.5 by Anthropic, through OpenRouter. The slides use the Elegant "
          "template by Lars Spreng, and the poster the Gemini theme by Anish Athalye. Roameo is built with "
          "FastAPI, React, Vite, Tailwind CSS and Leaflet. The UMass Boston logo marks the authors" + A +
          " affiliation only."),
    ("h1", "References"),
    ("p", f"[1] Expedia Group Media Solutions, {Q}Path to Purchase{E} research (2023). "
          "[expedia.com/newsroom/eg-path-to-purchase-research](https://www.expedia.com/newsroom/eg-path-to-purchase-research)"),
    ("p", "[2] Booking.com, Global AI Sentiment Report (July 2025), via Hospitality Net. "
          "[hospitalitynet.org/news/4128268.html](https://www.hospitalitynet.org/news/4128268.html)"),
    ("p", "[3] Expedia Group, Spring 2024 product release (Romie), May 2024. "
          "[expedia.com/newsroom/spring-product-release-2024](https://www.expedia.com/newsroom/spring-product-release-2024)"),
    ("p", f"[4] Fast.io, {Q}Best AI for travel planning 2026{E}, a vendor review (accessed October 2026). "
          "[fast.io/resources/best-ai-for-travel-planning-2026](https://fast.io/resources/best-ai-for-travel-planning-2026)"),
    ("p", "[5] Qlik and Censuswide survey, Business Wire (August 2025). "
          "[businesswire.com/news/home/20250805879663](https://www.businesswire.com/news/home/20250805879663)"),
    ("p", "[6] Global Rescue, Fall 2025 traveler survey on AI trip planning (accessed October 2026). "
          "[globalrescue.com/common/blog/detail/ai-agentic-trip-planning](https://www.globalrescue.com/common/blog/detail/ai-agentic-trip-planning)"),
    ("p", f"[7] Adobe, {Q}Consumers embrace generative AI for trip planning{E} (accessed October 2026). "
          "[business.adobe.com/blog/consumers-embrace-generative-ai-for-trip-planning](https://business.adobe.com/blog/consumers-embrace-generative-ai-for-trip-planning)"),
    ("p", f"[8] PhocusWire, {Q}Amadeus to shut down self-service APIs portal for developers{E} (2026). "
          "[phocuswire.com/amadeus-shut-down-self-service-apis-portal-developers](https://www.phocuswire.com/amadeus-shut-down-self-service-apis-portal-developers)"),
    ("p", "[9] SerpApi, Google search APIs (accessed October 2026). [serpapi.com](https://serpapi.com/)"),
    ("p", "[10] Ticketmaster Discovery API (accessed October 2026). "
          "[developer.ticketmaster.com](https://developer.ticketmaster.com/)"),
    ("p", "[11] Open-Meteo, weather APIs (accessed October 2026). [open-meteo.com](https://open-meteo.com/)"),
    ("p", "[12] OpenStreetMap contributors. [openstreetmap.org](https://www.openstreetmap.org/)"),
    ("p", "[13] Anthropic, Claude Haiku 5.5, through OpenRouter (accessed October 2026). "
          "[openrouter.ai](https://openrouter.ai/)"),
    ("p", "[14] Lars Spreng, Elegant Beamer template (2022), CC BY 4.0."),
    ("p", "[15] Anish Athalye, Gemini poster theme, MIT License. "
          "[github.com/anishathalye/gemini](https://github.com/anishathalye/gemini)"),
]
