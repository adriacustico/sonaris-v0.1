import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

type EditProjectPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function EditProjectPage({ params }: EditProjectPageProps): Promise<JSX.Element> {
  const { id } = await params;

  return (
    <form className="max-w-xl space-y-4">
      <h1 className="text-2xl font-semibold text-ink">Editar proyecto {id}</h1>
      <Input label="Nombre" name="name" placeholder="Nombre del proyecto" />
      <Input label="Descripcion" name="description" placeholder="Descripcion breve" />
      <Button type="submit">Actualizar</Button>
    </form>
  );
}
