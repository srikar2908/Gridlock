import { create } from "zustand";
import type { CorridorMetric, DashboardIncident, DashboardResources, HeatmapCell, KPIResponse } from "@/types/api";

interface DashboardState {
  kpis: KPIResponse | null;
  incidents: DashboardIncident[];
  heatmap: HeatmapCell[];
  corridors: CorridorMetric[];
  resources: DashboardResources | null;
  setDashboard: (patch: Partial<DashboardState>) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  kpis: null,
  incidents: [],
  heatmap: [],
  corridors: [],
  resources: null,
  setDashboard: (patch) => set(patch),
}));
