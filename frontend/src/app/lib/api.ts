import type {
  Appointment,
  AppointmentListResponse,
  AuthResponse,
  Doctor,
  DoctorLoadReport,
  DoctorSchedule,
  MedicalRecord,
  Patient,
  Payment,
  RevenueReport,
  ScheduleShift,
  Viewer,
} from "../types";
import { readCookie } from "./cookies";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type RequestOptions = RequestInit & {
  skipRefresh?: boolean;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers ?? {});

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrfToken = readCookie("csrf_token");
    if (csrfToken) {
      headers.set("X-CSRF-Token", csrfToken);
    }
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (response.status === 401 && !options.skipRefresh && !path.startsWith("/auth/")) {
    const refreshed = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (refreshed.ok) {
      return request<T>(path, { ...options, skipRefresh: true });
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Сталася помилка." }));
    throw new Error(body.detail ?? "Сталася помилка.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  auth: {
    me: () => request<Viewer>("/auth/me", { skipRefresh: true }),
    login: (payload: { email: string; password: string }) =>
      request<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
        skipRefresh: true,
      }),
    register: (payload: { email: string; password: string; first_name: string; last_name: string; phone?: string }) =>
      request<AuthResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
        skipRefresh: true,
      }),
    logout: () =>
      request<{ message: string }>("/auth/logout", {
        method: "POST",
      }),
  },
  doctors: {
    list: (specialty?: string) =>
      request<Doctor[]>(`/doctors${specialty ? `?specialty=${encodeURIComponent(specialty)}` : ""}`),
  },
  schedules: {
    list: (params?: { specialty?: string; date_from?: string; date_to?: string }) => {
      const query = new URLSearchParams();
      if (params?.specialty) query.set("specialty", params.specialty);
      if (params?.date_from) query.set("date_from", params.date_from);
      if (params?.date_to) query.set("date_to", params.date_to);
      const suffix = query.size > 0 ? `?${query.toString()}` : "";
      return request<DoctorSchedule[]>(`/schedules${suffix}`);
    },
    listShifts: () => request<ScheduleShift[]>("/schedules/shifts"),
    createShift: (payload: {
      doctor_id: string;
      start_time: string;
      end_time: string;
      slot_minutes: number;
      is_active: boolean;
    }) =>
      request<ScheduleShift>("/schedules/shifts", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
  appointments: {
    listMine: () => request<AppointmentListResponse>("/appointments/mine"),
    listAll: () => request<Appointment[]>("/appointments"),
    book: (payload: { doctor_id: string; start_time: string }) =>
      request<Appointment>("/appointments", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    cancel: (appointmentId: string) =>
      request<Appointment>(`/appointments/${appointmentId}/cancel`, {
        method: "PATCH",
      }),
    updateStatus: (appointmentId: string, status: string) =>
      request<Appointment>(`/appointments/${appointmentId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
  },
  medicalRecords: {
    listMine: () => request<MedicalRecord[]>("/medical-records/mine"),
    listByPatient: (patientId: string) => request<MedicalRecord[]>(`/medical-records/patient/${patientId}`),
    upsert: (payload: {
      appointment_id: string;
      complaints: string;
      diagnosis: string;
      treatment_plan: string;
    }) =>
      request<MedicalRecord>("/medical-records", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
  users: {
    listPatients: () => request<Patient[]>("/users/patients"),
    createPatient: (payload: {
      email?: string;
      first_name: string;
      last_name: string;
      phone?: string;
      is_verified?: boolean;
    }) =>
      request<Patient>("/users/patients", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    updatePatient: (
      patientId: string,
      payload: {
        email?: string;
        first_name?: string;
        last_name?: string;
        phone?: string;
        is_verified?: boolean;
      },
    ) =>
      request<Patient>(`/users/patients/${patientId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
  },
  payments: {
    list: () => request<Payment[]>("/payments"),
    create: (payload: {
      appointment_id: string;
      amount: number;
      currency: string;
      status: string;
      method: string;
    }) =>
      request<Payment>("/payments", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
  reports: {
    revenue: (dateFrom: string, dateTo: string) =>
      request<RevenueReport>(`/reports/revenue?date_from=${encodeURIComponent(dateFrom)}&date_to=${encodeURIComponent(dateTo)}`),
    doctorLoad: (dateFrom: string, dateTo: string) =>
      request<DoctorLoadReport>(
        `/reports/doctor-load?date_from=${encodeURIComponent(dateFrom)}&date_to=${encodeURIComponent(dateTo)}`,
      ),
  },
};

