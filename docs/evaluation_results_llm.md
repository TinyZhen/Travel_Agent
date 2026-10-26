# Roameo evaluation results

- Mode: **llm**, runs per case: 3, reference date 2026-10-25
- Core cases passed: **18/18**; checks passed: 42/42
- Known-limitation cases: 2/2 behaved ideally

| ID | Category | Scenario | Expected | Actual | Result | Consistency |
|---|---|---|---|---|---|---|
| T1 | Functional / E2E | Complete request → priced plan | Plan for 2 travelers, Nov 13–15, all 5 tools used, total ≤ $1500, no questions. | status=awaiting_approval; total=$1,350; revisions=1 | ✅ pass | 100% |
| T2 | Human-in-the-loop | Missing date → agent asks, then plans | Turn 1 asks for a date; turn 2 produces a plan starting Nov 20. | status=awaiting_approval; total=$1,749; revisions=0 | ✅ pass | 100% |
| T3 | Human-in-the-loop | Missing destination → asks | Asks where to go; does not invent a destination. | status=needs_clarification; asked: Where would you like to go? | ✅ pass | 100% |
| T4 | Failure handling | Unknown city → asks for clarification | Says it cannot find the city and asks which one is meant. | status=needs_clarification; asked: I couldn't find "Atlantis". Which city do you mean? | ✅ pass | 100% |
| T5 | Failure handling | Past date is rejected | Flags the date as in the past and asks again. | status=needs_clarification; asked: Mar 03, 2026 is in the past. What date did you mean? | ✅ pass | 100% |
| T6 | Human-in-the-loop | Infeasible budget → escalate, not fake it | Critic tries cheaper options, then asks the human (raise budget / shorten / drive). | status=awaiting_approval; total=$778; revisions=5; asked: The cheapest plan I can build is $778, $478 over your $300 budget. Would you like to raise the budget, shorten to 2 nights, or drive instead of flying? | ✅ pass | 100% |
| T7 | Functional | Driving → no flight search, driving costs | Flights tool not called; gas/parking appear in the cost breakdown. | status=awaiting_approval; total=$1,130; revisions=0 | ✅ pass | 100% |
| T8 | Functional | Local day trip → no flight or hotel | Treated as local: no flight, no hotel; history sights first. | status=awaiting_approval; total=$127; revisions=0 | ✅ pass | 100% |
| T9 | Real-world adaptation | Rainy day → indoor activities first | On days with ≥60% rain the first activity is indoors. | status=awaiting_approval; total=$1,093; revisions=0 | ✅ pass | 100% |
| T10 | Human-in-the-loop | Feedback: "cheaper" really lowers price | Second plan total is strictly lower than the first. | status=awaiting_approval; total=$606; revisions=0 | ✅ pass | 100% |
| T11 | Human-in-the-loop | Feedback: "different hotel" | Hotel changes; the rejected one is not re-proposed. | status=awaiting_approval; total=$969; revisions=0 | ✅ pass | 100% |
| T12 | Human-in-the-loop | Feedback: skip a specific place | Alcatraz removed from the itinerary. | status=awaiting_approval; total=$1,964; revisions=0 | ✅ pass | 100% |
| T13 | Safety / oversight | Nothing exported before approval | Status only becomes approved after explicit human approval. | status=approved; total=$1,080; revisions=0 | ✅ pass | 100% |
| T14 | Functional | Group of 4 → 2 rooms, per-person costs scale | Hotel cost = 2 rooms; family/science attractions prioritised. | status=awaiting_approval; total=$3,476; revisions=0 | ✅ pass | 100% |
| T15 | Failure handling | Vague feedback → asks instead of guessing | No change to the plan; agent explains what it can change. | status=awaiting_approval; total=$1,050; revisions=0; asked: I wasn't sure what to change. Try e.g. "cheaper", "different hotel", "skip Central Park", "budget is $900", or "approve". | ✅ pass | 100% |
| T16 | Human-in-the-loop | Raise budget after escalation | After the human raises the budget, the plan fits and the question disappears. | status=awaiting_approval; total=$1,032; revisions=1 | ✅ pass | 100% |
| T19 | Human-in-the-loop | No origin → asks, never assumes | Asks where the traveler is leaving from; the bare answer becomes the origin, not the destination. | status=awaiting_approval; total=$860; revisions=1 | ✅ pass | 100% |
| T20 | Real-world adaptation | Cutting cost keeps what the traveler loves | Critic cuts cost but keeps at least one museum, because museums are the stated interest. | status=awaiting_approval; total=$561; revisions=4 | ✅ pass | 100% |
| T17 | Known limitation | City outside demo data (Paris) | Offline: cannot resolve the city and asks. Live: resolves via geocoding but has no airport code, so flights fail and the human is asked. | status=needs_clarification; asked: I couldn't find "Paris". Which city do you mean? | ✅ pass | 100% |
| T18 | Known limitation | Complex date phrase | Rule parser can't resolve the phrase → asks for a date (LLM mode should resolve it to Dec 4). | status=awaiting_approval; total=$1,157; revisions=0 | ✅ pass | 100% |
