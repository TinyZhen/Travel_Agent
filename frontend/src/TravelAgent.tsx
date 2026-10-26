import React, { useEffect, useRef, useState } from "react";
import AttractionsMap from "./AttractionsMap";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type Item = { kind: string; name: string; hours?: number; time?: string; cost: number; price_unknown?: boolean; indoor?: boolean; lat?: number; lng?: number; source?: string; url?: string };
type Day = { date: string; weather?: string; rain_chance?: number; items: Item[] };
type State = {
    session_id: string;
    status: "needs_clarification" | "awaiting_approval" | "approved" | "error";
    mode: string;
    spec: { origin: string; destination?: string; start_date?: string; nights: number; travelers: number; budget_usd?: number; interests: string[]; transport: string; assumptions: string[] };
    questions: string[];
    plan?: { flight?: any; hotel?: any; days: Day[]; cost_breakdown: Record<string, number>; total_cost: number; summary: string; issues: string[]; revisions: number };
    trace: { agent: string; action: string; detail: string }[];
};
type Msg = { role: "user" | "agent"; text: string };

const EXAMPLES = [
    "Weekend in New York on Nov 13 from Boston with my partner, we love museums and jazz, budget $1500",
    "Chicago for 4 days, budget $600",
    "Day trip in Boston on Nov 7, I live in Boston and like history",
];

const AGENT_COLORS: Record<string, string> = {
    Intake: "bg-sky-100 text-sky-800",
    Research: "bg-amber-100 text-amber-800",
    Critic: "bg-rose-100 text-rose-800",
    Feedback: "bg-violet-100 text-violet-800",
    Orchestrator: "bg-emerald-100 text-emerald-800",
};

const money = (n: number) => `$${Math.round(n).toLocaleString()}`;

