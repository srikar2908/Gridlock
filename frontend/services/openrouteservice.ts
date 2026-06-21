import type { RouteSummary } from "@/types/api";

const ORS_API_KEY = process.env.NEXT_PUBLIC_ORS_API_KEY || "";
const ORS_BASE = "https://api.openrouteservice.org";

function toLatLngPair(pair: [number, number]): [number, number] {
  return [pair[1], pair[0]];
}

export async function getRoute(start: [number, number], end: [number, number], offset = 0): Promise<RouteSummary | null> {
  if (!ORS_API_KEY) return null;

  const shiftedEnd: [number, number] = [end[0] + offset, end[1] - offset];
  const response = await fetch(`${ORS_BASE}/v2/directions/driving-car/geojson`, {
    method: "POST",
    headers: {
      Authorization: ORS_API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      coordinates: [
        [start[1], start[0]],
        [shiftedEnd[1], shiftedEnd[0]],
      ],
    }),
  });

  if (!response.ok) return null;
  const data = await response.json();
  const feature = data.features?.[0];
  if (!feature) return null;

  return {
    distanceKm: Number((feature.properties.summary.distance / 1000).toFixed(1)),
    durationMin: Number((feature.properties.summary.duration / 60).toFixed(0)),
    coordinates: feature.geometry.coordinates.map(toLatLngPair),
  };
}

export async function reverseGeocode(lat: number, lng: number) {
  if (!ORS_API_KEY) return null;
  const response = await fetch(`${ORS_BASE}/geocode/reverse?api_key=${ORS_API_KEY}&point.lon=${lng}&point.lat=${lat}&size=1`);
  if (!response.ok) return null;
  const data = await response.json();
  const props = data.features?.[0]?.properties;
  if (!props) return null;
  return {
    area: props.locality || props.neighbourhood || props.county || "Bengaluru",
    landmark: props.name || props.label || "Selected map point",
  };
}
