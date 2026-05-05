import type { HTMLAttributes, ReactNode } from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
};

export function Card({ children, className = "", ...props }: CardProps): JSX.Element {
  return (
    <div className={`rounded border border-slate-200 bg-white p-5 shadow-sm ${className}`} {...props}>
      {children}
    </div>
  );
}
