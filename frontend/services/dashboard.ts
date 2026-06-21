import { apiFetch } from "@/services/api";
import type { CorridorMetric, DashboardIncident, DashboardResources, HeatmapCell, KPIResponse } from "@/types/api";

export const dashboardApi = {
  kpis: () => apiFetch<KPIResponse>("/api/v1/dashboard/kpis"),
  incidents: () => apiFetch<DashboardIncident[]>("/api/v1/dashboard/incidents?limit=50"),
  heatmap: () => apiFetch<HeatmapCell[]>("/api/v1/dashboard/heatmap"),
  corridors: () => apiFetch<CorridorMetric[]>("/api/v1/dashboard/corridors"),
  resources: () => apiFetch<DashboardResources>("/api/v1/dashboard/resources"),
};
