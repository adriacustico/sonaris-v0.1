import { Calculator } from "@/components/Calculator";

export default function CalculationsPage(): JSX.Element {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Calculadora acústica</h1>
        <p className="mt-1 text-sm text-slate-600">
          Selecciona materiales y capas para obtener el índice Rw y el espectro R(f).
        </p>
      </div>
      <Calculator />
    </div>
  );
}
