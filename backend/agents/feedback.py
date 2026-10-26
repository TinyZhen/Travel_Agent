"""Feedback agent: turn the traveler's reaction to a plan into concrete edit operations.

The plan is then *revised*, not rebuilt: the orchestrator keeps what the traveler
didn't ask to change and reports exactly what was added or removed.
"""
from __future__ import annotations

import re

import llm
from agents.intake import INTEREST_WORDS

TAGS = sorted(INTEREST_WORDS) + ["landmark"]
SYNONYMS = {w: tag for tag, words in INTEREST_WORDS.items() for w in words + [tag]}
SYNONYMS.update({"parks": "nature", "landmarks": "landmark", "sights": "landmark", "galleries": "art",
                 "art galleries": "art", "historic sites": "history", "markets": "food"})

SYSTEM = """You are the Feedback agent of a travel planner. The traveler is reacting to a proposed plan.
Return JSON with these keys (omit ones that don't apply):
approve (bool), cheaper (bool: ONLY if they ask to reduce cost, e.g. "cheaper", "too expensive";
stating or raising a budget such as "budget is $1400" is NOT cheaper), different_hotel (bool), different_flight (bool), upgrade_hotel (bool),
more (list of tags they want MORE of; only the kinds they actually named, e.g. "more museums" -> ["museum"]),
less (list of tags they want LESS of),
pace ("relaxed" | "packed" | "normal"),
add_places (list of specific named places they want added),
remove_places (list of names, copied exactly from the plan, that they want removed).
Allowed tags: {tags}.
Places currently in the plan: {places}."""


def _tag(word: str):
    w = word.lower().strip()
    return SYNONYMS.get(w) or SYNONYMS.get(w.rstrip("s"))


def rule_parse(message: str, plan_names: list[str]) -> dict:
    t, ops = message.lower(), {}
    if re.match(r"^\s*(approve|approved|looks good|lgtm|confirm|perfect)\b", t):
        ops["approve"] = True
    if re.search(r"\b(cheaper|too expensive|save money|lower cost)\b", t):
        ops["cheaper"] = True
    if re.search(r"\b(different|another|other|change the) hotel\b|don'?t like the hotel", t):
        ops["different_hotel"] = True
    if re.search(r"\b(different|another|other|change the) (flight|airline)\b", t):
        ops["different_flight"] = True
    if re.search(r"\b(nicer|better|upgrade|luxury) hotel\b", t):
        ops["upgrade_hotel"] = True
    words = "|".join(sorted(map(re.escape, SYNONYMS), key=len, reverse=True))
    ops["more"] = sorted({_tag(m[1]) for m in re.finditer(
        rf"\b(?:more|extra|additional|another)\s+(?:\w+\s+)?({words})\b", t)} - {None})
    ops["less"] = sorted({_tag(m[1]) for m in re.finditer(
        rf"\b(?:less|fewer|no more|not so many|too many|too much)\s+(?:\w+\s+)?({words})\b", t)} - {None})
    if re.search(r"\b(relax|relaxed|slower|less packed|less rushed|too packed|too rushed|take it easy|chill)\b", t):
        ops["pace"] = "relaxed"
    elif re.search(r"\b(packed|busier|fit more in|more things|see as much)\b", t):
        ops["pace"] = "packed"
    ops["add_places"] = [m[1].strip() for m in re.finditer(
        r"\b(?:add|include|also see|squeeze in)\s+(?:the\s+)?([A-Z][\w'&.-]*(?:\s+(?:of\s+)?[A-Z][\w'&.-]*)*)", message)]
    ops["remove_places"] = []
    for name in plan_names:
        key = next((w for w in re.findall(r"[a-z]+", name.lower())
                    if len(w) > 3 and w not in {"the", "museum", "national", "park"}), None)
        if key and re.search(rf"\b(skip|remove|drop|without|no)\b[^.,;]*\b{re.escape(key)}", t):
            ops["remove_places"].append(name)
    return {k: v for k, v in ops.items() if v}


def parse(message: str, plan_names: list[str]) -> tuple[dict, str]:
    ops = rule_parse(message, plan_names)
    if not llm.available():
        return ops, "rules"
    try:
        data = llm.chat_json(SYSTEM.format(tags=", ".join(TAGS), places="; ".join(plan_names)), message)
    except Exception:
        return ops, "rules"
    for k in ("approve", "cheaper", "different_hotel", "different_flight", "upgrade_hotel"):
        if data.get(k) is True:
            ops[k] = True
    for k in ("more", "less"):
        tags = {_tag(x) or (x if x in TAGS else None) for x in data.get(k) or []} - {None}
        if tags | set(ops.get(k, [])):
            ops[k] = sorted(tags | set(ops.get(k, [])))
    if data.get("pace") in ("relaxed", "packed", "normal"):
        ops["pace"] = data["pace"]
    for k in ("add_places", "remove_places"):
        vals = list(dict.fromkeys((ops.get(k) or []) + [str(x) for x in data.get(k) or []]))
        if vals:
            ops[k] = vals
    return ops, "llm"
