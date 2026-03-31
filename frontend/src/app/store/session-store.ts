import { create } from "zustand";

import type { Viewer } from "../types";

type SessionStatus = "idle" | "loading" | "authenticated" | "guest";

type SessionState = {
  viewer: Viewer | null;
  status: SessionStatus;
  setViewer: (viewer: Viewer | null) => void;
  setStatus: (status: SessionStatus) => void;
  clear: () => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  viewer: null,
  status: "idle",
  setViewer: (viewer) => set({ viewer, status: viewer ? "authenticated" : "guest" }),
  setStatus: (status) => set({ status }),
  clear: () => set({ viewer: null, status: "guest" }),
}));

