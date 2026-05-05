import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: false;
  children: ReactNode;
  variant?: "primary" | "secondary";
};

type ButtonAsChildProps = {
  asChild: true;
  children: React.ReactElement<typeof Link>;
  variant?: "primary" | "secondary";
};

const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary: "bg-signal text-white hover:bg-teal-800",
  secondary: "border border-slate-300 bg-white text-ink hover:bg-slate-50"
};

export function Button(props: ButtonProps | ButtonAsChildProps): JSX.Element {
  const variant = props.variant ?? "primary";
  const className = `inline-flex min-h-10 items-center justify-center gap-2 rounded px-4 text-sm font-medium transition ${variants[variant]}`;

  if (props.asChild) {
    return <span className={className}>{props.children}</span>;
  }

  const { children, asChild: _asChild, ...buttonProps } = props;
  return (
    <button className={className} {...buttonProps}>
      {children}
    </button>
  );
}
