import { useEffect, useState } from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { api } from "../../app/lib/api";
import { appointmentStatusLabel, formatCurrency, formatDateTime, paymentStatusLabel } from "../../app/lib/format";
import type { Patient, Viewer } from "../../app/types";
import { Card } from "../../components/ui/card";
import { EmptyState } from "../../components/ui/empty-state";
import { CalendarIcon, ClipboardIcon, ShieldCheckIcon, TrendingUpIcon, UsersIcon } from "../../components/ui/icons";
import { MetricCard } from "../../components/ui/metric-card";

const patientSchema = z.object({
  email: z.string().email("Вкажіть коректний email.").optional().or(z.literal("")),
  first_name: z.string().min(2, "Вкажіть ім’я."),
  last_name: z.string().min(2, "Вкажіть прізвище."),
  phone: z.string().optional(),
  is_verified: z.boolean(),
});

const shiftSchema = z.object({
  doctor_id: z.string().min(1, "Оберіть лікаря."),
  start_time: z.string().min(1, "Вкажіть початок зміни."),
  end_time: z.string().min(1, "Вкажіть завершення зміни."),
  slot_minutes: z.coerce.number().min(15).max(120),
  is_active: z.boolean(),
});

const paymentSchema = z.object({
  appointment_id: z.string().min(1, "Оберіть візит."),
  amount: z.coerce.number().positive("Вкажіть суму."),
  currency: z.string().min(3).max(3),
  status: z.enum(["PENDING", "PAID", "FAILED", "REFUNDED"]),
  method: z.enum(["CARD", "CASH"]),
});

type PatientFormValues = z.infer<typeof patientSchema>;
type ShiftFormValues = z.infer<typeof shiftSchema>;
type PaymentFormValues = z.infer<typeof paymentSchema>;

type AdminDashboardProps = {
  viewer: Viewer;
};

