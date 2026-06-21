import { apiFetch } from "@/services/api";
import type { AnalyzeResponse, IncidentRequest } from "@/types/api";

export function analyzeIncident(payload: IncidentRequest) {
  return apiFetch<AnalyzeResponse>("/api/v1/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
