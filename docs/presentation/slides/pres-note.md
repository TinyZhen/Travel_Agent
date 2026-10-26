# Roameo: seven-minute presentation script

Speakers: Zhen Lu and Noctis Zhang. Pace: about 140 spoken words per minute. Budget: 420 seconds
at most, planned 407. Numbers are written as they are spoken. Every number comes from the
repository (see ../STORY_PLAN.md, section 7). Alex is an illustration: say so on slide 2.

## Slide 1. Roameo: agents plan the trip, you make the call
_about 13 seconds_

Hi, we are Zhen Lu and Noctis Zhang. This is Roameo, an AI trip planner for students and budget
travellers. Its agents plan the trip, and you make the call.

## Slide 2. Alex has $600 and one sentence
_about 31 seconds_

Meet Alex, a student we made up for this talk. Alex has six hundred dollars for a long weekend
and types one sentence: Chicago for four days, budget six hundred dollars. Simple to say. But
flights, a hotel, sights, food and transit all have to add up, around the weather and the dates,
and again after every change. A chat reply can do that sum itself and say it fits, with nobody
checking.

## Slide 3. One sentence becomes a checked plan, and Alex keeps the final say
_about 43 seconds_

Here is one real run of the app. First, Roameo asked back: where are you leaving from, and what
date? It never guesses a city or a date. Alex answered: from Boston, leaving November twentieth.
Then the agents went to work. An agent is an AI helper with one job. They found eight flights,
eighteen hotels and fifty nine events, and saw rain and cold typical for those dates. The first
plan cost one thousand two hundred thirty five dollars. The critic cut it to seven hundred
eighty. Still one hundred eighty over. So Roameo did not decide. It asked Alex.

## Slide 4. AI agents gather, plain code checks the money, you decide twice
_about 60 seconds_

One, you ask. Two, AI agents gather. The intake agent turns your sentence into a city, dates and
a budget. If something is missing or in the past, it asks you. That is the first human
checkpoint. The research agent chooses which tools to call, and a final check adds any it
skipped. Three, plain code checks the money. The composer prices every stop, and the critic
repairs the plan one step at a time, at most five times. The AI never adds up the budget. Four,
you decide, the second checkpoint. You approve, or ask for a change, and the feedback agent
turns it into edits. Why agents? Each step depends on what the last one found. With no keys at
all, demo mode runs the same steps on rules and labelled sample data, all but the visit guides.

## Slide 5. The critic re-checks each repair, and stops after five
_about 44 seconds_

Here is the critic in Alex's run, from the app's own log. A cheaper hotel took the plan from one
thousand two hundred thirty five to nine hundred eighty four dollars. The cheapest flight did
not help. Dropping paid events even went up a little, because each repair rebuilds the plan.
Keeping free sights plus two that match Alex's interests reached seven hundred eighty. Moving
stops indoors for the rainy day kept it there. Five repairs is the limit. Our tests check the
same behaviour: with a three hundred dollar budget, it reports four hundred seventy eight over
instead of hiding it.

## Slide 6. Then it stops and asks Alex, instead of quietly going over
_about 36 seconds_

So Roameo stops and asks. The bar turns red: one hundred eighty dollars over your six hundred
dollar budget. Would you like to raise the budget, shorten to two nights, or drive instead of
flying? This is the moment that matters. The agents did the work, but the trade-off belongs to
Alex. Alex picks one, the plan is rebuilt and checked again, and it waits. Nothing is final
until Alex approves, and approving only exports a calendar file. Roameo never books or pays.

## Slide 7. Plans bend to feedback, weather and the season
_about 44 seconds_

Plans also bend. Alex can say cheaper, different hotel, skip a place, more museums or slower
pace. Each request is an edit, not a restart, and the reply lists what changed. Weather and
season count too. Here someone asks for Michigan in December. Michigan is a state, so it asks
which city, then uses what those dates were like in past years, puts indoor stops first and says
pack warm layers. And with the AI on, every stop gets a visit guide: what not to miss, and how
to spend the time there. For museums, exhibitions come only from a real web search.

## Slide 8. All 23 core tests pass in both modes, and in each of three AI runs
_about 54 seconds_

Does it work? We wrote twenty five test conversations. Each is a scripted chat followed by
checks on the result, for example, the total is within budget, or there is no flight search for
a road trip. Twenty three are core tests, and two are known limits that we report anyway. The
core tests pass in demo mode, which follows fixed rules, and in AI mode, with Claude Haiku
through OpenRouter. We ran AI mode three times, and every core test passed each time. Most tests
are about asking you and taking feedback. But we wrote the tests, the tools used sample prices,
and three runs is a small sample. Demo mode gives the same answer every time, so only the AI
runs tell us about consistency.

## Slide 9. What it cannot do yet
_about 31 seconds_

What it cannot do yet. Without keys it covers seven cities. Food and local transit are flat
daily estimates. Many events list no price, so they stay out of the total. Visit tips are
written by the AI and may be out of date. Trips live in memory, so a restart clears them. And
there was no user study. The tests do not judge how good a plan is, or live prices.

## Slide 10. One URL to deploy, three minutes to try without keys
_about 38 seconds_

It is easy to run. Without any keys, it starts on a laptop in about three minutes. To share it,
one Docker image and a blueprint file put it on Render as one web address. An access code and
sixty requests per visitor per hour protect the search quota. The free plan sleeps after fifteen
idle minutes, so open it a minute early. Then add keys one at a time, with any OpenRouter model
for the agents. It is built for students and budget travellers on short trips.

## Slide 11. Alex still makes the call on the $600
_about 13 seconds_

Back to Alex. Roameo did the research and the math, and showed the gap honestly. The six hundred
dollars stays Alex's call. Scan the code to try it. Thank you.