export type UserRole = "PATIENT" | "DOCTOR" | "ADMIN" | "OWNER";
export type AppointmentStatus = "SCHEDULED" | "COMPLETED" | "CANCELLED" | "NO_SHOW";
export type PaymentStatus = "PENDING" | "PAID" | "FAILED" | "REFUNDED";
export type PaymentMethod = "CARD" | "CASH";

export type Viewer = {
  id: string;
  email: string | null;
  role: UserRole;
  first_name: string;
  last_name: string;
  phone: string | null;
  is_verified: boolean;
  specialty?: string | null;
  cabinet_number?: string | null;
};

export type AuthResponse = {
  message: string;
  user: Viewer;
};

export type UserPreview = {
  id: string;
  first_name: string;
  last_name: string;
};

export type Doctor = {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  specialty: string;
  cabinet_number: string;
  bio: string | null;
};

export type ScheduleSlot = {
  start_time: string;
  end_time: string;
  is_available: boolean;
};

export type DoctorSchedule = {
  doctor: Doctor;
  slots: ScheduleSlot[];
};

export type ScheduleShift = {
  id: string;
  doctor_id: string;
  start_time: string;
  end_time: string;
  slot_minutes: number;
  is_active: boolean;
};

export type Appointment = {
  id: string;
  patient: UserPreview;
  doctor: UserPreview;
  start_time: string;
  end_time: string;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
};

export type AppointmentListResponse = {
  items: Appointment[];
};

export type MedicalRecord = {
  id: string;
  appointment_id: string;
  patient_id: string;
  doctor_id: string;
  complaints: string;
  diagnosis: string;
  treatment_plan: string;
  created_at: string;
  updated_at: string;
};

export type Patient = {
  id: string;
  email: string | null;
  first_name: string;
  last_name: string;
  phone: string | null;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
};

export type Payment = {
  id: string;
  appointment_id: string;
  patient_id: string;
  amount: string;
  currency: string;
  status: PaymentStatus;
  method: PaymentMethod;
  created_at: string;
  updated_at: string;
};

export type ReportPeriod = {
  date_from: string;
  date_to: string;
};

export type RevenueReport = {
  period: ReportPeriod;
  total_amount: string;
  paid_transactions: number;
  pending_transactions: number;
};

export type DoctorLoadItem = {
  doctor_id: string;
  doctor_name: string;
  specialty: string;
  completed_appointments: number;
  scheduled_appointments: number;
};

export type DoctorLoadReport = {
  period: ReportPeriod;
  doctors: DoctorLoadItem[];
};

