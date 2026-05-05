"use client";

import type { FormEvent } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Calculator as CalculatorIcon, Check, ChevronDown, Plus, Search, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

interface Material {
  nombre: string;
  densidad: number;
  tipoMaterial: string;
}

interface MaterialSeleccionado extends Material {
  espesor: number;
}

interface Resultado {
  Rw: number;
  C: number;
  Ctr: number;
  R_frecuencias: Record<number, number>;
}

type CalculatorProps = {
  projectId?: string;
};

type ApiMaterial = Material | {
  nombre: string;
  densidad: number;
  tipo?: string;
  tipo_material?: string;
};

const MATERIALES_FALLBACK: Material[] = [
  { nombre: "Hormigon 200mm", densidad: 2400, tipoMaterial: "rigido" },
  { nombre: "Lana mineral 50mm", densidad: 30, tipoMaterial: "poroso" },
  { nombre: "Vidrio 6mm", densidad: 2500, tipoMaterial: "rigido" },
  { nombre: "Doble vidrio 4-12-4", densidad: 800, tipoMaterial: "composite" },
  { nombre: "Ladrillo ceramico 120mm", densidad: 1800, tipoMaterial: "rigido" },
  { nombre: "Yeso + papel 13mm", densidad: 900, tipoMaterial: "rigido" }
];

const ISO_REFERENCE: Record<number, number> = {
  100: 30,
  125: 35,
  160: 40,
  200: 42,
  250: 44,
  315: 45,
  400: 46,
  500: 47,
  630: 48,
  800: 48,
  1000: 48,
  1250: 48,
  1600: 49,
  2000: 49,
  2500: 50,
  3150: 50,
  4000: 51,
  5000: 52
};

