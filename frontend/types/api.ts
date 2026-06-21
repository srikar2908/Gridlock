export type Severity = "low" | "medium" | "high" | "critical";

export interface IncidentRequest {
  event_type: string;
  corridor: string;
  zone: string;
  severity?: string | null;
  description: string;
  metadata?: Record<string, string | number | boolean>;
}

export interface ClosurePrediction {
  closure_required: boolean;
  confidence: number;
  model_version: string;
}

export interface PriorityPrediction {
  priority_level: string;
  priority_score: number;
  factors: Record<string, number>;
}

export interface ClearancePrediction {
  estimated_minutes: number;
  confidence: number;
  basis: string;
}

export interface ResourceRecommendation {
  officers: number;
  tow_trucks: number;
  traffic_units: number;
  ambulance_units: number;
  officer_requirement: string;
  tow_truck_requirement: string;
  traffic_unit_requirement: string;
  ambulance_requirement: string;
  resource_level: string;
  summary: string;
  rationale: string[];
  notes: string[];
}

export interface SimilarIncident {
  similar_incident_id: string;
  similarity_score: number;
  clearance_time: number;
  historical_outcome: string;
  event_cause?: string | null;
  corridor?: string | null;
  zone?: string | null;
  outcome?: string | null;
}

export interface AnalyzeResponse {
  incident_id: string;
  closure_prediction: ClosurePrediction;
  priority: PriorityPrediction;
  clearance: ClearancePrediction;
  resources: ResourceRecommendation;
  similar_incidents: SimilarIncident[];
  causes: string[];
  recommended_actions: string[];
  copilot_summary: Record<string, unknown>;
}

export interface KPIResponse {
  total_incidents: number;
  critical_incidents: number;
  average_clearance: number;
  active_zones: number;
}

export interface DashboardIncident {
  id: string;
  event_type: string;
  corridor: string;
  zone: string;
  priority_level: string;
  priority_score: number;
  estimated_clearance: number;
  created_at?: string;
}

export interface HeatmapCell {
  zone: string;
  incident_count: number;
  risk_score: number;
}

export interface CorridorMetric {
  corridor: string;
  incident_count: number;
  average_priority: number;
  average_clearance: number;
}

export interface DashboardResources {
  available: {
    officers: number;
    tow_trucks: number;
    ambulance_units: number;
    traffic_units: number;
  };
  allocated: {
    officers: number;
    tow_trucks: number;
    ambulance_units: number;
    traffic_units: number;
  };
}

export interface RouteSummary {
  distanceKm: number;
  durationMin: number;
  coordinates: [number, number][];
}
