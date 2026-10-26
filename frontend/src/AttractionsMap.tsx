import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export const DAY_COLORS = ['#0f766e', '#c2410c', '#7c3aed', '#0369a1', '#be123c', '#4d7c0f'];

type Stop = { name: string; lat: number; lng: number; kind: string; start?: string };
type Day = { date: string; items: any[] };

const numberIcon = (n: number | string, color: string) =>
    L.divIcon({
        className: '',
        html: `<div style="background:${color};color:#fff;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:600 12px system-ui;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.35)">${n}</div>`,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
    });

// Walking route along real streets (OpenStreetMap / FOSSGIS OSRM); straight dashed line if unavailable.
async function fetchRoute(stops: Stop[]): Promise<[number, number][] | null> {
    if (stops.length < 2) return null;
    const coords = stops.map((s) => `${s.lng},${s.lat}`).join(';');
    try {
        const res = await fetch(`https://routing.openstreetmap.de/routed-foot/route/v1/driving/${coords}?overview=full&geometries=geojson`);
        const data = await res.json();
        const line = data?.routes?.[0]?.geometry?.coordinates;
        return line ? line.map(([lng, lat]: [number, number]) => [lat, lng]) : null;
    } catch {
        return null;
    }
}

function FitBounds({ points }: { points: [number, number][] }) {
    const map = useMap();
    useEffect(() => {
        if (points.length) map.fitBounds(L.latLngBounds(points), { padding: [40, 40], maxZoom: 15 });
    }, [map, JSON.stringify(points)]);
    return null;
}

export default function TripMap({ days, hotel, selected, onSelect }: {
    days: Day[]; hotel?: any; selected: number | null; onSelect: (d: number | null) => void;
}) {
    // Each day: hotel → stops in visiting order (→ hotel, except on the last day).
    const dayStops: Stop[][] = useMemo(() => days.map((d, i) => {
        const stops: Stop[] = d.items.filter((it) => it.kind === 'attraction' && it.lat != null);
        if (!hotel?.lat || !stops.length) return stops;
        const h = { name: hotel.name, lat: hotel.lat, lng: hotel.lng, kind: 'hotel' };
        return i === days.length - 1 ? [h, ...stops] : [h, ...stops, h];
    }), [days, hotel]);

    const [routes, setRoutes] = useState<([number, number][] | null)[]>([]);
    useEffect(() => {
        let alive = true;
        Promise.all(dayStops.map(fetchRoute)).then((r) => alive && setRoutes(r));
        return () => { alive = false; };
    }, [JSON.stringify(dayStops)]);

    const visible = days.map((_, i) => selected === null || selected === i);
    const focus: [number, number][] = dayStops.flatMap((s, i) => (visible[i] ? s.map((p) => [p.lat, p.lng] as [number, number]) : []));
    const center: [number, number] = focus[0] ?? [40.7128, -74.006];

    return (
        <div className="overflow-hidden rounded-2xl border border-stone-200 bg-white">
            <div className="flex flex-wrap items-center gap-2 border-b border-stone-100 px-4 py-3">
                <span className="mr-1 text-sm font-semibold">Route</span>
                <button onClick={() => onSelect(null)} className={`rounded-full px-3 py-1 text-xs ${selected === null ? 'bg-stone-800 text-white' : 'bg-stone-100'}`}>All days</button>
                {days.map((d, i) => (
                    <button key={d.date} onClick={() => onSelect(i)}
                        className="rounded-full px-3 py-1 text-xs"
                        style={selected === i ? { background: DAY_COLORS[i % 6], color: '#fff' } : { background: '#f5f5f4' }}>
                        Day {i + 1}
                    </button>
                ))}
                <span className="ml-auto text-xs text-stone-400">routes along streets · OpenStreetMap</span>
            </div>
            <div className="h-[420px]">
                <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
                    <TileLayer attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    <FitBounds points={focus} />
                    {dayStops.map((stops, i) => visible[i] && (
                        <Polyline key={`r${i}`} positions={routes[i] ?? stops.map((s) => [s.lat, s.lng] as [number, number])}
                            pathOptions={{ color: DAY_COLORS[i % 6], weight: 4, opacity: 0.8, dashArray: routes[i] ? undefined : '6 8' }} />
                    ))}
                    {dayStops.map((stops, i) => visible[i] && stops.filter((s) => s.kind !== 'hotel').map((s, j) => (
                        <Marker key={`m${i}-${j}`} position={[s.lat, s.lng]} icon={numberIcon(j + 1, DAY_COLORS[i % 6])}>
                            <Popup><strong>Day {i + 1} · stop {j + 1}</strong><br />{s.name}{s.start ? <><br />{s.start}</> : null}</Popup>
                        </Marker>
                    )))}
                    {hotel?.lat && (
                        <Marker position={[hotel.lat, hotel.lng]} icon={numberIcon('H', '#1f2a2e')}>
                            <Popup><strong>{hotel.name}</strong><br />Your hotel</Popup>
                        </Marker>
                    )}
                </MapContainer>
            </div>
        </div>
    );
}
