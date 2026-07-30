import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  phone?: string;
  avatar_url?: string;
  building_id?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, user) => {
        localStorage.setItem("buildwise_token", token);
        localStorage.setItem("buildwise_user", JSON.stringify(user));
        set({ token, user, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem("buildwise_token");
        localStorage.removeItem("buildwise_user");
        set({ token: null, user: null, isAuthenticated: false });
        window.location.href = "/login";
      },
    }),
    { name: "buildwise-auth" }
  )
);

// ── UI Store ──────────────────────────────────────────────────────────────────
interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebar: (open: boolean) => void;
}

export const useUIStore = create<UIState>()((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebar: (open) => set({ sidebarOpen: open }),
}));
