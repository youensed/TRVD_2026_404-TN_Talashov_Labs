type BrandLockupProps = {
  className?: string;
  compact?: boolean;
  subtitle?: string | null;
};

export function BrandLockup({
  className = "",
  compact = false,
  subtitle = "Система керування записом, прийомами та даними клініки.",
}: BrandLockupProps) {
  const logoSize = compact ? "h-14 w-14" : "h-20 w-20";

  return (
    <div className={`flex items-center gap-4 ${className}`.trim()}>
      <div className={`brand-logo-shell ${logoSize}`}>
        <img alt="Логотип Verita Clinic" className="h-full w-full object-contain p-2" src="/verita-logo-clear.png" />
      </div>

      <div className="min-w-0 space-y-1">
        <p className="text-[0.72rem] font-semibold uppercase tracking-[0.34em] text-[var(--accent-secondary)]">Verita Clinic</p>
        {subtitle ? <p className={`${compact ? "text-xs" : "text-sm"} max-w-xl leading-6 text-slate-600`}>{subtitle}</p> : null}
      </div>
    </div>
  );
}
