import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

function IconBase({ className = "h-5 w-5", children, viewBox = "0 0 24 24", ...props }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
      viewBox={viewBox}
      {...props}
    >
      {children}
    </svg>
  );
}

export function ArrowRightIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </IconBase>
  );
}

export function CalendarIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M8 2v4" />
      <path d="M16 2v4" />
      <rect height="18" rx="3" width="18" x="3" y="4" />
      <path d="M3 10h18" />
    </IconBase>
  );
}

export function ClipboardIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect height="18" rx="3" width="14" x="5" y="4" />
      <path d="M9 4.5h6a1.5 1.5 0 0 0-1.5-1.5h-3A1.5 1.5 0 0 0 9 4.5Z" />
      <path d="M9 12h6" />
      <path d="M9 16h4" />
    </IconBase>
  );
}

export function HeartPulseIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M19.5 13.5 12 21l-7.5-7.5a4.9 4.9 0 0 1 0-7 4.9 4.9 0 0 1 7 0L12 7l.5-.5a4.9 4.9 0 0 1 7 7Z" />
      <path d="m7.5 12 2 0 1.5-2.5 2 5 1.5-2.5h2.5" />
    </IconBase>
  );
}

export function LogOutIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M15 3h3a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3h-3" />
      <path d="M10 17 15 12 10 7" />
      <path d="M15 12H3" />
    </IconBase>
  );
}

export function ShieldCheckIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M12 3 5 6v5c0 5 3.5 8.5 7 10 3.5-1.5 7-5 7-10V6l-7-3Z" />
      <path d="m9.5 12 1.8 1.8 3.7-4.1" />
    </IconBase>
  );
}

export function SparklesIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="m12 3 1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3Z" />
      <path d="m5 18 .8 2.2L8 21l-2.2.8L5 24l-.8-2.2L2 21l2.2-.8L5 18Z" />
      <path d="m19 15 1 2.5L22.5 18 20 19l-1 2.5-1-2.5L15.5 18l2.5-.5L19 15Z" />
    </IconBase>
  );
}

export function StethoscopeIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M8 3v5a4 4 0 0 0 8 0V3" />
      <path d="M8 3H6" />
      <path d="M18 3h-2" />
      <path d="M12 12v3a4 4 0 0 0 8 0v-1.5" />
      <circle cx="20" cy="13" r="2" />
    </IconBase>
  );
}

export function TrendingUpIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M3 17 9 11l4 4 8-8" />
      <path d="M15 7h6v6" />
    </IconBase>
  );
}

export function UsersIcon(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.9" />
      <path d="M16 3.1a4 4 0 0 1 0 7.8" />
    </IconBase>
  );
}
