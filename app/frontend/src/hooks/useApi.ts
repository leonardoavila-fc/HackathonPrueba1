import { useState, useCallback } from "react";
import axios from "axios";
import type {
  ScenarioFilters, ScenarioResponse,
  ZonesResponse, FormationResponse, TempoResponse,
  CoachAdviceRequest, CoachAdviceResponse,
} from "../types";

const BASE = "http://localhost:8000/api";

// ── Genérico ───────────────────────────────────────────────
function useRequest<T>() {
  const [data,    setData]    = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);

  const execute = useCallback(async (fn: () => Promise<T>) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fn();
      setData(result);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, execute };
}

// ── Hooks específicos ──────────────────────────────────────
export function useScenario() {
  const req = useRequest<ScenarioResponse>();
  const fetch = useCallback((filters: ScenarioFilters) => {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== undefined && v !== null && v !== "")
    );
    req.execute(() => axios.get(`${BASE}/scenario`, { params }).then(r => r.data));
  }, [req.execute]);
  return { ...req, fetch };
}

export function useZones() {
  const req = useRequest<ZonesResponse>();
  const fetch = useCallback(() => {
    req.execute(() => axios.get(`${BASE}/comparatives/zones`).then(r => r.data));
  }, [req.execute]);
  return { ...req, fetch };
}

export function useFormation() {
  const req = useRequest<FormationResponse>();
  const fetch = useCallback(() => {
    req.execute(() => axios.get(`${BASE}/comparatives/formation`).then(r => r.data));
  }, [req.execute]);
  return { ...req, fetch };
}

export function useTempo() {
  const req = useRequest<TempoResponse>();
  const fetch = useCallback(() => {
    req.execute(() => axios.get(`${BASE}/comparatives/tempo`).then(r => r.data));
  }, [req.execute]);
  return { ...req, fetch };
}

export function useCoachAdvice() {
  const req = useRequest<CoachAdviceResponse>();
  const fetch = useCallback((payload: CoachAdviceRequest) => {
    req.execute(() => axios.post(`${BASE}/coach-advice`, payload).then(r => r.data));
  }, [req.execute]);
  return { ...req, fetch };
}

export function useTeams() {
  const req = useRequest<{ teams: string[] }>();
  const fetch = useCallback(() => {
    req.execute(() => axios.get(`${BASE}/teams`).then(r => r.data));
  }, [req.execute]);
  return { ...req, fetch };
}
