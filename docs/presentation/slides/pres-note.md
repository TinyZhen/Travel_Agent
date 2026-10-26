# Roameo, the seven minute presentation script

Speakers are Zhen Lu (slides 1 to 5) and Noctis Zhang (slides 6 to 11). The team can change this split. The pace is about 140 spoken words a minute, and the budget is 420 seconds at most. Numbers are written as they are spoken. Every number comes from the repository or from the report's cited sources (see section 9 of the revision plan in this folder). Alex is a student we made up, so say so on slide 2. The run on slides 4 to 6 is real, and the ending on slide 6 comes from our tests.

> Lines that start with this sign are cues for the speaker and are not spoken. The notes tool in the tools folder copies the spoken text into the slide notes.

## Slide 1. Roameo plans your trip and lets you decide on the money
_about 15 seconds_

> Zhen Lu speaks.

Hi, we are Zhen Lu and Noctis Zhang, from computer science at UMass Boston. This is Roameo, a trip planner. AI agents do the legwork, code checks the money, and you make the call.

## Slide 2. Alex has $600 for four days in Chicago and types one sentence
_about 35 seconds_

Meet Alex, a student we made up for this talk. Alex has six hundred dollars for four days in Chicago, and types one sentence. But flights, a hotel, sights, food and transit all have to add up, again after every change. A chat reply can do that sum itself and say it fits, with nobody checking. And in one survey, eighty nine percent wanted AI help to plan, but only twelve percent were happy to let it decide alone.

## Slide 3. Roameo rests on three simple ideas
_about 19 seconds_

Roameo rests on three simple ideas. AI agents do the legwork. Code checks the money. You make the call. An agent here is an AI helper with one job. Each idea has three parts, and we will follow Alex through all of them.

## Slide 4. AI agents ask first, then choose what to search
_about 44 seconds_

Idea one, AI agents do the legwork. First, they ask for what is missing. Alex never said where from or when, so Roameo asked. It never guesses a city or a date, because a guessed date gives a useless plan. Second, they choose which searches the trip needs. For Alex they compared eight flights, eighteen hotels and fifty nine events. Past years' weather for those dates looked cold and rainy, so Roameo also looked for indoor places, holiday markets and ice skating. Third, they turn plain words into changes. Make it cheaper, or slower pace, edits the plan instead of starting over.

## Slide 5. Code adds up every price and tries five fixes, from $1,235 to $780
_about 47 seconds_

Idea two, code checks the money. Plain code adds up every total. The flight and the hotel are live prices, and food and local transit are labelled estimates. Alex's first plan came to one thousand two hundred thirty five dollars. Then code tries one fix at a time, at most five. A cheaper hotel, the cheapest flight, no paid events, free sights, indoor stops for the rain. Not every fix saves money, so it checks the total after each one. Why code and not the AI? Code gives the same exact sum every time, and we can test it. An AI model's answer can change from run to run.

## Slide 6. Still $180 over, Roameo stops and asks Alex what to do
_about 43 seconds_

> Hand over to Noctis Zhang.

After five fixes the plan costs seven hundred eighty dollars, still one hundred eighty over. This is the moment that matters. Roameo does not hide the gap, and it does not decide for Alex. It stops and asks. Raise the budget, shorten to two nights, or drive instead of flying? That is idea three, you make the call. Our tests replay Alex's exact sentence, and when the budget is raised, the plan is rebuilt, checked again, and it fits. Saying OK only downloads a calendar file. Roameo never books or pays, because paying is a choice a person should make.

## Slide 7. All 23 tests of what Roameo should do pass, with and without the AI
_about 49 seconds_

Does it work? A test here is a conversation we wrote in advance, typed into Roameo, with code that checks the answer. For example, that it asks for a missing date. A test passes when every check comes out right. We ran them in demo mode, which is practice runs with sample prices, and three times with the AI, because the AI can answer differently each time. All twenty three tests passed, in demo mode and in each of the three runs. Only the AI understood first weekend of December. To be fair, we wrote the tests ourselves, both modes used sample prices, three runs is a small sample, and there was no user study.

## Slide 8. Roameo never books or pays, and says what it cannot do yet
_about 40 seconds_

Responsible use of AI follows the same three ideas. The AI asks before it guesses, and each helper has one narrow job. Code shows its math and labels estimates. And you decide, and book it yourself. What goes where? In AI mode, what you type goes to the AI model. The searches get the city, the dates and airport codes, not your sentence or your budget. There are no accounts. What can be wrong? The summary and the visit tips are written by the AI, and they can be wrong or out of date.

## Slide 9. Other apps plan or sell trips, Roameo treats your budget as a limit
_about 38 seconds_

Who else helps plan trips? Chat assistants can plan a trip in a chat window. Expedia's assistant, Romie, helps you plan, shop and book inside Expedia. Planner apps like Mindtrip, Layla and Wonderplan focus on ideas and day plans. People also use spreadsheets, group chats or a travel agency. We have not tested the others. Roameo is the planning step in between, and it treats your budget as a limit, not a wish. It is built for students on short trips, budget travelers and small groups. First, student clubs.

## Slide 10. Anyone can try Roameo free, and a club can share one link
_about 33 seconds_

Anyone can try it free. Demo mode starts on a laptop in about three minutes, with sample prices for eight cities and no sign-ups. A club can share one link, and a group of four sees two rooms and the cost per person before anyone pays. A class can read the code to see an AI that asks before it spends. Next, a pilot with five to ten students. Please try it, and tell us where it goes wrong.

## Slide 11. AI did the legwork, code checked the money, and Alex made the call
_about 21 seconds_

So, three ideas. AI agents did the legwork for Alex. Code checked the money and found the one hundred eighty dollar gap. And Alex made the call. Roameo treats your budget as a limit, not a wish. Thank you to the PEAAII organizers. Scan the code to try it.
