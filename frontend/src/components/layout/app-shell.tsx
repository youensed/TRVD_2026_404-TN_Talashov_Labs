import type { PropsWithChildren } from "react";

import { roleLabel } from "../../app/lib/format";
import type { Viewer } from "../../app/types";
import { BrandLockup } from "../branding/brand-lockup";
import { ClipboardIcon, HeartPulseIcon, LogOutIcon, StethoscopeIcon, TrendingUpIcon } from "../ui/icons";

type AppShellProps = PropsWithChildren<{
  viewer: Viewer;
  onLogout: () => void;
}>;

const roleDescriptions: Record<Viewer["role"], string> = {
  PATIENT: "Запис на прийом і перегляд історії візитів.",
  DOCTOR: "Розклад прийомів і медичні записи.",
  ADMIN: "Керування пацієнтами, змінами та оплатами.",
  OWNER: "Фінансові звіти та навантаження лікарів.",
};

const roleSignals: Record<Viewer["role"], { icon: typeof HeartPulseIcon; label: string }> = {
  PATIENT: { icon: HeartPulseIcon, label: "Пацієнтський простір" },
  DOCTOR: { icon: StethoscopeIcon, label: "Клінічний режим" },
  ADMIN: { icon: ClipboardIcon, label: "Операційний контроль" },
  OWNER: { icon: TrendingUpIcon, label: "Аналітика клініки" },
};

export function AppShell({ viewer, onLogout, children }: AppShellProps) {
  return (
    <div className="page-shell">
      <header className="panel-strong relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-40 bg-[radial-gradient(circle_at_top_left,rgba(15,139,141,0.18),transparent_46%),radial-gradient(circle_at_top_right,rgba(94,110,230,0.18),transparent_38%)]" />
        <div className="absolute -right-12 bottom-0 h-48 w-48 rounded-full bg-[radial-gradient(circle,rgba(229,123,99,0.14),transparent_68%)]" />

        <div className="relative flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div className="space-y-5">
            <BrandLockup compact subtitle="Робочий простір клініки." />

            <div className="flex flex-wrap items-center gap-3">
              <div className="tag">{roleLabel(viewer.role)}</div>
              <div className="tag">{roleSignals[viewer.role].label}</div>
            </div>

            <div>
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Робочий простір</p>
              <h1 className="mt-2 text-3xl font-semibold text-slate-900">
                {viewer.first_name} {viewer.last_name}
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">{roleDescriptions[viewer.role]}</p>
            </div>
          </div>

          <div className="flex xl:justify-end">
            <button className="btn-primary" onClick={onLogout} type="button">
              <LogOutIcon className="h-5 w-5" />
              Вийти
            </button>
          </div>
        </div>
      </header>

      <main className="mt-6">{children}</main>
    </div>
  );
}
