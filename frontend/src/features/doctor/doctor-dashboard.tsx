import { useEffect, useState } from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { api } from "../../app/lib/api";
import { appointmentStatusLabel, formatDateTime } from "../../app/lib/format";
import type { Appointment, Viewer } from "../../app/types";
import { Card } from "../../components/ui/card";
import { EmptyState } from "../../components/ui/empty-state";
import { CalendarIcon, ClipboardIcon, HeartPulseIcon, StethoscopeIcon } from "../../components/ui/icons";
import { MetricCard } from "../../components/ui/metric-card";
import { StatusPill } from "../../components/ui/status-pill";

const schema = z.object({
  complaints: z.string().min(2, "Опишіть скарги пацієнта."),
  diagnosis: z.string().min(2, "Вкажіть діагноз."),
  treatment_plan: z.string().min(2, "Заповніть план лікування."),
});

type FormValues = z.infer<typeof schema>;

type DoctorDashboardProps = {
  viewer: Viewer;
};

export function DoctorDashboard({ viewer }: DoctorDashboardProps) {
  const queryClient = useQueryClient();
  const appointmentsQuery = useQuery({
    queryKey: ["appointments", "mine"],
    queryFn: () => api.appointments.listMine(),
  });

  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);

  useEffect(() => {
    if (!selectedAppointment && appointmentsQuery.data?.items.length) {
      setSelectedAppointment(appointmentsQuery.data.items[0]);
    }
  }, [appointmentsQuery.data, selectedAppointment]);

  const patientRecordsQuery = useQuery({
    queryKey: ["medical-records", selectedAppointment?.patient.id],
    queryFn: () => api.medicalRecords.listByPatient(selectedAppointment?.patient.id ?? ""),
    enabled: Boolean(selectedAppointment?.patient.id),
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      complaints: "",
      diagnosis: "",
      treatment_plan: "",
    },
  });

  useEffect(() => {
    const existingRecord = patientRecordsQuery.data?.find((item) => item.appointment_id === selectedAppointment?.id);
    form.reset({
      complaints: existingRecord?.complaints ?? "",
      diagnosis: existingRecord?.diagnosis ?? "",
      treatment_plan: existingRecord?.treatment_plan ?? "",
    });
  }, [form, patientRecordsQuery.data, selectedAppointment]);

  const recordMutation = useMutation({
    mutationFn: api.medicalRecords.upsert,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["medical-records", selectedAppointment?.patient.id] }),
        queryClient.invalidateQueries({ queryKey: ["appointments", "mine"] }),
      ]);
    },
  });

  const statusMutation = useMutation({
    mutationFn: ({ appointmentId, status }: { appointmentId: string; status: "COMPLETED" | "NO_SHOW" | "CANCELLED" }) =>
      api.appointments.updateStatus(appointmentId, status),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["appointments", "mine"] });
    },
  });

  const handleSubmit = form.handleSubmit((values) => {
    if (!selectedAppointment) {
      return;
    }
    recordMutation.mutate({
      appointment_id: selectedAppointment.id,
      complaints: values.complaints,
      diagnosis: values.diagnosis,
      treatment_plan: values.treatment_plan,
    });
  });

  const appointments = appointmentsQuery.data?.items ?? [];
  const completedAppointments = appointments.filter((appointment) => appointment.status === "COMPLETED").length;
  const activeAppointments = appointments.filter((appointment) => appointment.status === "SCHEDULED").length;
  const patientRecords = patientRecordsQuery.data?.length ?? 0;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard
          description={`${viewer.specialty ?? "Лікар"} • кабінет ${viewer.cabinet_number ?? "—"}`}
          icon={<StethoscopeIcon className="h-5 w-5" />}
          label="Клінічний профіль"
          tone="teal"
          value={`${viewer.first_name} ${viewer.last_name}`}
        />
        <MetricCard
          description="Прийоми, які ще очікують консультації або фінального статусу."
          icon={<CalendarIcon className="h-5 w-5" />}
          label="Активні прийоми"
          tone="indigo"
          value={activeAppointments}
        />
        <MetricCard
          description="Картки вибраного пацієнта, які вже доступні для швидкого перегляду."
          icon={<ClipboardIcon className="h-5 w-5" />}
          label="Доступні записи"
          tone="coral"
          value={patientRecords || completedAppointments}
        />
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <Card className="space-y-5">
          <div>
            <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
              <span className="icon-chip">
                <CalendarIcon className="h-5 w-5" />
              </span>
              Мій розклад
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Обирайте прийом зі списку і переходьте до швидкого внесення клінічних нотаток.
            </p>
          </div>

          {appointments.length ? (
            <div className="space-y-3">
              {appointments.map((appointment) => (
                <button
                  className={`w-full rounded-[24px] border p-4 text-left transition ${
                    selectedAppointment?.id === appointment.id
                      ? "border-cyan-500 bg-gradient-to-br from-cyan-50 via-white to-emerald-50 shadow-[0_18px_40px_rgba(14,116,144,0.12)]"
                      : "border-slate-200/70 bg-white/85 hover:border-cyan-300 hover:-translate-y-0.5"
                  }`}
                  key={appointment.id}
                  onClick={() => setSelectedAppointment(appointment)}
                  type="button"
                >
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-semibold text-slate-900">
                      {appointment.patient.first_name} {appointment.patient.last_name}
                    </h3>
                    <StatusPill
                      tone={
                        appointment.status === "COMPLETED"
                          ? "success"
                          : appointment.status === "CANCELLED"
                            ? "danger"
                            : appointment.status === "NO_SHOW"
                              ? "warning"
                              : "info"
                      }
                    >
                      {appointmentStatusLabel(appointment.status)}
                    </StatusPill>
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{formatDateTime(appointment.start_time)}</p>
                </button>
              ))}
            </div>
          ) : (
            <EmptyState
              title="Прийомів поки немає"
              description="Коли пацієнти бронюватимуть консультації, вони автоматично з’являться в цьому списку."
            />
          )}
        </Card>

        <Card className="space-y-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
                <span className="icon-chip">
                  <HeartPulseIcon className="h-5 w-5" />
                </span>
                Електронна медична картка
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                Фіксуйте скарги, діагноз і план лікування в одному структурованому сценарії.
              </p>
            </div>
            {selectedAppointment ? (
              <div className="rounded-2xl border border-slate-200/70 bg-white/85 px-4 py-3 text-right text-sm text-slate-600">
                <p className="font-semibold text-slate-900">
                  {selectedAppointment.patient.first_name} {selectedAppointment.patient.last_name}
                </p>
                <p>{formatDateTime(selectedAppointment.start_time)}</p>
              </div>
            ) : null}
          </div>

          {selectedAppointment ? (
            <>
              <div className="flex flex-wrap gap-3">
                <button
                  className="btn-secondary"
                  onClick={() => statusMutation.mutate({ appointmentId: selectedAppointment.id, status: "COMPLETED" })}
                  type="button"
                >
                  Позначити як завершений
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => statusMutation.mutate({ appointmentId: selectedAppointment.id, status: "NO_SHOW" })}
                  type="button"
                >
                  Пацієнт не з’явився
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => statusMutation.mutate({ appointmentId: selectedAppointment.id, status: "CANCELLED" })}
                  type="button"
                >
                  Скасувати
                </button>
              </div>

              <form className="space-y-4" onSubmit={handleSubmit}>
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">Скарги</label>
                  <textarea className="field min-h-28" {...form.register("complaints")} />
                  <p className="mt-2 text-sm text-rose-600">{form.formState.errors.complaints?.message}</p>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">Діагноз</label>
                  <textarea className="field min-h-24" {...form.register("diagnosis")} />
                  <p className="mt-2 text-sm text-rose-600">{form.formState.errors.diagnosis?.message}</p>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">План лікування</label>
                  <textarea className="field min-h-28" {...form.register("treatment_plan")} />
                  <p className="mt-2 text-sm text-rose-600">{form.formState.errors.treatment_plan?.message}</p>
                </div>

                {recordMutation.error ? <p className="text-sm text-rose-600">{recordMutation.error.message}</p> : null}
                {statusMutation.error ? <p className="text-sm text-rose-600">{statusMutation.error.message}</p> : null}

                <button className="btn-primary w-full sm:w-auto" disabled={recordMutation.isPending} type="submit">
                  {recordMutation.isPending ? "Зберігаємо..." : "Зберегти запис"}
                </button>
              </form>
            </>
          ) : (
            <EmptyState
              title="Оберіть прийом"
              description="Щоб заповнити картку, спочатку виберіть запис пацієнта в лівій колонці."
            />
          )}
        </Card>
      </div>
    </div>
  );
}