export function AdminDashboard({ viewer }: AdminDashboardProps) {
  const queryClient = useQueryClient();
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);

  const patientsQuery = useQuery({
    queryKey: ["patients"],
    queryFn: () => api.users.listPatients(),
  });
  const doctorsQuery = useQuery({
    queryKey: ["doctors"],
    queryFn: () => api.doctors.list(),
  });
  const shiftsQuery = useQuery({
    queryKey: ["shifts"],
    queryFn: () => api.schedules.listShifts(),
  });
  const appointmentsQuery = useQuery({
    queryKey: ["appointments", "all"],
    queryFn: () => api.appointments.listAll(),
  });
  const paymentsQuery = useQuery({
    queryKey: ["payments"],
    queryFn: () => api.payments.list(),
  });

  const patientForm = useForm<PatientFormValues>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      email: "",
      first_name: "",
      last_name: "",
      phone: "",
      is_verified: true,
    },
  });

  const shiftForm = useForm<ShiftFormValues>({
    resolver: zodResolver(shiftSchema),
    defaultValues: {
      doctor_id: "",
      start_time: "",
      end_time: "",
      slot_minutes: 30,
      is_active: true,
    },
  });

  const paymentForm = useForm<PaymentFormValues>({
    resolver: zodResolver(paymentSchema),
    defaultValues: {
      appointment_id: "",
      amount: 850,
      currency: "UAH",
      status: "PAID",
      method: "CARD",
    },
  });

  useEffect(() => {
    if (editingPatient) {
      patientForm.reset({
        email: editingPatient.email ?? "",
        first_name: editingPatient.first_name,
        last_name: editingPatient.last_name,
        phone: editingPatient.phone ?? "",
        is_verified: editingPatient.is_verified,
      });
    }
  }, [editingPatient, patientForm]);

  const patientMutation = useMutation({
    mutationFn: async (values: PatientFormValues) => {
      if (editingPatient) {
        return api.users.updatePatient(editingPatient.id, {
          ...values,
          email: values.email || undefined,
          phone: values.phone || undefined,
        });
      }
      return api.users.createPatient({
        ...values,
        email: values.email || undefined,
        phone: values.phone || undefined,
      });
    },
    onSuccess: async () => {
      setEditingPatient(null);
      patientForm.reset({
        email: "",
        first_name: "",
        last_name: "",
        phone: "",
        is_verified: true,
      });
      await queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });

  const shiftMutation = useMutation({
    mutationFn: (values: ShiftFormValues) =>
      api.schedules.createShift({
        doctor_id: values.doctor_id,
        start_time: values.start_time,
        end_time: values.end_time,
        slot_minutes: values.slot_minutes,
        is_active: values.is_active,
      }),
    onSuccess: async () => {
      shiftForm.reset({
        doctor_id: "",
        start_time: "",
        end_time: "",
        slot_minutes: 30,
        is_active: true,
      });
      await queryClient.invalidateQueries({ queryKey: ["shifts"] });
    },
  });

  const paymentMutation = useMutation({
    mutationFn: (values: PaymentFormValues) => api.payments.create(values),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["payments"] }),
        queryClient.invalidateQueries({ queryKey: ["appointments", "all"] }),
      ]);
    },
  });

  const patients = patientsQuery.data ?? [];
  const shifts = shiftsQuery.data ?? [];
  const payments = paymentsQuery.data ?? [];
  const appointments = appointmentsQuery.data ?? [];
  const paidPayments = payments.filter((payment) => payment.status === "PAID").length;
  const activeShifts = shifts.filter((shift) => shift.is_active).length;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard
          description="Координація пацієнтів, змін і фінансових подій у єдиному операційному ритмі."
          icon={<ShieldCheckIcon className="h-5 w-5" />}
          label="Операційна роль"
          tone="teal"
          value={`${viewer.first_name} ${viewer.last_name}`}
        />
        <MetricCard
          description={`${activeShifts} активних змін уже опубліковано для запису пацієнтів.`}
          icon={<UsersIcon className="h-5 w-5" />}
          label="Пацієнти"
          tone="indigo"
          value={patients.length}
        />
        <MetricCard
          description="Кількість успішно проведених транзакцій у поточній базі."
          icon={<TrendingUpIcon className="h-5 w-5" />}
          label="Оплати зафіксовано"
          tone="coral"
          value={paidPayments}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="space-y-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
                <span className="icon-chip">
                  <UsersIcon className="h-5 w-5" />
                </span>
                {editingPatient ? "Редагування пацієнта" : "Створення пацієнта"}
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                Додавайте профілі з реєстратури та швидко перемикайтеся між контактами без зайвих переходів.
              </p>
            </div>
            {editingPatient ? (
              <button
                className="btn-secondary"
                onClick={() => {
                  setEditingPatient(null);
                  patientForm.reset({
                    email: "",
                    first_name: "",
                    last_name: "",
                    phone: "",
                    is_verified: true,
                  });
                }}
                type="button"
              >
                Скасувати редагування
              </button>
            ) : null}
          </div>

          <form className="space-y-4" onSubmit={patientForm.handleSubmit((values) => patientMutation.mutate(values))}>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Ім’я</label>
                <input className="field" type="text" {...patientForm.register("first_name")} />
                <p className="mt-2 text-sm text-rose-600">{patientForm.formState.errors.first_name?.message}</p>
              </div>
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Прізвище</label>
                <input className="field" type="text" {...patientForm.register("last_name")} />
                <p className="mt-2 text-sm text-rose-600">{patientForm.formState.errors.last_name?.message}</p>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Email</label>
                <input className="field" type="email" {...patientForm.register("email")} />
                <p className="mt-2 text-sm text-rose-600">{patientForm.formState.errors.email?.message}</p>
              </div>
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Телефон</label>
                <input className="field" type="text" {...patientForm.register("phone")} />
              </div>
            </div>

            <label className="flex items-center gap-3 rounded-2xl border border-slate-200/70 bg-white/75 px-4 py-3 text-sm text-slate-700">
              <input type="checkbox" {...patientForm.register("is_verified")} />
              Профіль верифіковано
            </label>

            {patientMutation.error ? <p className="text-sm text-rose-600">{patientMutation.error.message}</p> : null}
            <button className="btn-primary" disabled={patientMutation.isPending} type="submit">
              {patientMutation.isPending ? "Зберігаємо..." : editingPatient ? "Оновити профіль" : "Створити профіль"}
            </button>
          </form>

          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-slate-900">Список пацієнтів</h3>
            {patients.length ? (
              patients.map((patient) => (
                <button
                  className="flex w-full items-center justify-between rounded-[22px] border border-slate-200/70 bg-white/85 px-4 py-3 text-left transition hover:-translate-y-0.5 hover:border-cyan-300"
                  key={patient.id}
                  onClick={() => setEditingPatient(patient)}
                  type="button"
                >
                  <span>
                    <span className="block font-semibold text-slate-900">
                      {patient.first_name} {patient.last_name}
                    </span>
                    <span className="block text-sm text-slate-600">{patient.phone || patient.email || "Без контактів"}</span>
                  </span>
                  <span className="tag">{patient.is_verified ? "Верифіковано" : "Очікує"}</span>
                </button>
              ))
            ) : (
              <EmptyState title="Поки без пацієнтів" description="Перший профіль можна створити через форму вище за кілька секунд." />
            )}
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="space-y-4">
            <div>
              <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
                <span className="icon-chip">
                  <CalendarIcon className="h-5 w-5" />
                </span>
                Розклад клініки
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                Публікуйте зміни лікарів і одразу відкривайте нові слоти в пацієнтському записі.
              </p>
            </div>

            <form className="space-y-4" onSubmit={shiftForm.handleSubmit((values) => shiftMutation.mutate(values))}>
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Лікар</label>
                <select className="field" {...shiftForm.register("doctor_id")}>
                  <option value="">Оберіть лікаря</option>
                  {doctorsQuery.data?.map((doctor) => (
                    <option key={doctor.user_id} value={doctor.user_id}>
                      {doctor.first_name} {doctor.last_name} • {doctor.specialty}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">Початок</label>
                  <input className="field" type="datetime-local" {...shiftForm.register("start_time")} />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">Завершення</label>
                  <input className="field" type="datetime-local" {...shiftForm.register("end_time")} />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">Тривалість слоту</label>
                  <input className="field" type="number" {...shiftForm.register("slot_minutes")} />
                </div>
                <label className="flex items-center gap-3 rounded-2xl border border-slate-200/70 bg-white/75 px-4 py-3 text-sm text-slate-700 sm:mt-7">
                  <input type="checkbox" {...shiftForm.register("is_active")} />
                  Зміна активна
                </label>
              </div>

              {shiftMutation.error ? <p className="text-sm text-rose-600">{shiftMutation.error.message}</p> : null}
              <button className="btn-primary" disabled={shiftMutation.isPending} type="submit">
                Додати зміну
              </button>
            </form>

            <div className="space-y-3">
              {shifts.slice(0, 6).map((shift) => {
                const doctor = doctorsQuery.data?.find((item) => item.user_id === shift.doctor_id);
                return (
                  <div className="rounded-[22px] border border-slate-200/70 bg-white/85 px-4 py-3" key={shift.id}>
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold text-slate-900">
                        {doctor ? `${doctor.first_name} ${doctor.last_name}` : shift.doctor_id}
                      </p>
                      <span className="tag">{shift.is_active ? "Активна" : "Чернетка"}</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">
                      {formatDateTime(shift.start_time)} - {formatDateTime(shift.end_time)}
                    </p>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card className="space-y-4">
            <div>
              <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
                <span className="icon-chip">
                  <ClipboardIcon className="h-5 w-5" />
                </span>
                Оплати
              </h2>
              <p className="mt-2 text-sm text-slate-600">Фіксуйте транзакції по завершених або запланованих візитах без ручних таблиць.</p>
            </div>

            <form className="space-y-4" onSubmit={paymentForm.handleSubmit((values) => paymentMutation.mutate(values))}>
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Візит</label>
                <select className="field" {...paymentForm.register("appointment_id")}>
                  <option value="">Оберіть візит</option>
                  {appointments.map((appointment) => (
                    <option key={appointment.id} value={appointment.id}>
                      {appointment.patient.first_name} {appointment.patient.last_name} • {formatDateTime(appointment.start_time)} •{" "}
                      {appointmentStatusLabel(appointment.status)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <input className="field" type="number" step="0.01" {...paymentForm.register("amount")} />
                <input className="field" type="text" {...paymentForm.register("currency")} />
                <select className="field" {...paymentForm.register("method")}>
                  <option value="CARD">Картка</option>
                  <option value="CASH">Готівка</option>
                </select>
              </div>

              <select className="field" {...paymentForm.register("status")}>
                <option value="PAID">Оплачено</option>
                <option value="PENDING">Очікує</option>
                <option value="FAILED">Помилка</option>
                <option value="REFUNDED">Повернено</option>
              </select>

              {paymentMutation.error ? <p className="text-sm text-rose-600">{paymentMutation.error.message}</p> : null}
              <button className="btn-primary" disabled={paymentMutation.isPending} type="submit">
                Зафіксувати оплату
              </button>
            </form>

            <div className="space-y-3">
              {payments.length ? (
                payments.map((payment) => (
                  <div className="rounded-[22px] border border-slate-200/70 bg-white/85 px-4 py-3" key={payment.id}>
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold text-slate-900">{formatCurrency(payment.amount)}</p>
                      <span className="tag">{paymentStatusLabel(payment.status)}</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{formatDateTime(payment.created_at)}</p>
                  </div>
                ))
              ) : (
                <EmptyState title="Оплат поки немає" description="Першу оплату можна додати через форму вище." />
              )}
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
