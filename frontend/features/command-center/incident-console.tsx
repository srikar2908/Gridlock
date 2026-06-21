"use client";

import { RotateCcw, ScanLine, Wand2 } from "lucide-react";
import { demoScenarios } from "@/data/bengaluru";
import { useIncidentStore } from "@/stores/incidentStore";

export function IncidentConsole({ onAnalyze }: { onAnalyze: () => void }) {
  const { form, selectedScenario, setForm, loadScenario, reset, isAnalyzing } = useIncidentStore();
  const fieldRows: Array<[string, keyof Pick<typeof form, "event_type" | "corridor" | "zone" | "severity">]> = [
    ["Event Type", "event_type"],
    ["Corridor", "corridor"],
    ["Zone", "zone"],
    ["Severity", "severity"],
  ];

  return (
    <div className="flex h-full flex-col">
      <div className="space-y-3 p-4">
        <label className="block text-xs uppercase tracking-[0.14em] text-slate-400">Demo Scenario</label>
        <select
          value={selectedScenario}
          onChange={(event) => loadScenario(event.target.value)}
          className="w-full border border-slate-700 bg-[#0b1220] px-3 py-2 text-sm text-white outline-none focus:border-info"
        >
          <option value="">Select operational scenario</option>
          {demoScenarios.map((scenario) => (
            <option key={scenario.name} value={scenario.name}>
              {scenario.name}
            </option>
          ))}
        </select>
      </div>

      <div className="sentinel-scroll flex-1 space-y-4 overflow-y-auto px-4 pb-4">
        {fieldRows.map(([label, key]) => (
          <label key={key} className="block">
            <span className="mb-2 block text-xs uppercase tracking-[0.14em] text-slate-400">{label}</span>
            <input
              value={String(form[key] || "")}
              onChange={(event) => setForm({ [key]: event.target.value })}
              className="w-full border border-slate-700 bg-[#0b1220] px-3 py-2 text-sm text-white outline-none focus:border-info"
            />
          </label>
        ))}

        <label className="block">
          <span className="mb-2 block text-xs uppercase tracking-[0.14em] text-slate-400">Description</span>
          <textarea
            value={form.description}
            onChange={(event) => setForm({ description: event.target.value })}
            rows={7}
            className="w-full resize-none border border-slate-700 bg-[#0b1220] px-3 py-2 text-sm leading-6 text-white outline-none focus:border-info"
          />
        </label>

        <div className="grid grid-cols-2 gap-3 text-xs text-slate-300">
          <div className="border border-slate-700 bg-[#0b1220] p-3">
            <span className="text-slate-500">Latitude</span>
            <p className="mt-1 text-white">{form.metadata?.latitude || "12.9716"}</p>
          </div>
          <div className="border border-slate-700 bg-[#0b1220] p-3">
            <span className="text-slate-500">Longitude</span>
            <p className="mt-1 text-white">{form.metadata?.longitude || "77.5946"}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 border-t border-slate-700 p-4">
        <button
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className="col-span-2 flex items-center justify-center gap-2 bg-info px-3 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <ScanLine className="h-4 w-4" />
          Analyze Incident
        </button>
        <button
          onClick={() => loadScenario(demoScenarios[0].name)}
          className="flex items-center justify-center border border-slate-700 bg-[#0b1220] px-3 py-3 text-slate-200 hover:border-info"
          title="Load demo scenario"
        >
          <Wand2 className="h-4 w-4" />
        </button>
        <button
          onClick={reset}
          className="col-span-3 flex items-center justify-center gap-2 border border-slate-700 bg-[#0b1220] px-3 py-2 text-sm text-slate-200 hover:border-warning"
        >
          <RotateCcw className="h-4 w-4" />
          Reset
        </button>
      </div>
    </div>
  );
}
