import { create } from "zustand";
import type { RouteSummary } from "@/types/api";

interface MapState {
  clickedPoint: { lat: number; lng: number; area?: string; landmark?: string } | null;
  routes: {
    primary: RouteSummary | null;
    diversion1: RouteSummary | null;
    diversion2: RouteSummary | null;
  };
  replayIndex: number;
  setClickedPoint: (point: MapState["clickedPoint"]) => void;
  setRoutes: (routes: MapState["routes"]) => void;
  setReplayIndex: (value: number) => void;
}

export const useMapStore = create<MapState>((set) => ({
  clickedPoint: null,
  routes: { primary: null, diversion1: null, diversion2: null },
  replayIndex: 50,
  setClickedPoint: (clickedPoint) => set({ clickedPoint }),
  setRoutes: (routes) => set({ routes }),
  setReplayIndex: (replayIndex) => set({ replayIndex }),
}));
