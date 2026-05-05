import Link from "next/link";
import { Plus } from "lucide-react";
import { ProjectCard } from "@/components/ProjectCard";
import { Button } from "@/components/ui/Button";

export default function ProjectsPage(): JSX.Element {
  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold text-ink">Proyectos</h1>
        <Button asChild>
          <Link href="/projects/new">
            <Plus className="h-4 w-4" />
            Nuevo
          </Link>
        </Button>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <ProjectCard id="demo" name="Edificio demo" description="Placeholder para listado de proyectos." />
      </div>
    </div>
  );
}
