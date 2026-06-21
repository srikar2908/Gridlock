import type { RouteSummary } from "@/types/api";

const ORS_API_KEY = process.env.NEXT_PUBLIC_ORS_API_KEY || "";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8000";

function toLatLngPair(pair: [number, number]): [number, number] {
  return [pair[1], pair[0]];
}

export async function getRoute(
  start: [number, number],
  end: [number, number],
  offset = 0
): Promise<RouteSummary | null> {
  if (!ORS_API_KEY) {
    console.warn("ORS API Key missing");
    return null;
  }

  const shiftedEnd: [number, number] = [
    end[0] + offset,
    end[1] - offset,
  ];

  try {
    const url = `${API_BASE}/api/v1/ors/directions`;

    console.log("Routing URL:", url);

    const response = await fetch(url, {
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

    console.log("Route Status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("ORS Error:", errorText);
      return null;
    }

    const data = await response.json();

    console.log("ORS Response:", data);

    const feature = data?.features?.[0];

    if (!feature) {
      console.warn("No route feature returned");
      return null;
    }

    return {
      distanceKm: Number(
        (feature.properties.summary.distance / 1000).toFixed(1)
      ),
      durationMin: Number(
        (feature.properties.summary.duration / 60).toFixed(0)
      ),
      coordinates: feature.geometry.coordinates.map(toLatLngPair),
    };
  } catch (error) {
    console.error("Routing failed:", error);
    return null;
  }
}

export async function reverseGeocode(
  lat: number,
  lng: number
) {
  if (!ORS_API_KEY) return null;

  try {
    const response = await fetch(
      `${API_BASE}/api/v1/ors/reverse?lat=${lat}&lng=${lng}`
    );

    if (!response.ok) {
      console.error(
        "Reverse geocode failed:",
        response.status
      );
      return null;
    }

    const data = await response.json();

    const props = data?.features?.[0]?.properties;

    if (!props) return null;

    return {
      area:
        props.locality ||
        props.neighbourhood ||
        props.county ||
        "Bengaluru",

      landmark:
        props.name ||
        props.label ||
        "Selected map point",
    };
  } catch (error) {
    console.error("Reverse geocode error:", error);
    return null;
  }
}