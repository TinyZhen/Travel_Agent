import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';



// Fix leaflet's default marker icon path
import 'leaflet/dist/leaflet.css';
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png',
});

export default function AttractionsMap({ attractions }: { attractions: any[] }) {
    const center = attractions.length
        ? [attractions[0].lat, attractions[0].lng]
        : [41.8781, -87.6298]; // fallback to Chicago

    return (
        <div className="h-[500px] rounded-2xl overflow-hidden shadow">
            <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {attractions.map((a, i) => (
                    <Marker key={i} position={[a.lat, a.lng]}>
                        <Popup>
                            <strong>{a.name}</strong>
                            <br />
                            {a.address}
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
}
