import { Link } from "react-router-dom";

import { BrandLockup } from "../components/branding/brand-lockup";
import { Card } from "../components/ui/card";
import { CalendarIcon, ShieldCheckIcon, SparklesIcon } from "../components/ui/icons";
import { LoginForm } from "../features/auth/login-form";

const highlights = [
  {
    description: "Вхід до системи за ролями.",
    icon: ShieldCheckIcon,
    title: "Авторизація",
  },
  {
    description: "Доступ до розкладу та прийомів.",
    icon: CalendarIcon,
    title: "Робочий простір",
  },
  {
    description: "Швидка щоденна робота.",
    icon: SparklesIcon,
    title: "Зручний інтерфейс",
  },
];

export function LoginPage() {
  return (
    <div className="page-shell grid gap-6 lg:grid-cols-[0.92fr_1.08fr] lg:items-start">
      <Card strong className="relative overflow-hidden space-y-6">
        <div className="absolute inset-x-0 top-0 h-36 bg-[radial-gradient(circle_at_top_left,rgba(15,139,141,0.16),transparent_45%),radial-gradient(circle_at_top_right,rgba(229,123,99,0.12),transparent_40%)]" />

        <div className="relative space-y-6">
          <p className="tag">Авторизація</p>
          <BrandLockup subtitle="Вхід до системи Verita Clinic." />
          <h1 className="text-3xl font-semibold leading-tight text-slate-900">Увійти в систему</h1>

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
            <h2 className="text-3xl font-semibold text-slate-900">Вхід</h2>
            <p className="mt-2 text-sm text-slate-600">Введіть email і пароль.</p>
          </div>
        </div>

        <LoginForm />

        <p className="text-sm text-slate-600">
          Ще немає профілю?{" "}
          <Link className="font-semibold text-cyan-700" to="/register">
            Зареєструватися
          </Link>
        </p>
      </Card>
    </div>
  );
}
