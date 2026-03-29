/**
 * ArchonX API Client v2
 * Typed fetch wrapper for /v1/ endpoints.
 * No secrets — only needs NEXT_PUBLIC_ARCHONX_API_URL.
 */

const BASE =
  process.env.NEXT_PUBLIC_ARCHONX_API_URL ?? "http://localhost:8080";

// ─── Types ───────────────────────────────────────────────────────────

export interface Agent {
  id: string;
  name: string;
  crew: "white" | "black";
  role: string;
  position: string;
  specialty: string;
  status: string;
  health: number;
  tasks: number;
  score: number;
  soul?: boolean;
}

export interface HealthStatus {
  status: "ok" | "degraded";
  version: string;
  timestamp: string;
  services: Record<string, string | number>;
}

export interface BoardState {
  positions: Record<string, unknown>;
  [key: string]: unknown;
}

export interface DashboardState {
  [key: string]: unknown;
}

export interface CostSummary {
  total_cost_usd: number;
  budget_usd: number;
  remaining_usd: number;
  budget_used_pct: number;
  total_actions_this_hour: number;
  circuit_breaker_active: boolean;
  fallback_model: string | null;
  agents: Record<string, unknown>[];
}

export interface TheaterEvent {
  timestamp: string;
  type: string;
  agent: string;
  description: string;
  crew: string;
}

export interface CockpitOverview {
  timestamp: string;
  kernel_version: string;
  booted: boolean;
  agents: { total: number; white_crew: number; black_crew: number };
  subsystems: Record<string, boolean>;
  cost: {
    spent_usd: number;
    budget_usd: number;
    remaining_pct: number;
    circuit_breaker: boolean;
  } | null;
  machines: number;
  active_tasks: number;
  ws_clients: number;
}

export interface TaskResult {
  task_id: string;
  status: string;
  [key: string]: unknown;
}

// ─── HTTP helper ─────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

// ─── v1 endpoints ────────────────────────────────────────────────────

export const archonx = {
  health: () => apiFetch<HealthStatus>("/v1/health"),

  agents: {
    list: () =>
      apiFetch<{ agents: Agent[]; count: number }>("/v1/agents"),
    get: (id: string) => apiFetch<Agent>(`/v1/agents/${id}`),
  },

  board: {
    state: () => apiFetch<BoardState>("/v1/board"),
    dashboard: () => apiFetch<DashboardState>("/v1/board/dashboard"),
    meetings: () => apiFetch<unknown>("/v1/board/meetings"),
  },

  theater: {
    events: (limit = 50) =>
      apiFetch<{ events: TheaterEvent[]; stats: Record<string, unknown> }>(
        `/v1/theater/events?limit=${limit}`
      ),
    startSession: (viewerId: string) =>
      apiFetch<{ session_id: string; viewer_id: string }>(
        "/v1/theater/session",
        { method: "POST", body: JSON.stringify({ viewer_id: viewerId }) }
      ),
    endSession: (sessionId: string) =>
      apiFetch<{ session_id: string; tokens_spent: number }>(
        `/v1/theater/session/${sessionId}`,
        { method: "DELETE" }
      ),
  },

  cost: {
    summary: () => apiFetch<CostSummary>("/v1/cost"),
    reset: (agentId: string) =>
      apiFetch<{ reset: boolean }>("/v1/cost/reset", {
        method: "POST",
        body: JSON.stringify({ agent_id: agentId }),
      }),
  },

  tasks: {
    submit: (task: {
      message: string;
      source?: string;
      priority?: string;
      crew?: string;
    }) =>
      apiFetch<TaskResult>("/v1/tasks", {
        method: "POST",
        body: JSON.stringify(task),
      }),
    status: (taskId: string) =>
      apiFetch<{ status: string; task_id: string }>(`/v1/tasks/${taskId}`),
  },

  cockpit: {
    overview: () => apiFetch<CockpitOverview>("/v1/cockpit/overview"),
    submitTask: (task: Record<string, unknown>) =>
      apiFetch<unknown>("/v1/cockpit/task", {
        method: "POST",
        body: JSON.stringify(task),
      }),
    hermesCouncil: (question: string) =>
      apiFetch<unknown>("/v1/cockpit/hermes/council", {
        method: "POST",
        body: JSON.stringify({ question }),
      }),
    popebotSend: (channel: string, message: string) =>
      apiFetch<unknown>("/v1/cockpit/popebot/send", {
        method: "POST",
        body: JSON.stringify({ channel, message }),
      }),
  },

  flywheel: {
    stats: () => apiFetch<Record<string, unknown>>("/v1/flywheel"),
  },
};

// ─── WebSocket helper ────────────────────────────────────────────────

export type WSMessage =
  | { type: "pong" }
  | { type: "board"; data: BoardState }
  | { type: "dashboard"; data: DashboardState }
  | { event: string; data: unknown };

export function connectWS(
  onMessage: (msg: WSMessage) => void,
  onClose?: () => void
): WebSocket {
  const wsUrl = BASE.replace(/^http/, "ws") + "/ws";
  const ws = new WebSocket(wsUrl);

  ws.onmessage = (ev) => {
    try {
      onMessage(JSON.parse(ev.data));
    } catch {
      /* ignore malformed */
    }
  };

  ws.onclose = () => onClose?.();

  ws.onopen = () => {
    // Auto-subscribe to board updates
    ws.send(JSON.stringify({ type: "subscribe_board" }));
  };

  return ws;
}
