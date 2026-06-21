"use client";

import { motion } from "framer-motion";
import { Radio, Volume2 } from "lucide-react";
import { useEffect, useState } from "react";
import { AnimatedCounter } from "@/components/ui/animated-counter";
import { coverageAssets } from "@/data/bengaluru";
import { clamp, formatMinutes } from "@/lib/utils";
import { useDashboardStore } from "@/stores/dashboardStore";
import { useCopilotStore } from "@/stores/copilotStore";
import { useIncidentStore } from "@/stores/incidentStore";
import { useMapStore } from "@/stores/mapStore";

function confidence(value?: number) {
  return value === undefined ? "--" : `${Math.round(value * 100)}%`;
}

function copilotText(summary: Record<string, unknown> | null, fallback: string[]) {
  if (!summary) return fallback.join(" ");
  const parts = ["incident_summary", "risk_assessment", "resource_explanation", "historical_context", "commander_recommendation", "summary", "recommendation"]
    .map((key) => summary[key])
    .filter(Boolean)
    .map(String);
  return parts.length ? parts.join(" ") : fallback.join(" ");
}

export function Pipeline() {
  const stage = useIncidentStore((state) => state.pipelineStage);
  const stages = ["Incident", "Closure AI", "Priority AI", "Retrieval AI", "Resource AI", "Copilot"];
  const activeIndex = ["incident", "closure", "priority", "retrieval", "resource", "copilot", "complete"].indexOf(stage);

  return (
    <div className="border-b border-slate-700 p-4">
      <div className="flex items-center justify-between gap-2">
        {stages.map((item, index) => (
          <div key={item} className="flex flex-1 items-center gap-2">
            <motion.div
              animate={{ scale: index <= activeIndex ? 1 : 0.88, opacity: index <= activeIndex ? 1 : 0.38 }}
              className={`grid h-8 w-8 place-items-center border text-xs font-semibold ${index <= activeIndex ? "border-info bg-info/20 text-white" : "border-slate-700 text-slate-500"}`}
            >
              {index + 1}
            </motion.div>
            <span className="hidden text-[10px] uppercase tracking-[0.12em] text-slate-400 2xl:block">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AiCommandCenter() {
  const analysis = useIncidentStore((state) => state.analysis);
  const form = useIncidentStore((state) => state.form);
  const setSpeaking = useCopilotStore((state) => state.setSpeaking);
  const isSpeaking = useCopilotStore((state) => state.isSpeaking);
  const routes = useMapStore((state) => state.routes);
  const [lat, lng] = [Number(form.metadata?.latitude || 12.9716), Number(form.metadata?.longitude || 77.5946)];
  const fallback = [
    `${form.event_type} reported on ${form.corridor}.`,
    "Maintain field verification and deploy staged response units.",
    "Use corridor diversions if closure confidence crosses threshold.",
  ];
  const brief = copilotText(analysis?.copilot_summary || null, analysis ? analysis.recommended_actions : fallback);

  function speakBrief() {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(brief);
    utterance.rate = 0.92;
    utterance.onend = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  }

  const nearest = coverageAssets
    .map((asset) => ({ ...asset, distance: Math.hypot(asset.lat - lat, asset.lng - lng) * 111 }))
    .sort((a, b) => a.distance - b.distance)
    .slice(0, 3);

  return (
    <div className="sentinel-scroll h-full overflow-y-auto">
      <Pipeline />
      <div className="space-y-3 p-4">
        <CommandCard title="Closure Decision">
          <div className="flex items-center justify-between">
            <span className={`px-2 py-1 text-xs font-semibold uppercase ${analysis?.closure_prediction.closure_required ? "bg-critical/20 text-critical" : "bg-success/20 text-success"}`}>
              {analysis ? (analysis.closure_prediction.closure_required ? "Closure Required" : "Managed Open") : "Awaiting Signal"}
            </span>
            <span className="text-sm text-slate-300">{confidence(analysis?.closure_prediction.confidence)}</span>
          </div>
          <p className="mt-3 text-sm text-slate-400">Impact badge: {analysis?.priority.priority_level || "standby"}</p>
        </CommandCard>

        <CommandCard title="Priority Intelligence">
          <div className="flex items-end justify-between">
            <span className="text-2xl font-semibold capitalize text-white">{analysis?.priority.priority_level || "--"}</span>
            <span className="text-info">{analysis ? Math.round(analysis.priority.priority_score * 100) : 0}/100</span>
          </div>
          <div className="mt-3 space-y-2">
            {Object.entries(analysis?.priority.factors || { severity: 0, corridor: 0, impact: 0 }).map(([key, value]) => (
              <div key={key}>
                <div className="mb-1 flex justify-between text-xs text-slate-400">
                  <span className="capitalize">{key.replaceAll("_", " ")}</span>
                  <span>{Math.round(value * 100)}%</span>
                </div>
                <div className="h-1.5 bg-slate-800">
                  <div className="h-full bg-info" style={{ width: `${clamp(value * 100, 4, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </CommandCard>

        <CommandCard title="Clearance Estimation">
          <div className="grid grid-cols-3 gap-2 text-center">
            <Metric label="ETA" value={formatMinutes(analysis?.clearance.estimated_minutes)} />
            <Metric label="Confidence" value={confidence(analysis?.clearance.confidence)} />
            <Metric label="Median" value={formatMinutes(analysis?.similar_incidents[0]?.clearance_time || analysis?.clearance.estimated_minutes)} />
          </div>
        </CommandCard>

        <CommandCard title="Resource Allocation">
          <div className="grid grid-cols-4 gap-2 text-center">
            <Metric label="Officers" value={<AnimatedCounter value={analysis?.resources.officers || 0} />} />
            <Metric label="Tow" value={<AnimatedCounter value={analysis?.resources.tow_trucks || 0} />} />
            <Metric label="Traffic" value={<AnimatedCounter value={analysis?.resources.traffic_units || 0} />} />
            <Metric label="Amb." value={<AnimatedCounter value={analysis?.resources.ambulance_units || 0} />} />
          </div>
          <p className="mt-3 text-xs leading-5 text-slate-400">{analysis?.resources.summary || "Resource model waiting for incident analysis."}</p>
        </CommandCard>

        <CommandCard title="AI Copilot Commander Brief">
          <p className="text-sm leading-6 text-slate-300">{brief}</p>
          {analysis?.closure_prediction.closure_required && routes.diversion1 && (
            <p className="mt-3 text-xs text-success">Alternate route ready: {routes.diversion1.distanceKm} km, {routes.diversion1.durationMin} min estimated.</p>
          )}
          <button onClick={speakBrief} className="mt-4 flex w-full items-center justify-center gap-2 border border-info bg-info/10 px-3 py-2 text-sm text-white hover:bg-info/20">
            <Volume2 className="h-4 w-4" />
            {isSpeaking ? "Brief Playing" : "Generate Voice Brief"}
          </button>
        </CommandCard>

        <WhatIfSimulator />

        <CommandCard title="Coverage Intelligence">
          <div className="space-y-2">
            {nearest.map((asset) => (
              <div key={asset.name} className="flex items-center justify-between border-b border-slate-800 pb-2 text-sm">
                <span>
                  <Radio className="mr-2 inline h-3.5 w-3.5 text-success" />
                  {asset.name}
                </span>
                <span className="text-slate-400">{asset.distance.toFixed(1)} km</span>
              </div>
            ))}
          </div>
        </CommandCard>
      </div>
    </div>
  );
}

function CommandCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border border-slate-700 bg-[#0b1220] p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{title}</h3>
      {children}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="border border-slate-800 bg-card p-2">
      <div className="text-base font-semibold text-white">{value}</div>
      <div className="mt-1 text-[10px] uppercase tracking-[0.12em] text-slate-500">{label}</div>
    </div>
  );
}

function WhatIfSimulator() {
  const analysis = useIncidentStore((state) => state.analysis);
  const base = analysis?.clearance.estimated_minutes || 80;
  const [officers, setOfficers] = useState(analysis?.resources.officers || 4);
  const [tow, setTow] = useState(analysis?.resources.tow_trucks || 1);
  const [traffic, setTraffic] = useState(analysis?.resources.traffic_units || 3);

  useEffect(() => {
    setOfficers(analysis?.resources.officers || 4);
    setTow(analysis?.resources.tow_trucks || 1);
    setTraffic(analysis?.resources.traffic_units || 3);
  }, [analysis?.resources.officers, analysis?.resources.tow_trucks, analysis?.resources.traffic_units]);

  const reduction = clamp(officers * 2.5 + tow * 7 + traffic * 2, 0, 45);

  return (
    <CommandCard title="What-If Simulator">
      <div className="space-y-3 text-sm text-slate-300">
        <SliderRow label="Officers" value={officers} max={24} onChange={setOfficers} />
        <SliderRow label="Tow Trucks" value={tow} max={8} onChange={setTow} />
        <SliderRow label="Traffic Units" value={traffic} max={42} onChange={setTraffic} />
      </div>
      <div className="mt-4 border border-success/40 bg-success/10 p-3 text-sm text-success">
        Potential clearance reduction: {Math.round(reduction)} min. Adjusted ETA: {formatMinutes(Math.max(15, base - reduction))}
      </div>
    </CommandCard>
  );
}

function SliderRow({ label, value, max, onChange }: { label: string; value: number; max: number; onChange: (value: number) => void }) {
  return (
    <div>
      <div className="mb-1 flex justify-between">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <input type="range" min={0} max={max} value={value} onChange={(event) => onChange(Number(event.target.value))} className="w-full accent-blue-500" />
    </div>
  );
}
