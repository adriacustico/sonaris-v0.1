import Link from "next/link";
import { Activity, FolderKanban } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function HomePage(): JSX.Element {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-64px)] max-w-6xl flex-col justify-center px-6 py-16">
      <div className="max-w-3xl">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-signal">Sonaris</p>
        <h1 className="text-4xl font-semibold leading-tight text-ink md:text-6xl">
          Calculos acusticos para equipos tecnicos.
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-700">
          Base SaaS para gestionar proyectos, ejecutar calculos y preparar reportes acusticos desde una interfaz web.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/projects">
              <FolderKanban className="h-4 w-4" />
              Proyectos
            </Link>
          </Button>
          <Button asChild variant="secondary">
            <Link href="/calculations">
              <Activity className="h-4 w-4" />
              Calculos
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
