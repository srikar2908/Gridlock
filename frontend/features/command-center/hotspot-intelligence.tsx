"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useDashboardStore } from "@/stores/dashboardStore";

export function HotspotIntelligence() {
  const corridors = useDashboardStore((state) => state.corridors);
  const data = (corridors.length ? corridors : fallbackCorridors).slice(0, 5);

  return (
    <div className="grid h-full grid-cols-3 gap-3 p-3">
      <HotspotList title="Top Accident Corridors" items={data.map((item) => [item.corridor, item.incident_count])} />
      <HotspotList title="Top Congested Corridors" items={data.map((item) => [item.corridor, Math.round(item.average_priority * 100)])} />
      <div className="border border-slate-700 bg-[#0b1220] p-3">
        <h3 className="mb-3 text-xs uppercase tracking-[0.14em] text-slate-400">Top Delay Corridors</h3>
        <ResponsiveContainer width="100%" height={120}>
          <BarChart data={data}>
            <CartesianGrid stroke="#1f2937" vertical={false} />
            <XAxis dataKey="corridor" hide />
            <YAxis hide />
            <Tooltip contentStyle={{ background: "#111827", border: "1px solid #334155", color: "#fff" }} />
            <Bar dataKey="average_clearance" fill="#F59E0B" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function HotspotList({ title, items }: { title: string; items: [string, number][] }) {
  return (
    <div className="border border-slate-700 bg-[#0b1220] p-3">
      <h3 className="mb-3 text-xs uppercase tracking-[0.14em] text-slate-400">{title}</h3>
      <div className="space-y-2">
        {items.map(([name, value]) => (
          <div key={name} className="flex items-center justify-between text-sm">
            <span className="truncate text-slate-300">{name}</span>
            <span className="font-semibold text-white">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const fallbackCorridors = [
  { corridor: "Outer Ring Road", incident_count: 18, average_priority: 0.82, average_clearance: 74 },
  { corridor: "Silk Board", incident_count: 14, average_priority: 0.79, average_clearance: 69 },
  { corridor: "KR Puram", incident_count: 11, average_priority: 0.71, average_clearance: 61 },
  { corridor: "Hebbal", incident_count: 9, average_priority: 0.68, average_clearance: 55 },
  { corridor: "Whitefield", incident_count: 8, average_priority: 0.62, average_clearance: 48 },
];
