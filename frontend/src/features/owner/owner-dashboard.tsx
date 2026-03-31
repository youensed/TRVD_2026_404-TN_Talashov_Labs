import { useMemo, useState } from "react";

import { useQuery } from "@tanstack/react-query";

import { api } from "../../app/lib/api";
import { formatCurrency } from "../../app/lib/format";
import type { Viewer } from "../../app/types";
import { Card } from "../../components/ui/card";
import { CalendarIcon, ClipboardIcon, StethoscopeIcon, TrendingUpIcon } from "../../components/ui/icons";
import { MetricCard } from "../../components/ui/metric-card";

type OwnerDashboardProps = {
  viewer: Viewer;
};

function toDateInput(value: Date): string {
  const timezoneOffsetMs = value.getTimezoneOffset() * 60 * 1000;
  return new Date(value.getTime() - timezoneOffsetMs).toISOString().slice(0, 16);
}

export function OwnerDashboard({ viewer }: OwnerDashboardProps) {
  const now = useMemo(() => new Date(), []);
  const [dateFrom, setDateFrom] = useState(toDateInput(new Date(now.getTime() - 1000 * 60 * 60 * 24 * 30)));
  const [dateTo, setDateTo] = useState(toDateInput(now));

  const revenueQuery = useQuery({
    queryKey: ["report", "revenue", dateFrom, dateTo],
    queryFn: () => api.reports.revenue(dateFrom, dateTo),
  });

  const doctorLoadQuery = useQuery({
    queryKey: ["report", "doctor-load", dateFrom, dateTo],
    queryFn: () => api.reports.doctorLoad(dateFrom, dateTo),
  });

  const topDoctor = doctorLoadQuery.data?.doctors[0];

  return (
    <div className="space-y-6">
      <Card strong className="relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-32 bg-[radial-gradient(circle_at_top_left,rgba(94,110,230,0.16),transparent_55%),radial-gradient(circle_at_top_right,rgba(229,123,99,0.14),transparent_45%)]" />

        <div className="relative flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Аналітика Verita Clinic</p>
            <h2 className="mt-3 text-3xl font-semibold text-slate-900">
              {viewer.first_name} {viewer.last_name}
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              Тут зібрані фінансові підсумки та навантаження лікарів без розкриття персональних медичних даних.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-semibold text-slate-700">Початок періоду</span>
              <input className="field" type="datetime-local" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
            </label>
            <label className="space-y-2">
              <span className="text-sm font-semibold text-slate-700">Кінець періоду</span>
              <input className="field" type="datetime-local" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
            </label>
          </div>
        </div>
      </Card>

      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard
          description="Підсумок оплачених транзакцій у вибраному вікні часу."
          icon={<TrendingUpIcon className="h-5 w-5" />}
          label="Дохід за період"
          tone="teal"
          value={revenueQuery.data ? formatCurrency(revenueQuery.data.total_amount) : "—"}
        />
        <MetricCard
          description="Кількість платежів, що були успішно проведені та враховані у звіті."
          icon={<ClipboardIcon className="h-5 w-5" />}
          label="Оплачені транзакції"
          tone="amber"
          value={revenueQuery.data?.paid_transactions ?? 0}
        />
        <MetricCard
          description={topDoctor?.specialty ?? "Оберіть період із даними, щоб визначити лідера навантаження."}
          icon={<StethoscopeIcon className="h-5 w-5" />}
          label="Лідер навантаження"
          tone="indigo"
          value={topDoctor?.doctor_name ?? "Немає даних"}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="space-y-4">
          <div>
            <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
              <span className="icon-chip">
                <CalendarIcon className="h-5 w-5" />
              </span>
              Фінансовий звіт
            </h2>
            <p className="mt-2 text-sm text-slate-600">Короткий огляд грошового потоку за вибраний період у Verita Clinic.</p>
          </div>

          <div className="space-y-3">
            <div className="rounded-[22px] border border-slate-200/70 bg-gradient-to-br from-cyan-50 via-white to-emerald-50 px-4 py-4">
              <p className="text-sm text-slate-500">Дохід</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">
                {revenueQuery.data ? formatCurrency(revenueQuery.data.total_amount) : "—"}
              </p>
            </div>
            <div className="rounded-[22px] border border-slate-200/70 bg-gradient-to-br from-amber-50 via-white to-orange-50 px-4 py-4">
              <p className="text-sm text-slate-500">Очікуючі транзакції</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{revenueQuery.data?.pending_transactions ?? 0}</p>
            </div>
          </div>
        </Card>

        <Card className="space-y-4">
          <div>
            <h2 className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
              <span className="icon-chip">
                <StethoscopeIcon className="h-5 w-5" />
              </span>
              Завантаженість лікарів
            </h2>
            <p className="mt-2 text-sm text-slate-600">Баланс між завершеними прийомами та майбутнім графіком команди.</p>
          </div>

          <div className="space-y-4">
            {doctorLoadQuery.data?.doctors.map((doctor) => {
              const total = doctor.completed_appointments + doctor.scheduled_appointments || 1;
              const completedWidth = `${(doctor.completed_appointments / total) * 100}%`;
              return (
                <div className="rounded-[22px] border border-slate-200/70 bg-white/85 px-4 py-4" key={doctor.doctor_id}>
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="font-semibold text-slate-900">{doctor.doctor_name}</p>
                      <p className="text-sm text-slate-600">{doctor.specialty}</p>
                    </div>
                    <div className="text-right text-sm text-slate-600">
                      <p>Завершено: {doctor.completed_appointments}</p>
                      <p>Заплановано: {doctor.scheduled_appointments}</p>
                    </div>
                  </div>
                  <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-emerald-500" style={{ width: completedWidth }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </section>
    </div>
  );
}
