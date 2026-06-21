import { useQueries } from "@tanstack/react-query";
import { useEffect } from "react";
import { dashboardApi } from "@/services/dashboard";
import { useDashboardStore } from "@/stores/dashboardStore";

export function useDashboardData() {
  const setDashboard = useDashboardStore((state) => state.setDashboard);
  const results = useQueries({
    queries: [
      { queryKey: ["dashboard", "kpis"], queryFn: dashboardApi.kpis, refetchInterval: 30000, retry: 2, staleTime: 15000 },
      { queryKey: ["dashboard", "incidents"], queryFn: dashboardApi.incidents, refetchInterval: 30000, retry: 2, staleTime: 15000 },
      { queryKey: ["dashboard", "heatmap"], queryFn: dashboardApi.heatmap, refetchInterval: 30000, retry: 2, staleTime: 15000 },
      { queryKey: ["dashboard", "corridors"], queryFn: dashboardApi.corridors, refetchInterval: 45000, retry: 2, staleTime: 20000 },
      { queryKey: ["dashboard", "resources"], queryFn: dashboardApi.resources, refetchInterval: 45000, retry: 2, staleTime: 20000 },
    ],
  });

  useEffect(() => {
    const [kpis, incidents, heatmap, corridors, resources] = results;
    setDashboard({
      kpis: kpis.data ?? null,
      incidents: incidents.data ?? [],
      heatmap: heatmap.data ?? [],
      corridors: corridors.data ?? [],
      resources: resources.data ?? null,
    });
  }, [results, setDashboard]);

  return {
    isLoading: results.some((result) => result.isLoading),
    isError: results.some((result) => result.isError),
    refetchAll: () => results.forEach((result) => void result.refetch()),
  };
}
