import { create } from "zustand";
import { corridorCoordinates, demoScenarios } from "@/data/bengaluru";
import type { AnalyzeResponse, IncidentRequest } from "@/types/api";

type PipelineStage = "idle" | "incident" | "closure" | "priority" | "retrieval" | "resource" | "copilot" | "complete";

interface IncidentState {
  form: IncidentRequest;
  selectedScenario: string;
  analysis: AnalyzeResponse | null;
  pipelineStage: PipelineStage;
  isAnalyzing: boolean;
  setForm: (patch: Partial<IncidentRequest>) => void;
  setAnalysis: (analysis: AnalyzeResponse | null) => void;
  setPipelineStage: (stage: PipelineStage) => void;
  setAnalyzing: (value: boolean) => void;
  loadScenario: (name: string) => void;
  reset: () => void;
}

const initialForm: IncidentRequest = {
  event_type: "accident",
  corridor: "Outer Ring Road",
  zone: "East",
  severity: "high",
  description: "Two-lane blockage reported on Outer Ring Road with slow-moving peak-hour traffic.",
  metadata: {
    source: "sentinel-frontend",
    latitude: corridorCoordinates["Outer Ring Road"].lat,
    longitude: corridorCoordinates["Outer Ring Road"].lng,
    landmark: corridorCoordinates["Outer Ring Road"].landmark,
  },
};

export const useIncidentStore = create<IncidentState>((set) => ({
  form: initialForm,
  selectedScenario: "",
  analysis: null,
  pipelineStage: "idle",
  isAnalyzing: false,
  setForm: (patch) => set((state) => ({ form: { ...state.form, ...patch, metadata: { ...state.form.metadata, ...patch.metadata } } })),
  setAnalysis: (analysis) => set({ analysis }),
  setPipelineStage: (pipelineStage) => set({ pipelineStage }),
  setAnalyzing: (isAnalyzing) => set({ isAnalyzing }),
  loadScenario: (name) => {
    const scenario = demoScenarios.find((item) => item.name === name);
    if (!scenario) return;
    const coord = corridorCoordinates[scenario.corridor] || corridorCoordinates["Outer Ring Road"];
    set({
      selectedScenario: name,
      form: {
        event_type: scenario.event_type,
        corridor: scenario.corridor,
        zone: scenario.zone,
        severity: scenario.severity,
        description: scenario.description,
        metadata: {
          ...scenario.metadata,
          source: "demo-scenario",
          latitude: coord.lat,
          longitude: coord.lng,
          landmark: coord.landmark,
        },
      },
    });
  },
  reset: () => set({ form: initialForm, selectedScenario: "", analysis: null, pipelineStage: "idle", isAnalyzing: false }),
}));
