import { useDeferredValue, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../../app/lib/api";
import { appointmentStatusLabel, formatDateTime } from "../../app/lib/format";
import type { Viewer } from "../../app/types";
import { Card } from "../../components/ui/card";
import { EmptyState } from "../../components/ui/empty-state";
import { CalendarIcon, ClipboardIcon, HeartPulseIcon } from "../../components/ui/icons";
import { MetricCard } from "../../components/ui/metric-card";
import { StatusPill } from "../../components/ui/status-pill";

type PatientDashboardProps = {
  viewer: Viewer;
};

export function PatientDashboard({ viewer }: PatientDashboardProps) {
  const queryClient = useQueryClient();
  const [specialty, setSpecialty] = useState("");
  const deferredSpecialty = useDeferredValue(specialty);

  const scheduleQuery = useQuery({
    queryKey: ["schedule", deferredSpecialty],
    queryFn: () => api.schedules.list({ specialty: deferredSpecialty || undefined }),
  });
  const appointmentsQuery = useQuery({
    queryKey: ["appointments", "mine"],
    queryFn: () => api.appointments.listMine(),
  });
  const recordsQuery = useQuery({
    queryKey: ["medical-records", "mine"],
    queryFn: () => api.medicalRecords.listMine(),
  });

  const bookMutation = useMutation({
    mutationFn: api.appointments.book,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["schedule"] }),
        queryClient.invalidateQueries({ queryKey: ["appointments", "mine"] }),
      ]);
    },
  });

  const cancelMutation = useMutation({
    mutationFn: api.appointments.cancel,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["appointments", "mine"] });
    },
  });

  const appointments = appointmentsQuery.data?.items ?? [];
  const scheduledAppointments = appointments.filter((item) => item.status === "SCHEDULED").length;
  const completedAppointments = appointments.filter((item) => item.status === "COMPLETED").length;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard
          description={viewer.email ?? "Профіль пацієнта"}
          icon={<HeartPulseIcon className="h-5 w-5" />}
          label="Поточний користувач"
          tone="teal"
          value={`${viewer.first_name} ${viewer.last_name}`}
        />
        <MetricCard
          description="Активні записи, які ще можна переглянути або скасувати."
          icon={<CalendarIcon className="h-5 w-5" />}
          label="Заплановані візити"
          tone="indigo"
          value={scheduledAppointments}
        />
        <MetricCard
          description="Завершені консультації вже формують вашу історію."
          icon={<ClipboardIcon className="h-5 w-5" />}
          label="Завершені консультації"
          tone="coral"
          value={completedAppointments}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <Card className="space-y-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
                <span className="icon-chip">
                  <CalendarIcon className="h-5 w-5" />
                </span>
                Розклад лікарів
              </h2>
              <p className="mt-2 text-sm text-slate-600">Фільтруйте за спеціальністю та бронюйте вільні слоти.</p>
            </div>
            <input
              className="field w-full max-w-xs"
              placeholder="Наприклад, сімейна медицина"
              value={specialty}
              onChange={(event) => setSpecialty(event.target.value)}
            />
          </div>

          {scheduleQuery.data?.length ? (
            <div className="space-y-4">
              {scheduleQuery.data.map((row) => (
                <div className="rounded-[24px] border border-slate-200/70 bg-white/80 p-4" key={row.doctor.user_id}>
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        {row.doctor.first_name} {row.doctor.last_name}
                      </h3>
                      <p className="text-sm text-slate-600">
                        {row.doctor.specialty} · Кабінет {row.doctor.cabinet_number}
                      </p>
                    </div>
                    <span className="tag">{row.slots.length} доступних слотів</span>
                  </div>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {row.slots.slice(0, 6).map((slot) => (
                      <button
                        className="rounded-2xl border border-cyan-200 bg-cyan-50/80 px-4 py-3 text-left transition hover:-translate-y-0.5 hover:border-cyan-400"
                        key={slot.start_time}
                        onClick={() =>
                          bookMutation.mutate({
                            doctor_id: row.doctor.user_id,
                            start_time: slot.start_time,
                          })
                        }
                        type="button"
                      >
                        <span className="block text-sm font-semibold text-slate-900">{formatDateTime(slot.start_time)}</span>
                        <span className="mt-1 block text-xs text-cyan-700">Записатися на прийом</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="Вільних слотів поки немає"
              description="Спробуйте змінити фільтр або перевірте трохи пізніше, коли адміністратор додасть нові зміни."
            />
          )}

          {bookMutation.error ? <p className="text-sm text-rose-600">{bookMutation.error.message}</p> : null}
        </Card>

        <Card className="space-y-4">
          <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
            <span className="icon-chip">
              <ClipboardIcon className="h-5 w-5" />
            </span>
            Мої візити
          </h2>
          {appointments.length ? (
            <div className="space-y-3">
              {appointments.map((appointment) => (
                <div className="rounded-[24px] border border-slate-200/70 bg-white/85 p-4" key={appointment.id}>
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <h3 className="font-semibold text-slate-900">
                      {appointment.doctor.first_name} {appointment.doctor.last_name}
                    </h3>
                    <StatusPill
                      tone={
                        appointment.status === "COMPLETED"
                          ? "success"
                          : appointment.status === "CANCELLED"
                            ? "danger"
                            : "info"
                      }
                    >
                      {appointmentStatusLabel(appointment.status)}
                    </StatusPill>
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{formatDateTime(appointment.start_time)}</p>
                  {appointment.status === "SCHEDULED" ? (
                    <button
                      className="btn-secondary mt-4 w-full"
                      onClick={() => cancelMutation.mutate(appointment.id)}
                      type="button"
                    >
                      Скасувати візит
                    </button>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="У вас ще немає візитів"
              description="Оберіть лікаря ліворуч та забронюйте перший зручний слот."
            />
          )}
          {cancelMutation.error ? <p className="text-sm text-rose-600">{cancelMutation.error.message}</p> : null}
        </Card>
      </section>

      <Card className="space-y-5">
        <div>
          <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
            <span className="icon-chip">
              <HeartPulseIcon className="h-5 w-5" />
            </span>
            Медична історія
          </h2>
          <p className="mt-2 text-sm text-slate-600">Після завершених прийомів тут з’являються ваші базові медичні записи.</p>
        </div>

        {recordsQuery.data?.length ? (
          <div className="grid gap-4 md:grid-cols-2">
            {recordsQuery.data.map((record) => (
              <div className="rounded-[24px] border border-slate-200/70 bg-white/85 p-4" key={record.id}>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{formatDateTime(record.created_at)}</p>
                <h3 className="mt-3 text-lg font-semibold text-slate-900">Діагноз: {record.diagnosis}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                  <strong>Скарги:</strong> {record.complaints}
                </p>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                  <strong>План лікування:</strong> {record.treatment_plan}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="Медичні записи ще не додані"
            description="Після прийому лікар зафіксує скарги, діагноз і план лікування в цій секції."
          />
        )}
      </Card>
    </div>
  );
}
