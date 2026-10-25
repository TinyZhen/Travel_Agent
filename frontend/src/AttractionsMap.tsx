import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';



// Fix leaflet's default marker icon path
import 'leaflet/dist/leaflet.css';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl });

export default function AttractionsMap({ attractions }: { attractions: any[] }) {
    // Remount when the city changes; MapContainer ignores later `center` updates.
    const key = attractions.map((a) => a.name).join('|');
    const center: [number, number] = attractions.length
        ? [attractions[0].lat, attractions[0].lng]
        : [41.8781, -87.6298]; // fallback to Chicago

    return (
        <div className="h-[380px] overflow-hidden rounded-2xl border border-stone-200">
            <MapContainer key={key} center={center} zoom={12} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {attractions.map((a, i) => (
                    <Marker key={i} position={[a.lat, a.lng]}>
                        <Popup>
                            <strong>{a.name}</strong>
                            <br />
                            {a.kind === 'event' ? a.time : `${a.hours}h · ${a.cost ? '$' + a.cost : 'free'}`}
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
}
