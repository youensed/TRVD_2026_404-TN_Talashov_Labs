import type { PropsWithChildren } from "react";

type CardProps = PropsWithChildren<{
  className?: string;
  strong?: boolean;
}>;

export function Card({ children, className = "", strong = false }: CardProps) {
  return <section className={`${strong ? "panel-strong" : "panel"} ${className}`.trim()}>{children}</section>;
}

