import { Link } from "react-router-dom";

import { BrandLockup } from "../components/branding/brand-lockup";
import { ArrowRightIcon, CalendarIcon, ClipboardIcon, ShieldCheckIcon } from "../components/ui/icons";

const features = [
  {
    description: "Авторизація та доступ за ролями.",
    icon: ShieldCheckIcon,
    title: "Безпечний вхід",
  },
  {
    description: "Розклад, записи та прийоми.",
    icon: CalendarIcon,
    title: "Робота з візитами",
  },
  {
    description: "Медичні записи, оплати та звіти.",
    icon: ClipboardIcon,
    title: "Керування клінікою",
  },
];

export function HomePage() {
  return (
    <div className="page-shell space-y-6">
      <section className="panel-strong relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-40 bg-[radial-gradient(circle_at_top_left,rgba(15,139,141,0.16),transparent_45%),radial-gradient(circle_at_top_right,rgba(94,110,230,0.18),transparent_40%)]" />
        <div className="absolute -right-16 top-20 h-56 w-56 rounded-full bg-[radial-gradient(circle,rgba(229,123,99,0.16),transparent_68%)]" />

        <div className="relative space-y-8">
          <BrandLockup subtitle="Єдина система для пацієнтів, лікарів, адміністраторів і керівника." />

          <div className="max-w-4xl space-y-4">
            <p className="tag">Медична інформаційна система</p>
            <h1 className="text-4xl font-semibold leading-tight text-slate-900 sm:text-5xl">
              Запис, прийоми та керування клінікою в одній системі.
            </h1>
            <p className="max-w-3xl text-base leading-7 text-slate-600">
              Verita Clinic об’єднує роботу з пацієнтами, розкладом, медичними записами, оплатами та звітами.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Link className="btn-primary" to="/login">
              <ArrowRightIcon className="h-5 w-5" />
              Увійти
            </Link>
            <Link className="btn-secondary" to="/register">
              <ClipboardIcon className="h-5 w-5" />
              Реєстрація пацієнта
            </Link>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div className="feature-tile" key={feature.title}>
                  <div className="icon-chip">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h2 className="mt-4 text-lg font-semibold text-slate-900">{feature.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
