import axios from "axios";

// Use relative URL in browser (routes through Next.js proxy → no CORS)
// Use absolute URL in SSR if NEXT_PUBLIC_API_URL is set
const API_BASE =
  typeof window !== "undefined"
    ? ""
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Request interceptor — attach JWT token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("buildwise_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("buildwise_token");
      localStorage.removeItem("buildwise_user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ── Error Formatter Helper ───────────────────────────────────────────────────

export function getErrorMessage(err: any, fallback: string = "An error occurred"): string {
  const detail = err?.response?.data?.detail;
  if (!detail) {
    if (err?.code === "ERR_NETWORK") {
      return "Cannot connect to backend server. Please make sure backend is running.";
    }
    if (err?.message && typeof err.message === "string") {
      return err.message;
    }
    return fallback;
  }
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (typeof item === "object" && item !== null) {
          const loc = Array.isArray(item.loc) ? item.loc.filter((l: string) => l !== "body").join(".") : "";
          const msg = item.msg || JSON.stringify(item);
          return loc ? `${loc}: ${msg}` : msg;
        }
        return String(item);
      })
      .join("; ");
  }
  if (typeof detail === "object" && detail !== null) {
    return detail.msg || detail.message || JSON.stringify(detail);
  }
  return String(detail);
}

// ── API Helpers ───────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) => api.post("/auth/login", { email, password }),
  register: (data: Record<string, unknown>) => api.post("/auth/register", data),
  me: () => api.get("/auth/me"),
  updateMe: (data: Record<string, unknown>) => api.put("/auth/me", data),
};

export const complaintsApi = {
  list: (params?: Record<string, unknown>) => api.get("/complaints", { params }),
  create: (data: Record<string, unknown>) => api.post("/complaints", data),
  get: (id: string) => api.get(`/complaints/${id}`),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/complaints/${id}`, data),
  delete: (id: string) => api.delete(`/complaints/${id}`),
  stats: (buildingId?: string) => api.get("/complaints/stats/summary", { params: { building_id: buildingId } }),
};

export const buildingsApi = {
  list: () => api.get("/buildings"),
  create: (data: Record<string, unknown>) => api.post("/buildings", data),
  get: (id: string) => api.get(`/buildings/${id}`),
  delete: (id: string) => api.delete(`/buildings/${id}`),
};

export const techniciansApi = {
  list: (params?: Record<string, unknown>) => api.get("/technicians", { params }),
  create: (data: Record<string, unknown>) => api.post("/technicians", data),
  get: (id: string) => api.get(`/technicians/${id}`),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/technicians/${id}`, data),
  available: (params?: Record<string, unknown>) => api.get("/technicians/available", { params }),
};

export const analyticsApi = {
  dashboard: (buildingId?: string, days?: number) =>
    api.get("/analytics/dashboard", { params: { building_id: buildingId, days: days || 30 } }),
  technicianPerformance: () => api.get("/analytics/technician-performance"),
  buildingHealth: () => api.get("/analytics/building-health"),
  equipmentRisk: () => api.get("/analytics/equipment-risk"),
};

export const agentsApi = {
  list: () => api.get("/agents"),
  run: (complaintId: string, agentName?: string) => api.post("/agents/run", { complaint_id: complaintId, agent_name: agentName }),
  analyzeComplaint: (data: Record<string, unknown>) => api.post("/agents/analyze-complaint", data),
  ragChat: (question: string, context?: string) => api.post("/agents/rag-chat", { question, context }),
  workflowStatus: (complaintId: string) => api.get(`/agents/workflow-status/${complaintId}`),
};

export const equipmentApi = {
  list: (params?: Record<string, unknown>) => api.get("/equipment", { params }),
  create: (data: Record<string, unknown>) => api.post("/equipment", data),
  get: (id: string) => api.get(`/equipment/${id}`),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/equipment/${id}`, data),
  history: (id: string) => api.get(`/equipment/${id}/history`),
};

export const predictionsApi = {
  list: (params?: Record<string, unknown>) => api.get("/predictions", { params }),
  run: (equipmentId: string) => api.post(`/predictions/run/${equipmentId}`),
};

export const knowledgeApi = {
  list: () => api.get("/knowledge"),
  upload: (formData: FormData) => api.post("/knowledge/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
  search: (query: string, limit?: number) => api.post("/knowledge/search", { query, limit }),
  chat: (question: string, context?: string) => api.post("/knowledge/chat", { question, context }),
  delete: (id: string) => api.delete(`/knowledge/${id}`),
};

export const notificationsApi = {
  list: () => api.get("/notifications"),
  unreadCount: () => api.get("/notifications/unread-count"),
  markRead: (id: string) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.patch("/notifications/read-all"),
};

export const cvApi = {
  detect: (formData: FormData) => api.post("/cv/detect", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
  classes: () => api.get("/cv/classes"),
};

export const uploadsApi = {
  image: (formData: FormData) => api.post("/uploads/image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
  audio: (formData: FormData) => api.post("/uploads/audio", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
};