export default function TravelAgent() {
    const [input, setInput] = useState("");
    const [state, setState] = useState<State | null>(null);
    const [msgs, setMsgs] = useState<Msg[]>([]);
    const [busy, setBusy] = useState(false);
    const [showTrace, setShowTrace] = useState(true);
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [msgs]);

    const send = async (text: string) => {
        if (!text.trim() || busy) return;
        setMsgs((m) => [...m, { role: "user", text }]);
        setInput("");
        setBusy(true);
        try {
            const res = await fetch(`${API}/api/message`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, session_id: state?.status === "error" ? null : state?.session_id }),
            });
            if (!res.ok) throw new Error(`${res.status}`);
            const data: State = await res.json();
            setState(data);
            setMsgs((m) => [...m, { role: "agent", text: replyFor(data) }]);
        } catch (e) {
            setMsgs((m) => [...m, { role: "agent", text: `Couldn't reach the planner (${e}). Is the backend running on ${API}?` }]);
        } finally {
            setBusy(false);
        }
    };

    const reset = () => { setState(null); setMsgs([]); };

    return (
        <div className="min-h-screen bg-stone-50 text-stone-800">
            <header className="border-b border-stone-200 bg-white">
                <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight text-teal-800">Roameo</h1>
                        <p className="text-sm text-stone-500">Your trip, planned by agents and approved by you.</p>
                    </div>
                    <div className="flex items-center gap-3">
                        {state && (
                            <span className={`rounded-full px-3 py-1 text-xs font-medium ${state.mode === "llm" ? "bg-teal-100 text-teal-800" : "bg-amber-100 text-amber-800"}`}>
                                {state.mode === "llm" ? "LLM agents" : "Demo mode · sample prices"}
                            </span>
                        )}
                        <button onClick={reset} className="text-sm text-stone-500 hover:text-stone-800">New trip</button>
                    </div>
                </div>
            </header>

            <main className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[400px_1fr]">
                {/* ---------------- conversation */}
                <section className="flex h-[calc(100vh-130px)] flex-col rounded-2xl border border-stone-200 bg-white">
                    <div className="flex-1 space-y-3 overflow-y-auto p-4">
                        {msgs.length === 0 && (
                            <div className="space-y-2">
                                <p className="text-sm text-stone-500">Tell me where and when. Try:</p>
                                {EXAMPLES.map((e) => (
                                    <button key={e} onClick={() => send(e)} className="block w-full rounded-xl border border-stone-200 p-3 text-left text-sm hover:border-teal-400 hover:bg-teal-50">
                                        {e}
                                    </button>
                                ))}
                            </div>
                        )}
                        {msgs.map((m, i) => (
                            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                                <div className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm ${m.role === "user" ? "bg-teal-700 text-white" : "bg-stone-100"}`}>
                                    {m.text}
                                </div>
                            </div>
                        ))}
                        {busy && <div className="text-sm text-stone-400">Agents are working…</div>}
                        <div ref={endRef} />
                    </div>

                    {state?.status === "awaiting_approval" && (
                        <div className="flex flex-wrap gap-2 border-t border-stone-100 px-4 pt-3">
                            <button onClick={() => send("approve")} className="rounded-full bg-teal-700 px-4 py-1.5 text-sm font-medium text-white hover:bg-teal-800">✓ Approve plan</button>
                            {["make it cheaper", "different hotel", "I'll drive"].map((q) => (
                                <button key={q} onClick={() => send(q)} className="rounded-full border border-stone-300 px-3 py-1.5 text-sm hover:bg-stone-100">{q}</button>
                            ))}
                        </div>
                    )}
                    <form onSubmit={(e) => { e.preventDefault(); send(input); }} className="flex gap-2 p-4">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={state?.status === "awaiting_approval" ? "Ask for changes, or approve…" : "Where to, and when?"}
                            className="flex-1 rounded-xl border border-stone-300 px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                        />
                        <button disabled={busy} className="rounded-xl bg-teal-700 px-4 text-sm font-semibold text-white disabled:opacity-50">Send</button>
                    </form>
                </section>

                {/* ---------------- plan */}
                <section className="space-y-6">
                    {!state?.plan && (
                        <div className="flex h-64 items-center justify-center rounded-2xl border border-dashed border-stone-300 text-stone-400">
                            Your plan will appear here.
                        </div>
                    )}
                    {state?.plan && <PlanView state={state} />}
                    {state && state.trace.length > 0 && (
                        <div className="rounded-2xl border border-stone-200 bg-white p-5">
                            <button onClick={() => setShowTrace(!showTrace)} className="flex w-full items-center justify-between text-left">
                                <h2 className="font-semibold">What the agents did</h2>
                                <span className="text-sm text-stone-400">{showTrace ? "hide" : "show"} ({state.trace.length} steps)</span>
                            </button>
                            {showTrace && (
                                <ol className="mt-4 space-y-2">
                                    {state.trace.map((t, i) => (
                                        <li key={i} className="flex items-start gap-3 text-sm">
                                            <span className={`w-24 shrink-0 rounded-md px-2 py-0.5 text-center text-xs font-medium ${AGENT_COLORS[t.agent] ?? "bg-stone-100"}`}>{t.agent}</span>
                                            <span><span className="font-medium">{t.action}</span>{t.detail && <span className="text-stone-500"> · {t.detail}</span>}</span>
                                        </li>
                                    ))}
                                </ol>
                            )}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}

function replyFor(s: State): string {
    if (s.status === "approved") return "Approved! Download your itinerary as a calendar file from the plan panel. Nothing has been booked. Bookings stay in your hands.";
    const parts: string[] = [];
    if (s.status === "awaiting_approval" && s.plan) {
        parts.push(s.plan.summary);
        if (s.plan.revisions) parts.push(`(The critic revised this plan ${s.plan.revisions}× to fit your constraints.)`);
    }
    parts.push(...s.questions);
    if (s.status === "awaiting_approval" && !s.questions.length) parts.push("Approve it, or tell me what to change.");
    return parts.join("\n\n");
}

function PlanView({ state }: { state: State }) {
    const { plan, spec } = state;
    if (!plan) return null;
    const budget = spec.budget_usd;
    const pct = budget ? Math.min(100, (plan.total_cost / budget) * 100) : 0;
    const over = budget ? plan.total_cost > budget : false;
    const points = plan.days.flatMap((d) => d.items).filter((i) => i.lat && i.lng);
    const sources = [plan.flight, plan.hotel, ...plan.days.flatMap((d) => d.items)].filter(Boolean).map((x) => x.source);
    const isDemo = sources.includes("demo");
    const live = [...new Set(sources.filter((s) => s && s !== "demo"))];

    return (
        <>
            <div className="rounded-2xl border border-stone-200 bg-white p-5">
                <div className="flex flex-wrap items-end justify-between gap-4">
                    <div>
                        <p className="text-sm text-stone-500">{spec.origin} → {spec.destination} · {spec.travelers} traveler{spec.travelers > 1 ? "s" : ""} · {spec.nights} night{spec.nights === 1 ? "" : "s"}</p>
                        <p className="text-3xl font-bold">{money(plan.total_cost)} <span className="text-base font-normal text-stone-500">estimated total</span></p>
                    </div>
                    {state.status === "approved" ? (
                        <a href={`${API}/api/export/${state.session_id}.ics`} className="rounded-xl bg-teal-700 px-4 py-2 text-sm font-semibold text-white">Download .ics</a>
                    ) : (
                        <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800">Waiting for your approval</span>
                    )}
                </div>
                {budget && (
                    <div className="mt-4">
                        <div className="h-2.5 overflow-hidden rounded-full bg-stone-100">
                            <div className={`h-full ${over ? "bg-rose-500" : "bg-teal-600"}`} style={{ width: `${pct}%` }} />
                        </div>
                        <p className={`mt-1 text-xs ${over ? "text-rose-600" : "text-stone-500"}`}>
                            {over ? `${money(plan.total_cost - budget)} over` : `${money(budget - plan.total_cost)} under`} your {money(budget)} budget
                        </p>
                    </div>
                )}
                <div className="mt-4 flex flex-wrap gap-2">
                    {Object.entries(plan.cost_breakdown).map(([k, v]) => (
                        <span key={k} className="rounded-lg bg-stone-100 px-2.5 py-1 text-xs">{k.replace(/_/g, " ")}: <b>{money(v)}</b></span>
                    ))}
                </div>
                {spec.assumptions.length > 0 && (
                    <ul className="mt-4 space-y-1 text-xs text-stone-500">
                        {spec.assumptions.map((a) => <li key={a}>• {a}</li>)}
                    </ul>
                )}
                {live.length > 0 && <p className="mt-3 text-xs text-teal-700">Live data: {live.join(", ").replace(/_/g, " ")}</p>}
                {isDemo && <p className="mt-1 text-xs text-amber-700">Items marked as samples use illustrative prices, not live quotes.</p>}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
                {plan.flight && (
                    <Card title="Flight" accent="border-l-sky-500">
                        <p className="font-semibold">{plan.flight.airline} · {plan.flight.from} → {plan.flight.to}{plan.flight.stops ? ` · ${plan.flight.stops} stop` : ""}</p>
                        <p className="text-sm text-stone-500">{fmtTime(plan.flight.departure_time)} → {fmtTime(plan.flight.arrival_time)}</p>
                        <p className="text-sm">{money(plan.flight.price_per_person)} / person{plan.flight.round_trip ? " round trip" : ""}</p>
                        <SourceTag item={plan.flight} />
                    </Card>
                )}
                {plan.hotel && (
                    <Card title="Hotel" accent="border-l-violet-500">
                        <p className="font-semibold">{plan.hotel.name}</p>
                        <p className="text-sm text-stone-500">{plan.hotel.stars ? `${plan.hotel.stars}-star · ` : `${plan.hotel.tier} · `}{plan.hotel.rating ? `guest rating ${plan.hotel.rating}` : "no rating"}</p>
                        <p className="text-sm">{money(plan.hotel.nightly_price)} / night</p>
                        <SourceTag item={plan.hotel} />
                    </Card>
                )}
            </div>

            <div className="space-y-3">
                {plan.days.map((d, i) => (
                    <div key={d.date} className="rounded-2xl border border-stone-200 bg-white p-5">
                        <div className="mb-3 flex items-baseline justify-between">
                            <h3 className="font-semibold">Day {i + 1} · {new Date(d.date + "T12:00").toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}</h3>
                            {d.weather && <span className={`text-xs ${(d.rain_chance ?? 0) >= 60 ? "text-sky-700 font-medium" : "text-stone-500"}`}>{(d.rain_chance ?? 0) >= 60 ? "☔ " : ""}{d.weather}</span>}
                        </div>
                        <ul className="space-y-2">
                            {d.items.map((it) => (
                                <li key={it.name} className="flex items-center justify-between gap-3 text-sm">
                                    <span>
                                        <span className="mr-2 text-stone-400">{it.kind === "event" ? (it.time ?? "evening") : `${it.hours}h`}</span>
                                        {it.url ? <a href={it.url} target="_blank" rel="noreferrer" className="underline">{it.name}</a> : it.name}
                                        {it.indoor && <span className="ml-2 rounded bg-stone-100 px-1.5 text-xs text-stone-500">indoor</span>}
                                    </span>
                                    <span className="text-stone-500">{it.price_unknown ? "price on site" : it.cost ? money(it.cost) : "free"}</span>
                                </li>
                            ))}
                            {d.items.length === 0 && <li className="text-sm text-stone-400">Free time</li>}
                        </ul>
                    </div>
                ))}
            </div>

            {points.length > 0 && <AttractionsMap attractions={points} />}
        </>
    );
}

function Card({ title, accent, children }: { title: string; accent: string; children: React.ReactNode }) {
    return (
        <div className={`rounded-2xl border border-l-4 border-stone-200 bg-white p-4 ${accent}`}>
            <p className="mb-1 text-xs font-medium uppercase tracking-wide text-stone-400">{title}</p>
            {children}
        </div>
    );
}

function SourceTag({ item }: { item: any }) {
    const label = item.source === "demo" ? "sample price" : `live · ${String(item.source).replace(/_/g, " ")}`;
    return (
        <p className="mt-1 text-xs text-stone-400">
            {label}
            {item.url && <> · <a href={item.url} target="_blank" rel="noreferrer" className="underline">view</a></>}
        </p>
    );
}

function fmtTime(s: string) {
    return new Date(s).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}
