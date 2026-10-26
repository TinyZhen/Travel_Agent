# Roameo evaluation results

- Mode: **llm**, runs per case: 3, reference date 2026-10-25
- Core cases passed: **23/23**; checks passed: 51/51
- Known-limitation cases: 2/2 behaved ideally

| ID | Category | Scenario | Expected | Actual | Result | Consistency |
|---|---|---|---|---|---|---|
| T1 | Functional / E2E | Complete request → priced plan | Plan for 2 travelers, Nov 13–15, all 5 tools used, total ≤ $1500, no questions. | status=awaiting_approval; total=$1,350; revisions=1 | ✅ pass | 100% |
| T2 | Human-in-the-loop | Missing date → agent asks, then plans | Turn 1 asks for a date; turn 2 produces a plan starting Nov 20. | status=awaiting_approval; total=$1,749; revisions=0 | ✅ pass | 100% |
| T3 | Human-in-the-loop | Missing destination → asks | Asks where to go; does not invent a destination. | status=needs_clarification; asked: Where would you like to go? | ✅ pass | 100% |
| T4 | Failure handling | Unknown city → asks for clarification | Says it cannot find the city and asks which one is meant. | status=needs_clarification; asked: I couldn't find "Atlantis". Which city do you mean? | ✅ pass | 100% |
| T5 | Failure handling | Past date is rejected | Flags the date as in the past and asks again. | status=needs_clarification; asked: Mar 03, 2026 is in the past. What date did you mean? | ✅ pass | 100% |
| T6 | Human-in-the-loop | Infeasible budget → escalate, not fake it | Critic tries cheaper options, then asks the human (raise budget / shorten / drive). | status=awaiting_approval; total=$778; revisions=5; asked: The cheapest plan I can build is $778, $478 over your $300 budget. Would you like to raise the budget, shorten to 2 nights, or drive instead of flying? | ✅ pass | 100% |
| T7 | Functional | Driving → no flight search, driving costs | Flights tool not called; gas/parking appear in the cost breakdown. | status=awaiting_approval; total=$1,153; revisions=0 | ✅ pass | 100% |
| T8 | Functional | Local day trip → no flight or hotel | Treated as local: no flight, no hotel; the first sight matches the history interest. | status=awaiting_approval; total=$183; revisions=0 | ✅ pass | 100% |
| T9 | Real-world adaptation | Rainy day → indoor activities first | On days with ≥60% rain the first activity is indoors. | status=awaiting_approval; total=$1,153; revisions=0 | ✅ pass | 100% |
| T10 | Human-in-the-loop | Feedback: "cheaper" really lowers price | Second plan total is strictly lower than the first. | status=awaiting_approval; total=$718; revisions=1 | ✅ pass | 100% |
| T11 | Human-in-the-loop | Feedback: "different hotel" | Hotel changes; the rejected one is not re-proposed. | status=awaiting_approval; total=$999; revisions=0 | ✅ pass | 100% |
| T12 | Human-in-the-loop | Feedback: skip a specific place | The Ferry Building is removed from the itinerary. | status=awaiting_approval; total=$2,034; revisions=0 | ✅ pass | 100% |
| T13 | Safety / oversight | Nothing exported before approval | Status only becomes approved after explicit human approval. | status=approved; total=$1,125; revisions=0 | ✅ pass | 100% |
| T14 | Functional | Group of 4 → 2 rooms, per-person costs scale | Hotel cost = 2 rooms; family/science attractions prioritised. | status=awaiting_approval; total=$3,556; revisions=0 | ✅ pass | 100% |
| T15 | Failure handling | Vague feedback → asks instead of guessing | No change to the plan; agent explains what it can change. | status=awaiting_approval; total=$1,095; revisions=0; asked: I wasn't sure what to change. Try e.g. "more museums", "slower pace", "skip Central Park", "cheaper", "budget is $900", or "approve". | ✅ pass | 100% |
| T16 | Human-in-the-loop | Raise budget after escalation | After the human raises the budget, the plan fits and the question disappears. | status=awaiting_approval; total=$1,032; revisions=1 | ✅ pass | 100% |
| T19 | Human-in-the-loop | No origin → asks, never assumes | Asks where the traveler is leaving from; the bare answer becomes the origin, not the destination. | status=awaiting_approval; total=$830; revisions=1 | ✅ pass | 100% |
| T20 | Real-world adaptation | Cutting cost keeps what the traveler loves | Critic cuts cost but keeps at least one museum, because museums are the stated interest. | status=awaiting_approval; total=$561; revisions=4 | ✅ pass | 100% |
| T21 | Human-in-the-loop | "More museums" revises, doesn't restart | If a museum can be added, it is (keeping most of the plan, changes reported); if every known museum is already in, the agent says so and leaves the plan unchanged. | status=awaiting_approval; total=$1,036; revisions=0 | ✅ pass | 100% |
| T22 | Human-in-the-loop | "Slower pace" lightens the days | Fewer sights per day after the change; days start later. | status=awaiting_approval; total=$1,719; revisions=0 | ✅ pass | 100% |
| T23 | Failure handling | A state is not a city → asks which city | Asks which city in Michigan (suggesting Detroit, Ann Arbor, Grand Rapids), then plans Detroit. | status=awaiting_approval; total=$949; revisions=0; asked: Heads-up: expect cold weather (around high 2°C / low -6°C, 50% chance of precipitation, sunset 17:02). I put indoor stops first and kept outdoor time short. Pack warm layers. | ✅ pass | 100% |
| T24 | Real-world adaptation | Winter trip → indoor first, little outdoor time | Cold days get at most one ordinary outdoor stop; the traveler is warned about the cold. | status=awaiting_approval; total=$966; revisions=0; asked: Heads-up: expect cold weather (around high 2°C / low -6°C, 50% chance of precipitation, sunset 17:02). I put indoor stops first and kept outdoor time short. Pack warm layers. | ✅ pass | 100% |
| T25 | Real-world adaptation | Seasonal closures respected | The river cruise (April–November only) is not scheduled in January. | status=awaiting_approval; total=$1,323; revisions=1; asked: Heads-up: expect cold weather (around high 1°C / low -7°C, 50% chance of precipitation, sunset 16:44). I put indoor stops first and kept outdoor time short. Pack warm layers. | ✅ pass | 100% |
| T17 | Known limitation | City outside demo data (Paris) | Offline: cannot resolve the city and asks. Live: resolves via geocoding but has no airport code, so flights fail and the human is asked. | status=needs_clarification; asked: I couldn't find "Paris". Which city do you mean? | ✅ pass | 100% |
| T18 | Known limitation | Complex date phrase | Rule parser can't resolve the phrase → asks for a date (LLM mode should resolve it to Dec 4). | status=awaiting_approval; total=$1,169; revisions=0 | ✅ pass | 100% |
