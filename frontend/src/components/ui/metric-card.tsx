import type { ReactNode } from "react";

import { Card } from "./card";

type MetricTone = "teal" | "coral" | "indigo" | "amber";

type MetricCardProps = {
  label: string;
  value: ReactNode;
  description?: string;
  icon: ReactNode;
  tone?: MetricTone;
};

const toneClasses: Record<MetricTone, string> = {
  teal: "from-cyan-500/18 via-teal-500/10 to-emerald-500/18 text-cyan-800",
  coral: "from-orange-400/18 via-rose-400/10 to-pink-500/16 text-rose-700",
  indigo: "from-indigo-500/18 via-sky-500/10 to-cyan-500/16 text-indigo-700",
  amber: "from-amber-300/20 via-orange-300/10 to-yellow-300/20 text-amber-700",
};

export function MetricCard({ label, value, description, icon, tone = "teal" }: MetricCardProps) {
  return (
    <Card className={`metric-card bg-gradient-to-br ${toneClasses[tone]}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{value}</p>
          {description ? <p className="mt-2 text-sm text-slate-600">{description}</p> : null}
        </div>
        <div className="icon-chip shrink-0">{icon}</div>
      </div>
    </Card>
  );
}
