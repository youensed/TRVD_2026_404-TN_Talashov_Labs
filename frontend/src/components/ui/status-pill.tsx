type StatusPillProps = {
  tone: "info" | "success" | "danger" | "warning";
  children: string;
};

const toneClasses: Record<StatusPillProps["tone"], string> = {
  info: "bg-cyan-50 text-cyan-700",
  success: "bg-emerald-50 text-emerald-700",
  danger: "bg-rose-50 text-rose-700",
  warning: "bg-amber-50 text-amber-700",
};

export function StatusPill({ tone, children }: StatusPillProps) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${toneClasses[tone]}`}>{children}</span>;
}

