import type { InputHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export function Input({ label, id, ...props }: InputProps): JSX.Element {
  const inputId = id ?? props.name ?? label.toLowerCase().replaceAll(" ", "-");

  return (
    <label className="block text-sm font-medium text-slate-700" htmlFor={inputId}>
      {label}
      <input
        id={inputId}
        className="mt-2 h-10 w-full rounded border border-slate-300 bg-white px-3 text-sm text-ink outline-none focus:border-signal"
        {...props}
      />
    </label>
  );
}
