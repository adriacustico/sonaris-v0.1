import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export default function NewProjectPage(): JSX.Element {
  return (
    <form className="max-w-xl space-y-4">
      <h1 className="text-2xl font-semibold text-ink">Crear proyecto</h1>
      <Input label="Nombre" name="name" placeholder="Edificio corporativo" />
      <Input label="Descripcion" name="description" placeholder="Alcance acustico del proyecto" />
      <Button type="submit">Guardar</Button>
    </form>
  );
}
