import { ProjectCard } from "@/components/ProjectCard";

export default function DashboardPage(): JSX.Element {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink">Dashboard</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <ProjectCard id="demo" name="Proyecto demo" description="Vista inicial para validar el flujo de trabajo." />
      </div>
    </div>
  );
}
