import { Calculator } from "@/components/Calculator";

type ProjectDetailPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function ProjectDetailPage({ params }: ProjectDetailPageProps): Promise<JSX.Element> {
  const { id } = await params;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-600">Proyecto {id}</p>
        <h1 className="text-2xl font-semibold text-ink">Calculadora acustica</h1>
      </div>
      <Calculator projectId={id} />
    </div>
  );
}
