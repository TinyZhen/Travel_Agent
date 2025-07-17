import React, { useState } from "react";
import AttractionsMap from "./AttractionsMap";

export default function TravelAgent() {
    const [prompt, setPrompt] = useState("");
    const [result, setResult] = useState<any>(null);


    const fetchPlan = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/agent", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt }),
            });
            const data = await res.json();
            console.log("Backend response:", data); // 👈 LOG
            setResult({
                summary: data.result,
                ...data.structured,
            });
        } catch (err) {
            console.error("Fetch or parse error:", err);
            setResult({ error: "Failed to get plan." });
        }
    };

    const SectionTitle = ({ children }: { children: React.ReactNode }) => (
        <h2 className="text-3xl font-bold text-gray-800 border-b border-gray-300 pb-2 mb-6">{children}</h2>
    );

    const Card = ({ image, title, subtitle, description, url, size = "default" }: any) => {
        const baseClasses = "bg-white rounded-xl shadow p-4 flex flex-col justify-between";
        const compactClasses = "gap-2 min-h-[180px]";
        const defaultClasses = "h-[400px]";

        return (
            <div className={`${baseClasses} ${size === "compact" ? compactClasses : defaultClasses}`}>
                {image && (
                    <img
                        src={image || "/placeholder.jpg"}
                        alt={title}
                        referrerPolicy="no-referrer"
                        onError={(e) => (e.currentTarget.src = "/placeholder.jpg")}
                        className="w-full h-48 object-cover rounded-lg mb-3"
                    />
                )}
                <h3 className="text-base font-bold text-gray-800 mb-1">{title}</h3>
                {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
                {description && (
                    <div className="text-sm text-gray-600 space-y-1">
                        {description}
                    </div>
                )}
                {url && (
                    <a
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-2 text-blue-600 hover:underline text-sm"
                    >
                        View More
                    </a>
                )}
            </div>
        );
    };


    const EventsSection = ({ events }: { events: any[] }) =>
        events?.length ? (
            <div>
                <SectionTitle>🎉 Events</SectionTitle>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {events.map((e, i) => (
                        <Card
                            key={i}
                            image={e.image}
                            title={e.name}
                            subtitle={e.venue}
                            description={e.date}
                            url={e.url}
                        />
                    ))}
                </div>
            </div>
        ) : null;

    const FlightsSection = ({ flights }: { flights: any[] }) =>
        flights?.length ? (
            <div>
                <SectionTitle>✈️ Flights</SectionTitle>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {flights.map((f, i) => {
                        const dep = new Date(f.departure_time).toLocaleString("en-US", {
                            month: "short",
                            day: "numeric",
                            hour: "numeric",
                            minute: "2-digit",
                            hour12: true,
                        });

                        const arr = new Date(f.arrival_time).toLocaleString("en-US", {
                            month: "short",
                            day: "numeric",
                            hour: "numeric",
                            minute: "2-digit",
                            hour12: true,
                        });

                        const price = f.price?.toFixed?.(2) ?? f.price;

                        return (
                            <Card
                                key={i}
                                title={`${f.from} → ${f.to}`}
                                subtitle={
                                    <>
                                        <p className="text-sm font-medium text-gray-800">{f.airline}</p>
                                        <p className="text-sm">Departure: {dep}</p>
                                        <p className="text-sm">Arrival: {arr}</p>
                                        <p className="text-sm font-semibold text-green-700">Price: ${price}</p>
                                    </>
                                }
                                size="compact"
                            />
                        );
                    })}
                </div>
            </div>
        ) : null;


    const HotelsSection = ({ hotels }: { hotels: any[] }) =>
        hotels?.length ? (
            <div>
                <SectionTitle>🏨 Hotels</SectionTitle>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {hotels.map((h, i) => (
                        <Card
                            key={i}
                            image={h.image}
                            title={h.name}
                            subtitle={h.address}
                            url={h.url}
                        />
                    ))}
                </div>
            </div>
        ) : null;

    const AttractionsSection = ({ attractions }: { attractions: any[] }) =>
        attractions?.length ? (
            <div>
                <SectionTitle>🌆 Attractions</SectionTitle>
                <AttractionsMap attractions={attractions} />
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
                    {attractions.map((a, i) => (
                        <Card
                            key={i}
                            image={a.image}
                            title={a.name}
                            subtitle={`⭐ ${a.rating} · ${a.reviews} reviews`}
                            description={`Category: ${a.category}`}
                            url={a.maps_url}
                        />
                    ))}
                </div>
            </div>
        ) : null;

    return (

        <div className="min-h-screen bg-gray-50 px-6 py-16">
            <div className="w-full px-6 space-y-14 ">
                <h1 className="text-4xl font-bold text-center text-blue-700">
                    🧠 This is Roameo
                </h1>

                {/* 输入区：加一层容器并加大间距 */}
                <div className="flex justify-center">
                    <div className="w-full max-w-3xl space-y-6">
                        <div className="flex flex-col sm:flex-row gap-6 items-stretch">
                            <input
                                type="text"
                                placeholder="e.g. I want to visit Chicago on May 7"
                                className="border border-gray-300 rounded-lg p-4 flex-1 shadow-sm focus:ring focus:ring-blue-200 w-full"
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                            />
                            <button
                                onClick={fetchPlan}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-lg shadow w-full sm:w-auto font-semibold"
                            >
                                Plan
                            </button>
                        </div>
                    </div>
                </div>

                {result?.summary && (
                    <div className="bg-white p-6 rounded-2xl shadow border border-gray-100 whitespace-pre-wrap">
                        <SectionTitle>📝 Plan Summary</SectionTitle>
                        <p className="text-gray-700 text-lg">
                            {typeof result.summary === "string"
                                ? result.summary
                                : result.summary?.text ?? "No summary available"}
                        </p>
                    </div>
                )}

                {result?.events && <EventsSection events={result.events} />}
                {result?.flights && <FlightsSection flights={result.flights} />}
                {result?.hotels && <HotelsSection hotels={result.hotels} />}
                {result?.attractions && <AttractionsSection attractions={result.attractions} />}

                {result?.error && (
                    <div className="text-red-500 bg-white p-4 rounded shadow border text-center">
                        Error: {result.error}
                    </div>
                )}
            </div>
        </div>
    );
}
