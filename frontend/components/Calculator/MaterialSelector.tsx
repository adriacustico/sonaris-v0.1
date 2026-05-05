import { Input } from "@/components/ui/Input";

export function MaterialSelector(): JSX.Element {
  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold text-ink">Material</h2>
      <Input label="Tipo" name="material" placeholder="concrete" />
      <Input label="Espesor mm" name="thickness" placeholder="120" type="number" />
    </div>
  );
}
