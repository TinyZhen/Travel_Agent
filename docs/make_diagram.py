"""Draws docs/workflow.png. Run: backend/venv/bin/python docs/make_diagram.py"""
import pathlib

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = pathlib.Path(__file__).with_name("workflow.png")
INK, MUTED = "#1f2a2e", "#5b6b70"
C = {"human": "#0f766e", "intake": "#0369a1", "research": "#b45309", "compose": "#4d7c0f",
     "critic": "#be123c", "tool": "#78716c"}

fig, ax = plt.subplots(figsize=(13, 6.4), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 6.4)
ax.axis("off")


def box(x, y, w, h, title, sub, color, fill=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=color if fill else "white", ec=color, lw=1.6))
    tc = "white" if fill else color
    ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center", fontsize=11.5, weight="bold", color=tc)
    ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center", fontsize=8.6, color=tc, linespacing=1.25)


def arrow(x1, y1, x2, y2, label="", color=INK, rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, lw=1.4,
                                 color=color, connectionstyle=f"arc3,rad={rad}", linestyle=ls))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.16, label, ha="center", fontsize=8.3, color=color,
                bbox=dict(fc="white", ec="none", pad=1.5))


# main row
box(0.2, 3.6, 1.9, 1.3, "Traveler", "free-text request", C["human"])
box(2.7, 3.6, 2.0, 1.3, "Intake agent", "extract trip spec\ncheck what's missing", C["intake"])
box(5.3, 3.6, 2.1, 1.3, "Research agent", "choose & call tools\ncoverage guardrail", C["research"])
box(8.0, 3.6, 2.0, 1.3, "Composer agent", "pick flight & hotel\nschedule days, price", C["compose"])
box(10.6, 3.6, 2.2, 1.3, "Critic agent", "budget, dates, weather\nduplicates check", C["critic"])

arrow(2.1, 4.25, 2.7, 4.25)
arrow(4.7, 4.25, 5.3, 4.25, "spec")
arrow(7.4, 4.25, 8.0, 4.25, "results")
arrow(10.0, 4.25, 10.6, 4.25, "plan")
arrow(11.7, 4.9, 9.0, 4.9, "", C["critic"], rad=0.35)
ax.text(10.35, 5.62, "issue → safe repair (≤4×)", ha="center", fontsize=8.3, color=C["critic"])

# clarification loop
arrow(3.7, 4.9, 1.15, 4.9, "", C["human"], rad=0.45)
ax.text(2.45, 5.62, "HITL #1: ask for missing / invalid info", ha="center", fontsize=8.3, color=C["human"])

# tools
tools = ["flights", "hotels", "attractions", "events", "weather"]
for i, t in enumerate(tools):
    x = 3.3 + i * 1.25
    ax.add_patch(FancyBboxPatch((x, 1.95), 1.1, 0.6, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="white", ec=C["tool"], lw=1.3))
    ax.text(x + 0.55, 2.25, t, ha="center", va="center", fontsize=9.5, color=INK)
    arrow(6.35, 3.6, x + 0.55, 2.55, color="#a8a29e")
ax.text(6.35, 1.62, "live API when a key is set · sample data otherwise (labelled)", ha="center",
        fontsize=8.3, color=MUTED)

# approval
box(10.6, 1.0, 2.2, 1.3, "Traveler reviews", "approve · or say\n\"cheaper\", \"skip X\"…", C["human"])
arrow(11.7, 3.6, 11.7, 2.3, "plan + trace")
arrow(10.6, 1.65, 9.0, 3.6, "HITL #2: feedback → re-plan", C["human"], rad=-0.25)
box(7.6, 0.2, 2.4, 0.75, "Export .ics", "nothing is booked or paid", C["human"], fill=False)
arrow(10.6, 1.15, 10.0, 0.6)
ax.text(10.45, 0.62, "approve", fontsize=8.3, color=INK)

ax.text(0.2, 6.05, "Roameo: multi-agent workflow with two human-in-the-loop checkpoints",
        fontsize=14, weight="bold", color=INK)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print(OUT)
