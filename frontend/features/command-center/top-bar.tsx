"use client";

import { Activity, Ambulance, Clock3, ShieldAlert } from "lucide-react";
import { AnimatedCounter } from "@/components/ui/animated-counter";
import { useDashboardStore } from "@/stores/dashboardStore";

export function TopBar({ loading, degraded }: { loading: boolean; degraded: boolean }) {
  const kpis = useDashboardStore((state) => state.kpis);
  const resources = useDashboardStore((state) => state.resources);
  const deployed =
    (resources?.allocated.officers || 0) +
    (resources?.allocated.tow_trucks || 0) +
    (resources?.allocated.ambulance_units || 0) +
    (resources?.allocated.traffic_units || 0);

  const items = [
    { label: "Total Incidents", value: kpis?.total_incidents || 0, icon: Activity, tone: "text-info" },
    { label: "Critical Incidents", value: kpis?.critical_incidents || 0, icon: ShieldAlert, tone: "text-critical" },
    { label: "Average Clearance", value: kpis?.average_clearance || 0, suffix: "m", icon: Clock3, tone: "text-warning" },
    { label: "Resources Deployed", value: deployed, icon: Ambulance, tone: "text-success" },
  ];

  return (
    <header className="border-b border-slate-700 bg-[#08111f] px-5 py-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-info">SENTINEL Bengaluru</p>
          <h1 className="mt-1 text-2xl font-semibold text-white">AI Traffic Command Center</h1>
        </div>
        <div className="flex items-center gap-3 text-xs uppercase tracking-[0.16em] text-slate-300">
          <span className={`h-2.5 w-2.5 ${degraded ? "bg-warning" : "bg-success"}`} />
          {loading ? "Synchronizing" : degraded ? "Backend Link Degraded" : "Live Operations"}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        {items.map((item) => (
          <div key={item.label} className="border border-slate-700 bg-card px-4 py-3">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-[0.14em] text-slate-400">{item.label}</span>
              <item.icon className={`h-4 w-4 ${item.tone}`} />
            </div>
            <div className="mt-3 text-3xl font-semibold text-white">
              <AnimatedCounter value={item.value} suffix={item.suffix} />
            </div>
          </div>
        ))}
      </div>
    </header>
  );
}