export function Calculator({ projectId = "1" }: CalculatorProps = {}): JSX.Element {
  const [materiales_seleccionados, setMaterialesSeleccionados] = useState<MaterialSeleccionado[]>([]);
  const [frecuencias] = useState<number[] | undefined>(undefined);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [materialesDisponibles, setMaterialesDisponibles] = useState<Material[]>(MATERIALES_FALLBACK);
  const [materialSeleccionado, setMaterialSeleccionado] = useState<Material | null>(null);
  const [dropdownAbierto, setDropdownAbierto] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const buscarMateriales = useCallback(async (search: string): Promise<Material[]> => {
    const normalizedSearch = search.trim().toLowerCase();

    try {
      const response = await fetch(apiUrl(`/api/materiales?search=${encodeURIComponent(search)}`));
      if (response.ok) {
        const data = (await response.json()) as ApiMaterial[];
        return data.map(normalizarMaterial);
      }
    } catch {
      // The backend material endpoint is optional during early UI work.
    }

    if (!normalizedSearch) {
      return MATERIALES_FALLBACK;
    }

    return MATERIALES_FALLBACK.filter((material) => material.nombre.toLowerCase().includes(normalizedSearch));
  }, []);

  useEffect(() => {
    let activo = true;

    async function cargarOpciones(): Promise<void> {
      const materiales = await buscarMateriales(query);
      if (activo) {
        setMaterialesDisponibles(materiales);
      }
    }

    void cargarOpciones();
    return () => {
      activo = false;
    };
  }, [buscarMateriales, query]);

  useEffect(() => {
    function cerrarDropdown(event: MouseEvent): void {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownAbierto(false);
      }
    }

    document.addEventListener("mousedown", cerrarDropdown);
    return () => document.removeEventListener("mousedown", cerrarDropdown);
  }, []);

  const puedeCalcular = materiales_seleccionados.length > 0 && !cargando;

  const chartData = useMemo(() => {
    if (!resultado) {
      return [];
    }

    return Object.entries(resultado.R_frecuencias)
      .map(([frecuencia, valor]) => ({
        frecuencia: Number(frecuencia),
        valor,
        referencia: ISO_REFERENCE[Number(frecuencia)] ?? null
      }))
      .sort((a, b) => a.frecuencia - b.frecuencia);
  }, [resultado]);

  function agregarMaterial(material: Material): void {
    setError(null);
    setResultado(null);
    setMaterialesSeleccionados((actuales) => [
      ...actuales,
      {
        ...material,
        espesor: 0.1
      }
    ]);
  }

  function agregarMaterialElegido(): void {
    const material = materialSeleccionado ?? materialesDisponibles[0];
    if (!material) {
      setError("No hay materiales disponibles para agregar.");
      return;
    }

    agregarMaterial(material);
    setMaterialSeleccionado(null);
    setQuery("");
    setDropdownAbierto(false);
  }

  function actualizarEspesor(index: number, espesor: number): void {
    setMaterialesSeleccionados((actuales) =>
      actuales.map((material, itemIndex) => (itemIndex === index ? { ...material, espesor } : material))
    );
  }

  function eliminarMaterial(index: number): void {
    setMaterialesSeleccionados((actuales) => actuales.filter((_, itemIndex) => itemIndex !== index));
    setResultado(null);
  }

  async function calcular(): Promise<void> {
    setCargando(true);
    setError(null);
    setResultado(null);

    try {
      if (materiales_seleccionados.length === 0) {
        throw new Error("Agrega al menos un material antes de calcular.");
      }

      const response = await fetch(apiUrl("/api/calculations"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          proyecto_id: Number(projectId) || 1,
          nombre: "Calculo acustico",
          materiales: materiales_seleccionados.map((material) => ({
            nombre: material.nombre,
            espesor: material.espesor
          })),
          frecuencias
        })
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = (await response.json()) as { salida?: Resultado };
      if (!data.salida) {
        throw new Error("La API no devolvio resultados de calculo.");
      }

      setResultado({
        ...data.salida,
        R_frecuencias: normalizarFrecuencias(data.salida.R_frecuencias)
      });
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo calcular el aislamiento.");
    } finally {
      setCargando(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    void calcular();
  }

  return (
    <Card className="space-y-6 bg-white text-ink dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100">
      <header className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded bg-teal-50 text-signal dark:bg-teal-950">
          <CalculatorIcon className="h-5 w-5" aria-hidden="true" />
        </span>
        <div>
          <h2 className="text-xl font-semibold">Calculadora Acustica</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">Aislamiento por bandas R(f) e indice Rw.</p>
        </div>
      </header>

      <form className="space-y-6" onSubmit={handleSubmit}>
        <section className="space-y-3">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300" htmlFor="buscar-material">
            Selecciona materiales
          </label>

          <div ref={dropdownRef} className="relative">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                aria-autocomplete="list"
                aria-expanded={dropdownAbierto}
                aria-controls="materiales-listbox"
                id="buscar-material"
                className="h-11 w-full rounded border border-slate-300 bg-white pl-10 pr-10 text-sm text-ink outline-none focus:border-signal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                placeholder="Buscar material..."
                role="combobox"
                type="search"
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setDropdownAbierto(true);
                  setMaterialSeleccionado(null);
                }}
                onFocus={() => setDropdownAbierto(true)}
              />
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            </div>

            {dropdownAbierto ? (
              <div
                className="absolute z-20 mt-2 max-h-64 w-full overflow-auto rounded border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-900"
                id="materiales-listbox"
                role="listbox"
              >
                {materialesDisponibles.length > 0 ? (
                  materialesDisponibles.map((material) => {
                    const selected = materialSeleccionado?.nombre === material.nombre;
                    return (
                      <button
                        key={material.nombre}
                        className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-sm hover:bg-teal-50 dark:hover:bg-slate-800"
                        role="option"
                        type="button"
                        aria-selected={selected}
                        onClick={() => {
                          setMaterialSeleccionado(material);
                          setQuery(material.nombre);
                          setDropdownAbierto(false);
                        }}
                      >
                        <span>
                          <span className="block font-medium">{material.nombre}</span>
                          <span className="text-xs text-slate-600 dark:text-slate-400">
                            {material.densidad} kg/m3 | {material.tipoMaterial}
                          </span>
                        </span>
                        {selected ? <Check className="h-4 w-4 text-signal" aria-hidden="true" /> : null}
                      </button>
                    );
                  })
                ) : (
                  <p className="px-3 py-3 text-sm text-slate-600 dark:text-slate-400">No se encontraron materiales.</p>
                )}
              </div>
            ) : null}
          </div>

          <Button type="button" variant="secondary" onClick={agregarMaterialElegido}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            Agregar material
          </Button>
        </section>

        <section className="space-y-3">
          {materiales_seleccionados.length === 0 ? (
            <p className="rounded border border-dashed border-slate-300 p-4 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-400">
              Aun no hay materiales seleccionados.
            </p>
          ) : (
            <div className="space-y-2">
              {materiales_seleccionados.map((material, index) => (
                <div
                  key={`${material.nombre}-${index}`}
                  className="grid gap-3 rounded border border-slate-200 p-3 dark:border-slate-700 sm:grid-cols-[1fr_150px_44px]"
                >
                  <div>
                    <p className="text-sm font-medium">{material.nombre}</p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {material.densidad} kg/m3 | {material.tipoMaterial}
                    </p>
                  </div>

                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                    Espesor m
                    <input
                      className="mt-2 h-10 w-full rounded border border-slate-300 bg-white px-3 text-sm text-ink outline-none focus:border-signal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                      min={0.001}
                      step={0.001}
                      type="number"
                      value={material.espesor}
                      onChange={(event) => actualizarEspesor(index, Number(event.target.value))}
                    />
                  </label>

                  <button
                    aria-label={`Eliminar ${material.nombre}`}
                    className="flex h-10 w-10 items-center justify-center self-end rounded border border-slate-300 text-slate-600 transition hover:border-red-300 hover:text-red-600 dark:border-slate-700 dark:text-slate-300"
                    type="button"
                    onClick={() => eliminarMaterial(index)}
                  >
                    <Trash2 className="h-4 w-4" aria-hidden="true" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {error ? (
          <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-200">
            {error}
          </p>
        ) : null}

        <div className="flex justify-center">
          <Button type="submit" disabled={!puedeCalcular}>
            {cargando ? "Calculando..." : "Calcular"}
          </Button>
        </div>
      </form>

      {resultado ? (
        <section className="space-y-4 border-t border-slate-200 pt-5 dark:border-slate-700">
          <ResultsDisplay resultado={resultado} />
          <SpectrumChart data={chartData} />
        </section>
      ) : null}
    </Card>
  );
}

function ResultsDisplay({ resultado }: { resultado: Resultado }): JSX.Element {
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <ResultMetric label="Rw" value={`${resultado.Rw} dB`} />
      <ResultMetric label="C" value={`${resultado.C} dB`} />
      <ResultMetric label="Ctr" value={`${resultado.Ctr} dB`} />
    </div>
  );
}

function ResultMetric({ label, value }: { label: string; value: string }): JSX.Element {
  return (
    <div className="rounded border border-slate-200 bg-surface p-4 dark:border-slate-700 dark:bg-slate-900">
      <p className="text-xs font-medium uppercase text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function SpectrumChart({
  data
}: {
  data: Array<{ frecuencia: number; valor: number; referencia: number | null }>;
}): JSX.Element {
  const width = 720;
  const height = 260;
  const padding = 36;
  const maxY = Math.max(...data.flatMap((point) => [point.valor, point.referencia ?? 0]), 60);
  const minFrequency = Math.min(...data.map((point) => point.frecuencia), 100);
  const maxFrequency = Math.max(...data.map((point) => point.frecuencia), 5000);

  const x = (frequency: number): number => {
    if (minFrequency === maxFrequency) {
      return width / 2;
    }

    const minLog = Math.log10(minFrequency);
    const maxLog = Math.log10(maxFrequency);
    return padding + ((Math.log10(frequency) - minLog) / (maxLog - minLog)) * (width - padding * 2);
  };

  const y = (value: number): number => height - padding - (value / maxY) * (height - padding * 2);

  const rPath = data.map((point, index) => `${index === 0 ? "M" : "L"} ${x(point.frecuencia)} ${y(point.valor)}`).join(" ");
  const isoPath = data
    .filter((point) => point.referencia !== null)
    .map((point, index) => `${index === 0 ? "M" : "L"} ${x(point.frecuencia)} ${y(point.referencia ?? 0)}`)
    .join(" ");

  return (
    <div className="rounded border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-950">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold">Grafico R(f)</h3>
        <div className="flex gap-4 text-xs text-slate-600 dark:text-slate-400">
          <span className="inline-flex items-center gap-2">
            <span className="h-0.5 w-6 bg-signal" />
            Calculado
          </span>
          <span className="inline-flex items-center gap-2">
            <span className="h-0.5 w-6 bg-slate-400" />
            ISO 717-1
          </span>
        </div>
      </div>

      <svg aria-label="Grafico de aislamiento acustico por frecuencia" className="h-auto w-full" viewBox={`0 0 ${width} ${height}`}>
        <line x1={padding} x2={padding} y1={padding} y2={height - padding} className="stroke-slate-300" />
        <line x1={padding} x2={width - padding} y1={height - padding} y2={height - padding} className="stroke-slate-300" />
        <text x={padding} y={18} className="fill-slate-500 text-[12px]">
          R (dB)
        </text>
        <text x={width - 116} y={height - 8} className="fill-slate-500 text-[12px]">
          Frecuencia (Hz)
        </text>
        {isoPath ? <path d={isoPath} fill="none" className="stroke-slate-400" strokeDasharray="6 5" strokeWidth={2} /> : null}
        {rPath ? <path d={rPath} fill="none" className="stroke-signal" strokeWidth={3} /> : null}
        {data.map((point) => (
          <g key={point.frecuencia}>
            <circle cx={x(point.frecuencia)} cy={y(point.valor)} r={4} className="fill-signal" />
            <text x={x(point.frecuencia) - 12} y={height - 16} className="fill-slate-500 text-[10px]">
              {point.frecuencia}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function normalizarMaterial(material: ApiMaterial): Material {
  if ("tipoMaterial" in material) {
    return material;
  }

  return {
    nombre: material.nombre,
    densidad: material.densidad,
    tipoMaterial: material.tipo_material ?? material.tipo ?? "rigido"
  };
}

function normalizarFrecuencias(R_frecuencias: Record<number, number>): Record<number, number> {
  return Object.fromEntries(
    Object.entries(R_frecuencias).map(([frecuencia, valor]) => [Number(frecuencia), Number(valor)])
  ) as Record<number, number>;
}

function apiUrl(path: string): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  return baseUrl ? `${baseUrl}${path}` : path;
}
