"use client";

import { useMemo } from "react";
import { useIncidentStore } from "@/stores/incidentStore";

export function HistoricalTable() {
  const similar = useIncidentStore(
    (state) => state.analysis?.similar_incidents
  );

  const rows = useMemo(() => {
    return similar && similar.length > 0
      ? similar
      : placeholderRows;
  }, [similar]);

  return (
    <div className="h-full overflow-hidden">
      <div className="sentinel-scroll h-full overflow-auto">
        <table className="w-full min-w-[980px] border-collapse text-left text-sm">
          <thead className="sticky top-0 bg-[#08111f] text-xs uppercase tracking-[0.14em] text-slate-400">
            <tr>
              {[
                "Incident ID",
                "Similarity",
                "Clearance",
                "Outcome",
                "Event Cause",
                "Corridor",
                "Zone",
              ].map((heading) => (
                <th
                  key={heading}
                  className="border-b border-slate-700 px-4 py-3 font-semibold"
                >
                  {heading}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.map((incident) => (
              <tr
                key={incident.similar_incident_id}
                className="border-b border-slate-800 text-slate-300"
              >
                <td className="px-4 py-3 font-medium text-white">
                  {incident.similar_incident_id}
                </td>

                <td className="px-4 py-3">
                  {Math.round((incident.similarity_score || 0) * 100)}%
                </td>

                <td className="px-4 py-3">
                  {incident.clearance_time ?? "--"} min
                </td>

                <td className="px-4 py-3">
                  {incident.historical_outcome || "--"}
                </td>

                <td className="px-4 py-3">
                  {incident.event_cause || "--"}
                </td>

                <td className="px-4 py-3">
                  {incident.corridor || "--"}
                </td>

                <td className="px-4 py-3">
                  {incident.zone || "--"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const placeholderRows = [
  {
    similar_incident_id: "BLR-HIST-1172",
    similarity_score: 0.82,
    clearance_time: 74,
    historical_outcome: "Resolved with staged lane release",
    event_cause: "Peak-hour collision",
    corridor: "Outer Ring Road",
    zone: "East",
  },
  {
    similar_incident_id: "BLR-HIST-0904",
    similarity_score: 0.76,
    clearance_time: 58,
    historical_outcome: "Diversion reduced queue length",
    event_cause: "Breakdown",
    corridor: "Hebbal",
    zone: "North",
  },
];