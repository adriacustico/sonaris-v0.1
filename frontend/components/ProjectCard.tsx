import Link from "next/link";
import { Card } from "@/components/ui/Card";

type ProjectCardProps = {
  id: string;
  name: string;
  description: string;
};

export function ProjectCard({ id, name, description }: ProjectCardProps): JSX.Element {
  return (
    <Card>
      <h2 className="text-lg font-semibold text-ink">{name}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
      <Link href={`/projects/${id}`} className="mt-4 inline-flex text-sm font-medium text-signal">
        Abrir proyecto
      </Link>
    </Card>
  );
}
