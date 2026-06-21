"use client";

import L from "leaflet";
import { Ambulance, Car, MapPin, Shield } from "lucide-react";
import { useEffect, useMemo } from "react";
import { Circle, CircleMarker, MapContainer, Marker, Polyline, Popup, TileLayer, useMapEvents } from "react-leaflet";
import { renderToStaticMarkup } from "react-dom/server";
import { coverageAssets, corridorCoordinates, zoneCenters } from "@/data/bengaluru";
import { getRoute, reverseGeocode } from "@/services/openrouteservice";
import { useDashboardStore } from "@/stores/dashboardStore";
import { useIncidentStore } from "@/stores/incidentStore";
import { useMapStore } from "@/stores/mapStore";

const BENGALURU: [number, number] = [12.9716, 77.5946];

function iconFor(kind: "incident" | "similar" | "police" | "tow" | "ambulance") {
  const color = kind === "incident" ? "#EF4444" : kind === "similar" ? "#F59E0B" : kind === "police" ? "#3B82F6" : kind === "tow" ? "#22C55E" : "#E879F9";
  const Icon = kind === "police" ? Shield : kind === "tow" ? Car : kind === "ambulance" ? Ambulance : MapPin;
  return L.divIcon({
    className: "",
    html: renderToStaticMarkup(
      <div style={{ background: color, border: "2px solid white", width: 28, height: 28, display: "grid", placeItems: "center", boxShadow: `0 0 22px ${color}` }}>
        <Icon size={15} color="white" />
      </div>,
    ),
    iconSize: [28, 28],
    iconAnchor: [14, 28],
  });
}

function ClickReporter() {
  const setClickedPoint = useMapStore((state) => state.setClickedPoint);
  const setForm = useIncidentStore((state) => state.setForm);

  useMapEvents({
    async click(event) {
      const { lat, lng } = event.latlng;
      setClickedPoint({ lat, lng });
      setForm({ metadata: { latitude: Number(lat.toFixed(5)), longitude: Number(lng.toFixed(5)) } });
      const location = await reverseGeocode(lat, lng);
      if (location) {
        setClickedPoint({ lat, lng, area: location.area, landmark: location.landmark });
        setForm({ zone: location.area, metadata: { latitude: Number(lat.toFixed(5)), longitude: Number(lng.toFixed(5)), landmark: location.landmark } });
      }
    },
  });
  return null;
}

function resourcePositions(lat: number, lng: number) {
  return [
    { type: "police" as const, label: "Police Unit Alpha", position: [lat + 0.012, lng - 0.01] as [number, number] },
    { type: "police" as const, label: "Traffic Unit Bravo", position: [lat - 0.011, lng + 0.009] as [number, number] },
    { type: "tow" as const, label: "Tow Truck Recovery", position: [lat + 0.006, lng + 0.016] as [number, number] },
    { type: "ambulance" as const, label: "Ambulance Standby", position: [lat - 0.015, lng - 0.012] as [number, number] },
  ];
}

