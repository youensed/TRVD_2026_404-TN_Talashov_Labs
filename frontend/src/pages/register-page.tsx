import { Link } from "react-router-dom";

import { BrandLockup } from "../components/branding/brand-lockup";
import { Card } from "../components/ui/card";
import { CalendarIcon, ClipboardIcon, HeartPulseIcon } from "../components/ui/icons";
import { RegisterForm } from "../features/auth/register-form";

const highlights = [
  {
    description: "Створення профілю пацієнта.",
    icon: ClipboardIcon,
    title: "Реєстрація",
  },
  {
    description: "Швидкий перехід до запису на прийом.",
    icon: CalendarIcon,
    title: "Запис",
  },
  {
    description: "Доступ до історії візитів.",
    icon: HeartPulseIcon,
    title: "Особистий кабінет",
  },
];

export function RegisterPage() {
  return (
    <div className="page-shell grid gap-6 lg:grid-cols-[0.92fr_1.08fr] lg:items-start">
      <Card strong className="relative overflow-hidden space-y-6">
        <div className="absolute inset-x-0 top-0 h-36 bg-[radial-gradient(circle_at_top_left,rgba(94,110,230,0.14),transparent_45%),radial-gradient(circle_at_top_right,rgba(15,139,141,0.14),transparent_42%)]" />

        <div className="relative space-y-6">
          <p className="tag">Новий пацієнт</p>
          <BrandLockup subtitle="Створення профілю в Verita Clinic." />
          <h1 className="text-3xl font-semibold leading-tight text-slate-900">Реєстрація пацієнта</h1>

          <div className="space-y-3">
            {highlights.map((item) => {
              const Icon = item.icon;
              return (
                <div className="feature-tile flex items-start gap-4" key={item.title}>
                  <div className="icon-chip">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-slate-900">{item.title}</h2>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{item.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Card>

      <Card className="space-y-6 border-white/70 bg-white/94">
        <div className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-secondary)]">Verita Clinic</p>
          <div>
            <h2 className="text-3xl font-semibold text-slate-900">Реєстрація</h2>
            <p className="mt-2 text-sm text-slate-600">Заповніть дані для створення профілю.</p>
          </div>
        </div>

        <RegisterForm />

        <p className="text-sm text-slate-600">
          Уже маєте обліковий запис?{" "}
          <Link className="font-semibold text-cyan-700" to="/login">
            Увійти
          </Link>
        </p>
      </Card>
    </div>
  );
}
