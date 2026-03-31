import { startTransition, useEffect } from "react";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Navigate, useNavigate } from "react-router-dom";

import { api } from "../app/lib/api";
import { useSessionStore } from "../app/store/session-store";
import type { Viewer } from "../app/types";
import { AppShell } from "../components/layout/app-shell";
import { Loader } from "../components/ui/loader";
import { AdminDashboard } from "../features/admin/admin-dashboard";
import { DoctorDashboard } from "../features/doctor/doctor-dashboard";
import { OwnerDashboard } from "../features/owner/owner-dashboard";
import { PatientDashboard } from "../features/patient/patient-dashboard";

function DashboardSwitch({ viewer }: { viewer: Viewer }) {
  switch (viewer.role) {
    case "PATIENT":
      return <PatientDashboard viewer={viewer} />;
    case "DOCTOR":
      return <DoctorDashboard viewer={viewer} />;
    case "ADMIN":
      return <AdminDashboard viewer={viewer} />;
    case "OWNER":
      return <OwnerDashboard viewer={viewer} />;
    default:
      return null;
  }
}

export function AppPage() {
  const navigate = useNavigate();
  const setViewer = useSessionStore((state) => state.setViewer);
  const setStatus = useSessionStore((state) => state.setStatus);
  const clear = useSessionStore((state) => state.clear);
  const viewer = useSessionStore((state) => state.viewer);

  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: () => api.auth.me(),
  });

  useEffect(() => {
    setStatus(meQuery.isLoading ? "loading" : meQuery.isError ? "guest" : "authenticated");
    if (meQuery.data) {
      startTransition(() => {
        setViewer(meQuery.data);
      });
    }
    if (meQuery.isError) {
      clear();
    }
  }, [clear, meQuery.data, meQuery.isError, meQuery.isLoading, setStatus, setViewer]);

  const logoutMutation = useMutation({
    mutationFn: api.auth.logout,
    onSuccess: () => {
      clear();
      void navigate("/");
    },
  });

  if (meQuery.isLoading) {
    return <Loader label="Відкриваємо робочий простір..." />;
  }

  const resolvedViewer = meQuery.data ?? viewer;

  if (meQuery.isError || !resolvedViewer) {
    return <Navigate replace to="/login" />;
  }

  return (
    <AppShell viewer={resolvedViewer} onLogout={() => logoutMutation.mutate()}>
      <DashboardSwitch viewer={resolvedViewer} />
    </AppShell>
  );
}
