import Link from "next/link";
import { Navigation } from "@/components/Navigation";

export function Header(): JSX.Element {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="text-lg font-semibold text-ink">
          Sonaris
        </Link>
        <Navigation />
      </div>
    </header>
  );
}