export function DigitalTwinMap() {
  const form = useIncidentStore((state) => state.form);
  const analysis = useIncidentStore((state) => state.analysis);
  const heatmap = useDashboardStore((state) => state.heatmap);
  const routes = useMapStore((state) => state.routes);
  const setRoutes = useMapStore((state) => state.setRoutes);
  const replayIndex = useMapStore((state) => state.replayIndex);

  const incidentPosition = useMemo<[number, number]>(() => {
    const lat = Number(form.metadata?.latitude);
    const lng = Number(form.metadata?.longitude);
    if (Number.isFinite(lat) && Number.isFinite(lng)) return [lat, lng];
    const coord = corridorCoordinates[form.corridor];
    return coord ? [coord.lat, coord.lng] : BENGALURU;
  }, [form.corridor, form.metadata]);

  useEffect(() => {
    let cancelled = false;
    async function buildRoutes() {
      if (!analysis?.closure_prediction.closure_required) {
        setRoutes({ primary: null, diversion1: null, diversion2: null });
        return;
      }
      const primaryEnd: [number, number] = [incidentPosition[0] + 0.045, incidentPosition[1] + 0.052];
      const [primary, diversion1, diversion2] = await Promise.all([
        getRoute(incidentPosition, primaryEnd),
        getRoute(incidentPosition, primaryEnd, 0.025),
        getRoute(incidentPosition, primaryEnd, -0.025),
      ]);
      if (!cancelled) setRoutes({ primary, diversion1, diversion2 });
    }
    void buildRoutes();
    return () => {
      cancelled = true;
    };
  }, [analysis?.closure_prediction.closure_required, incidentPosition, setRoutes]);

  const radius =
    analysis?.priority.priority_level === "critical" ? 2400 : analysis?.priority.priority_level === "high" ? 1800 : analysis ? 1200 : 0;
  const replayRadius = Math.max(250, radius * (replayIndex / 100));
  const similar = analysis?.similar_incidents.slice(0, 5) || [];

  return (
    <div className="relative h-full min-h-[520px] overflow-hidden">
      <MapContainer center={BENGALURU} zoom={11} scrollWheelZoom className="z-0">
        <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <ClickReporter />

        {heatmap.map((cell) => {
          const center = zoneCenters[cell.zone] || BENGALURU;
          return (
            <CircleMarker
              key={cell.zone}
              center={center}
              radius={18 + Math.min(30, cell.incident_count * 3)}
              pathOptions={{ color: "#F59E0B", fillColor: cell.risk_score > 0.7 ? "#EF4444" : "#F59E0B", fillOpacity: 0.24, weight: 1 }}
            >
              <Popup>
                <strong>{cell.zone} Hotspot</strong>
                <br />
                Incidents: {cell.incident_count}
                <br />
                Risk: {Math.round(cell.risk_score * 100)}%
              </Popup>
            </CircleMarker>
          );
        })}

        {analysis && (
          <>
            <Marker position={incidentPosition} icon={iconFor("incident")}>
              <Popup>
                <strong>{form.corridor}</strong>
                <br />
                {form.event_type}
                <br />
                Priority: {analysis.priority.priority_level}
              </Popup>
            </Marker>
            <Circle center={incidentPosition} radius={replayRadius} pathOptions={{ color: "#EF4444", fillColor: "#EF4444", fillOpacity: 0.1 }} />
            {similar.map((incident, index) => (
              <Marker
                key={incident.similar_incident_id}
                position={[incidentPosition[0] + (index + 1) * 0.011, incidentPosition[1] - (index + 1) * 0.009]}
                icon={iconFor("similar")}
              >
                <Popup>
                  <strong>{incident.similar_incident_id}</strong>
                  <br />
                  Similarity: {Math.round(incident.similarity_score * 100)}%
                  <br />
                  Clearance: {incident.clearance_time} min
                </Popup>
              </Marker>
            ))}
            {resourcePositions(incidentPosition[0], incidentPosition[1]).map((unit) => (
              <Marker key={unit.label} position={unit.position} icon={iconFor(unit.type)}>
                <Popup>{unit.label}</Popup>
              </Marker>
            ))}
          </>
        )}

        {coverageAssets.map((asset) => (
          <CircleMarker key={asset.name} center={[asset.lat, asset.lng]} radius={5} pathOptions={{ color: "#22C55E", fillColor: "#22C55E", fillOpacity: 0.75 }}>
            <Popup>
              <strong>{asset.type}</strong>
              <br />
              {asset.name}
            </Popup>
          </CircleMarker>
        ))}

        {routes.primary && <Polyline positions={routes.primary.coordinates} pathOptions={{ color: "#3B82F6", weight: 5 }} />}
        {routes.diversion1 && <Polyline positions={routes.diversion1.coordinates} pathOptions={{ color: "#22C55E", weight: 4, dashArray: "8 8" }} />}
        {routes.diversion2 && <Polyline positions={routes.diversion2.coordinates} pathOptions={{ color: "#F59E0B", weight: 4, dashArray: "6 10" }} />}
      </MapContainer>

      <div className="absolute left-4 top-4 z-[500] border border-slate-700 bg-[#08111f]/95 px-4 py-3 text-xs text-slate-200">
        <p className="font-semibold uppercase tracking-[0.16em] text-info">Bengaluru Digital Twin</p>
        <p className="mt-2 text-slate-400">Click map to report. Heat indicates live corridor risk.</p>
      </div>

      {analysis?.closure_prediction.closure_required && (
        <div className="absolute bottom-4 right-4 z-[500] w-72 border border-slate-700 bg-[#08111f]/95 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-[0.16em] text-warning">AI Diversion Planner</p>
          <div className="mt-3 space-y-2">
            {(
              [
                ["Primary", routes.primary],
                ["Diversion 1", routes.diversion1],
                ["Diversion 2", routes.diversion2],
              ] as const
            ).map(([label, route]) => (
              <div key={label} className="flex justify-between border-b border-slate-800 pb-2">
                <span>{label}</span>
                <span className="text-white">{route ? `${route.distanceKm} km / ${route.durationMin} min` : "routing..."}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
