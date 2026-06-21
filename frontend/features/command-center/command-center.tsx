"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { useCallback } from "react";
import { Panel, PanelHeader } from "@/components/ui/panel";
import { corridorCoordinates } from "@/data/bengaluru";
import { HotspotIntelligence } from "@/features/command-center/hotspot-intelligence";
import { AiCommandCenter } from "@/features/command-center/ai-command-center";
import { HistoricalTable } from "@/features/command-center/historical-table";
import { IncidentConsole } from "@/features/command-center/incident-console";
import { TopBar } from "@/features/command-center/top-bar";
import { useDashboardData } from "@/hooks/use-dashboard";
import { analyzeIncident } from "@/services/analyze";
import { useIncidentStore } from "@/stores/incidentStore";
import { useMapStore } from "@/stores/mapStore";
import type { IncidentRequest } from "@/types/api";

const DigitalTwinMap = dynamic(() => import("@/features/command-center/digital-twin-map").then((mod) => mod.DigitalTwinMap), {
  ssr: false,
  loading: () => <div className="grid h-full min-h-[520px] place-items-center bg-[#08111f] text-slate-300">Initializing Bengaluru digital twin...</div>,
});

const pipelineStages = ["incident", "closure", "priority", "retrieval", "resource", "copilot"] as const;

export function CommandCenter() {
  const queryClient = useQueryClient();
  const dashboard = useDashboardData();
  const form = useIncidentStore((state) => state.form);
  const setAnalysis = useIncidentStore((state) => state.setAnalysis);
  const setPipelineStage = useIncidentStore((state) => state.setPipelineStage);
  const setAnalyzing = useIncidentStore((state) => state.setAnalyzing);
  const setReplayIndex = useMapStore((state) => state.setReplayIndex);
  const replayIndex = useMapStore((state) => state.replayIndex);

  const mutation = useMutation({
    mutationFn: (payload: IncidentRequest) => analyzeIncident(payload),
    onMutate: () => {
      setAnalysis(null);
      setAnalyzing(true);
      setPipelineStage("incident");
      pipelineStages.forEach((stage, index) => {
        window.setTimeout(() => setPipelineStage(stage), index * 420);
      });
    },
    onSuccess: (data) => {
      setPipelineStage("complete");
      setAnalysis(data);
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
    onError: () => {
      setPipelineStage("idle");
    },
    onSettled: () => {
      setAnalyzing(false);
    },
  });

  const handleAnalyze = useCallback(() => {
    const coord = corridorCoordinates[form.corridor] || corridorCoordinates["Outer Ring Road"];
    mutation.mutate({
      ...form,
      metadata: {
        ...form.metadata,
        source: form.metadata?.source || "sentinel-frontend",
        latitude: form.metadata?.latitude || coord.lat,
        longitude: form.metadata?.longitude || coord.lng,
        landmark: form.metadata?.landmark || coord.landmark,
      },
    });
  }, [form, mutation]);

  return (
    <main className="min-h-screen bg-background text-slate-100">
      <TopBar loading={dashboard.isLoading || mutation.isPending} degraded={dashboard.isError || mutation.isError} />

      <div className="grid min-h-[calc(100vh-156px)] grid-cols-1 gap-3 p-3 xl:grid-cols-[320px_minmax(640px,1fr)_390px]">
        <Panel className="min-h-[640px] overflow-hidden">
          <PanelHeader title="Incident Intake Console" />
          <IncidentConsole onAnalyze={handleAnalyze} />
        </Panel>

        <div className="grid min-h-[640px] grid-rows-[1fr_174px] gap-3">
          <Panel className="overflow-hidden">
            <PanelHeader
              title="Bengaluru Digital Twin Map"
              action={<span className="text-xs text-slate-400">OpenStreetMap + OpenRouteService</span>}
            />
            <DigitalTwinMap />
          </Panel>

          <Panel className="overflow-hidden">
            <PanelHeader
              title="Digital Twin Replay + Hotspot Intelligence"
              action={
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span>Timeline</span>
                  <input
                    aria-label="Replay timeline"
                    type="range"
                    min={10}
                    max={100}
                    value={replayIndex}
                    onChange={(event) => setReplayIndex(Number(event.target.value))}
                    className="w-36 accent-blue-500"
                  />
                </div>
              }
            />
            <HotspotIntelligence />
          </Panel>
        </div>

        <Panel className="min-h-[640px] overflow-hidden">
          <PanelHeader title="AI Command Center" />
          <AiCommandCenter />
        </Panel>
      </div>

      <div className="px-3 pb-3">
        <Panel className="h-[260px] overflow-hidden">
          <PanelHeader title="Historical Similar Incidents" />
          <HistoricalTable />
        </Panel>
      </div>
    </main>
  );
}
