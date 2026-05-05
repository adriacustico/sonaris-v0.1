"use client";

import type { FormEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Plus, Trash2 } from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface CatalogoMaterial {
  nombre: string;
  densidad: number;
  tipo: string;
}

interface CapaItem {
  nombre: string;
  densidad: number;
  tipo: string;
  espesorMm: number;
}

interface Resultado {
  Rw: number;
  C: number;
  Ctr: number;
  R_frecuencias: Record<string, number>;
}

type ApiMaterial = {
  nombre: string;
  densidad: number;
  tipo?: string;
  tipo_material?: string;
  tipoMaterial?: string;
};

type TipoUnion = "rigida" | "montantes_metal" | "montantes_madera" | "canal_resiliente" | "aire";

// ─── Constants ───────────────────────────────────────────────────────────────

const FALLBACK_MATERIALES: CatalogoMaterial[] = [
  { nombre: "Hormigon 200mm", densidad: 2400, tipo: "rigido" },
  { nombre: "Ladrillo ceramico 120mm", densidad: 1800, tipo: "rigido" },
  { nombre: "Yeso + papel 13mm", densidad: 900, tipo: "rigido" },
  { nombre: "Vidrio 6mm", densidad: 2500, tipo: "rigido" },
  { nombre: "Lana mineral 50mm", densidad: 30, tipo: "poroso" },
  { nombre: "Lana de roca 70mm", densidad: 70, tipo: "poroso" },
  { nombre: "Doble vidrio 4-12-4", densidad: 800, tipo: "composite" },
  { nombre: "Tabique metalcon doble placa", densidad: 520, tipo: "composite" },
];

const FRECUENCIAS_CHART = [125, 200, 315, 500, 800, 1250, 2000, 3150, 5000];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function defaultEspesorMm(nombre: string): number {
  const m = nombre.match(/(\d+(?:[.,]\d+)?)\s*mm/i);
  return m ? parseInt(m[1]) : 100;
}

function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL;
  return base ? `${base}${path}` : path;
}

function normalizarMaterial(m: ApiMaterial): CatalogoMaterial {
  return {
    nombre: m.nombre,
    densidad: m.densidad,
    tipo: m.tipoMaterial ?? m.tipo_material ?? m.tipo ?? "rigido",
  };
}

function abreviarFrecuencia(hz: number): string {
  if (hz >= 1000) return `${hz / 1000}k`;
  return String(hz);
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function EsquemaTabique({ capas }: { capas: CapaItem[] }): JSX.Element {
  const SVG_H = 160;
  const LABEL_H = 36;
  const MIN_W = 22;
  const MAX_TOTAL_W = 260;
  const GAP = 3;

  if (capas.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-slate-400">
        Añade materiales para ver el esquema
      </div>
    );
  }

  const totalMm = capas.reduce((s, c) => s + c.espesorMm, 0);
  const available = MAX_TOTAL_W - GAP * (capas.length - 1);
  const scale = Math.min(1, available / Math.max(totalMm, 1));

  const widths = capas.map((c) => Math.max(MIN_W, c.espesorMm * scale));
  const totalW = widths.reduce((s, w) => s + w, 0) + GAP * (capas.length - 1);
  const svgW = Math.max(totalW + 8, 120);

  const fillColor = (tipo: string): string => {
    if (tipo === "poroso") return "#e2e8f0";
    if (tipo === "composite") return "#cbd5e1";
    return "url(#hatch-rigido)";
  };

  const strokeColor = (tipo: string): string => {
    if (tipo === "poroso") return "#94a3b8";
    return "#64748b";
  };

  const startX = (svgW - totalW) / 2;
  const positions = widths.map((w, i) => ({
    x: startX + widths.slice(0, i).reduce((s, v) => s + v, 0) + GAP * i,
    w,
  }));

  return (
    <svg
      viewBox={`0 0 ${svgW} ${SVG_H + LABEL_H}`}
      className="mx-auto h-auto w-full max-w-[300px]"
      aria-label="Esquema de sección transversal del tabique"
    >
      <defs>
        <pattern
          id="hatch-rigido"
          width="6"
          height="6"
          patternUnits="userSpaceOnUse"
          patternTransform="rotate(45)"
        >
          <line x1="0" y1="0" x2="0" y2="6" stroke="#94a3b8" strokeWidth="1.5" />
        </pattern>
      </defs>

      {capas.map((capa, i) => {
        const { x, w } = positions[i];
        const labelX = x + w / 2;
        const base = capa.nombre.replace(/\s+\d+mm$/i, "");
        const nombreCorto = base.length > 14 ? base.slice(0, 13) + "…" : base;

        return (
          <g key={`${capa.nombre}-${i}`}>
            <rect
              x={x}
              y={0}
              width={w}
              height={SVG_H}
              fill={fillColor(capa.tipo)}
              stroke={strokeColor(capa.tipo)}
              strokeWidth={1}
              rx={2}
            />
            <text
              x={labelX}
              y={SVG_H + 14}
              textAnchor="middle"
              className="fill-slate-600"
              fontSize={9}
            >
              {nombreCorto}
            </text>
            <text
              x={labelX}
              y={SVG_H + 26}
              textAnchor="middle"
              className="fill-slate-400"
              fontSize={8}
            >
              {capa.espesorMm} mm
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function GraficoR({
  data,
}: {
  data: Array<{ frecuencia: number; valor: number }>;
}): JSX.Element {
  const ML = 44;
  const MR = 16;
  const MT = 20;
  const MB = 36;
  const W = 520;
  const H = 220;
  const innerW = W - ML - MR;
  const innerH = H - MT - MB;
  const Y_MAX = 100;
  const Y_TICKS = [0, 25, 50, 75, 100];
  const F_MIN = 100;
  const F_MAX = 5000;

  const xPos = (hz: number): number =>
    ML + ((Math.log10(hz) - Math.log10(F_MIN)) / (Math.log10(F_MAX) - Math.log10(F_MIN))) * innerW;

  const yPos = (db: number): number =>
    MT + innerH - (db / Y_MAX) * innerH;

  const linePath = data.length < 2
    ? ""
    : data
        .map((p, i) => `${i === 0 ? "M" : "L"} ${xPos(p.frecuencia).toFixed(1)} ${yPos(p.valor).toFixed(1)}`)
        .join(" ");

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="h-auto w-full"
      aria-label="Gráfico de aislamiento acústico por frecuencia"
    >
      {/* Grid lines */}
      {Y_TICKS.map((db) => (
        <g key={db}>
          <line
            x1={ML}
            x2={W - MR}
            y1={yPos(db)}
            y2={yPos(db)}
            stroke={db === 0 ? "#cbd5e1" : "#f1f5f9"}
            strokeWidth={db === 0 ? 1 : 1}
          />
          <text
            x={ML - 6}
            y={yPos(db) + 4}
            textAnchor="end"
            fontSize={10}
            fill="#94a3b8"
          >
            {db}
          </text>
        </g>
      ))}

      {/* Axes */}
      <line x1={ML} x2={ML} y1={MT} y2={H - MB} stroke="#cbd5e1" strokeWidth={1} />
      <line x1={ML} x2={W - MR} y1={H - MB} y2={H - MB} stroke="#cbd5e1" strokeWidth={1} />

      {/* X-axis labels */}
      {FRECUENCIAS_CHART.map((hz) => (
        <text
          key={hz}
          x={xPos(hz)}
          y={H - MB + 14}
          textAnchor="middle"
          fontSize={9}
          fill="#94a3b8"
        >
          {abreviarFrecuencia(hz)}
        </text>
      ))}

      {/* Axis titles */}
      <text
        x={ML - 32}
        y={MT + innerH / 2}
        textAnchor="middle"
        fontSize={10}
        fill="#64748b"
        transform={`rotate(-90, ${ML - 32}, ${MT + innerH / 2})`}
      >
        R (dB)
      </text>
      <text x={ML + innerW / 2} y={H - 2} textAnchor="middle" fontSize={10} fill="#64748b">
        Frecuencia (Hz)
      </text>

      {/* Data line */}
      {linePath && (
        <path d={linePath} fill="none" stroke="#2563eb" strokeWidth={2} strokeLinejoin="round" />
      )}

      {/* Data points */}
      {data.map((p) => (
        <circle
          key={p.frecuencia}
          cx={xPos(p.frecuencia)}
          cy={yPos(p.valor)}
          r={3}
          fill="#2563eb"
        />
      ))}

      {/* Empty state */}
      {data.length === 0 && (
        <text
          x={ML + innerW / 2}
          y={MT + innerH / 2}
          textAnchor="middle"
          fontSize={12}
          fill="#cbd5e1"
        >
          Sin datos
        </text>
      )}
    </svg>
  );
}

function MetricaCard({
  label,
  value,
}: {
  label: string;
  value: number | null;
}): JSX.Element {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 text-center">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      {value !== null ? (
        <>
          <p className="mt-1 text-3xl font-bold text-ink">{value}</p>
          <p className="text-xs text-slate-400">dB</p>
        </>
      ) : (
        <p className="mt-1 text-3xl font-bold text-slate-200">—</p>
      )}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

type CalculatorProps = { projectId?: string };

export function Calculator({ projectId = "1" }: CalculatorProps = {}): JSX.Element {
  const [catalogo, setCatalogo] = useState<CatalogoMaterial[]>(FALLBACK_MATERIALES);
  const [capas, setCapas] = useState<CapaItem[]>([]);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Double-leaf (doble hoja) state
  const [modoDoble, setModoDoble] = useState(false);
  const [separacionMm, setSeparacionMm] = useState<number>(90);
  const [tipoUnion, setTipoUnion] = useState<TipoUnion>("montantes_metal");
  const [tieneRelleno, setTieneRelleno] = useState(false);

  // Load full catalog from API
  const cargarCatalogo = useCallback(async (): Promise<void> => {
    try {
      const res = await fetch(apiUrl("/api/materiales/"));
      if (res.ok) {
        const data = (await res.json()) as ApiMaterial[];
        setCatalogo(data.map(normalizarMaterial));
      }
    } catch {
      // fall back to static list
    }
  }, []);

  useEffect(() => { void cargarCatalogo(); }, [cargarCatalogo]);

  function agregarCapa(): void {
    if (capas.length >= 8) return;
    const primero = catalogo[0];
    if (!primero) return;
    setCapas((prev) => [
      ...prev,
      {
        nombre: primero.nombre,
        densidad: primero.densidad,
        tipo: primero.tipo,
        espesorMm: defaultEspesorMm(primero.nombre),
      },
    ]);
    setResultado(null);
  }

  function eliminarCapa(index: number): void {
    setCapas((prev) => prev.filter((_, i) => i !== index));
    setResultado(null);
  }

  function cambiarMaterial(index: number, nombre: string): void {
    const mat = catalogo.find((m) => m.nombre === nombre);
    if (!mat) return;
    setCapas((prev) =>
      prev.map((c, i) =>
        i === index
          ? { nombre: mat.nombre, densidad: mat.densidad, tipo: mat.tipo, espesorMm: defaultEspesorMm(mat.nombre) }
          : c
      )
    );
    setResultado(null);
  }

  function cambiarEspesor(index: number, mm: number): void {
    setCapas((prev) =>
      prev.map((c, i) => (i === index ? { ...c, espesorMm: Math.max(1, mm) } : c))
    );
    setResultado(null);
  }

  const chartData = useMemo(() => {
    if (!resultado) return [];
    return Object.entries(resultado.R_frecuencias)
      .map(([f, v]) => ({ frecuencia: Number(f), valor: Number(v) }))
      .sort((a, b) => a.frecuencia - b.frecuencia);
  }, [resultado]);

  async function calcular(): Promise<void> {
    if (capas.length === 0) return;
    setCargando(true);
    setError(null);
    try {
      const res = await fetch(apiUrl("/api/calculations/"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          proyecto_id: Number(projectId) || 1,
          nombre: "Calculo acustico",
          materiales: capas.map((c) => ({ nombre: c.nombre, espesor: c.espesorMm / 1000 })),
          ...(modoDoble && capas.length === 2 && {
            separacion_mm: separacionMm,
            tipo_union: tipoUnion,
            tiene_relleno: tieneRelleno,
          }),
        }),
      });
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = (await res.json()) as { salida?: Resultado };
      if (!data.salida) throw new Error("La API no devolvió resultados.");
      setResultado(data.salida);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo calcular.");
    } finally {
      setCargando(false);
    }
  }

  function handleSubmit(e: FormEvent): void {
    e.preventDefault();
    void calcular();
  }

  const puedeCalcular = capas.length > 0 && !cargando;

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-[340px_1fr_1fr]">

        {/* ── Columna izquierda: Configurador ── */}
        <div className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-5">
          <div>
            <h2 className="text-base font-semibold text-ink">Configurador de Tabique</h2>
            <p className="mt-0.5 text-xs text-slate-400">
              Diseña y simula el aislamiento acústico multicapa.
            </p>
          </div>

          {/* Sencillo / Doble toggle */}
          <div className="flex rounded-lg border border-slate-200 p-0.5">
            {(["Sencillo", "Doble"] as const).map((label) => {
              const active = modoDoble === (label === "Doble");
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => { setModoDoble(label === "Doble"); setResultado(null); }}
                  className={`flex-1 rounded-md py-1.5 text-xs font-semibold transition ${
                    active
                      ? "bg-signal text-white shadow-sm"
                      : "text-slate-500 hover:text-ink"
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>

          {/* Union section — visible only in Doble mode */}
          {modoDoble && (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                Unión entre capas
              </p>

              <div className="grid grid-cols-[1fr_72px] gap-2">
                <div>
                  <p className="mb-1 text-[10px] text-slate-400">Tipo</p>
                  <select
                    value={tipoUnion}
                    onChange={(e) => { setTipoUnion(e.target.value as TipoUnion); setResultado(null); }}
                    className="h-9 w-full rounded-md border border-slate-300 bg-white px-2 text-xs text-ink focus:border-signal focus:outline-none"
                  >
                    <option value="rigida">Rígida</option>
                    <option value="montantes_metal">Montantes metal (Metalcon)</option>
                    <option value="montantes_madera">Montantes madera</option>
                    <option value="canal_resiliente">Canal resiliente</option>
                    <option value="aire">Sin montantes (aire)</option>
                  </select>
                </div>
                <div>
                  <p className="mb-1 text-[10px] text-slate-400">Sep. (mm)</p>
                  <input
                    type="number"
                    min={10}
                    max={500}
                    step={5}
                    value={separacionMm}
                    onChange={(e) => { setSeparacionMm(parseInt(e.target.value) || 90); setResultado(null); }}
                    className="h-9 w-full rounded-md border border-slate-300 bg-white px-2 text-center text-xs text-ink focus:border-signal focus:outline-none"
                  />
                </div>
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={tieneRelleno}
                  onChange={(e) => { setTieneRelleno(e.target.checked); setResultado(null); }}
                  className="h-3.5 w-3.5 accent-signal"
                />
                <span className="text-xs text-slate-600">Cavidad con lana mineral</span>
              </label>

              {capas.length !== 2 && (
                <p className="text-[10px] text-amber-600">
                  El modo Doble requiere exactamente 2 capas.
                </p>
              )}
            </div>
          )}

          {/* Layers */}
          <div className="flex flex-col gap-3">
            {capas.length === 0 && (
              <p className="rounded-lg border border-dashed border-slate-200 p-4 text-center text-xs text-slate-400">
                Pulsa &ldquo;+ Añadir Capa&rdquo; para empezar
              </p>
            )}

            {capas.map((capa, i) => (
              <div key={i} className="rounded-lg border border-slate-200 p-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-semibold text-ink">Capa {i + 1}</span>
                  <button
                    type="button"
                    aria-label={`Eliminar capa ${i + 1}`}
                    onClick={() => eliminarCapa(i)}
                    className="rounded p-0.5 text-slate-400 transition hover:text-red-500"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                <div className="grid grid-cols-[1fr_72px] gap-2">
                  <div>
                    <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                      Material
                    </p>
                    <select
                      value={capa.nombre}
                      onChange={(e) => cambiarMaterial(i, e.target.value)}
                      className="h-9 w-full rounded-md border border-slate-300 bg-white px-2 text-xs text-ink focus:border-signal focus:outline-none"
                    >
                      {catalogo.map((m) => (
                        <option key={m.nombre} value={m.nombre}>
                          {m.nombre}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                      Esp. (mm)
                    </p>
                    <input
                      type="number"
                      min={1}
                      max={999}
                      step={1}
                      value={capa.espesorMm}
                      onChange={(e) => cambiarEspesor(i, parseInt(e.target.value) || 1)}
                      className="h-9 w-full rounded-md border border-slate-300 bg-white px-2 text-center text-xs text-ink focus:border-signal focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Add layer button */}
          {capas.length < 8 && (
            <button
              type="button"
              onClick={agregarCapa}
              className="flex items-center justify-center gap-1.5 rounded-lg border border-dashed border-slate-300 py-2 text-xs font-medium text-slate-500 transition hover:border-signal hover:text-signal"
            >
              <Plus className="h-3.5 w-3.5" />
              Añadir Capa
            </button>
          )}

          {/* Error */}
          {error && (
            <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
              {error}
            </p>
          )}

          {/* Calculate button */}
          <button
            type="submit"
            disabled={!puedeCalcular}
            className="mt-auto rounded-lg bg-signal px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {cargando ? "Calculando…" : "Calcular"}
          </button>
        </div>

        {/* ── Columna central: Esquema ── */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-ink">Esquema Tabique</h2>
          <div className="flex flex-1 items-center justify-center">
            <EsquemaTabique capas={capas} />
          </div>
        </div>

        {/* ── Columna derecha: Gráfico + métricas ── */}
        <div className="flex flex-col gap-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-3 text-sm font-semibold text-ink">Aislamiento Acústico R</h2>
            <GraficoR data={chartData} />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <MetricaCard label="Rw" value={resultado?.Rw ?? null} />
            <MetricaCard label="C" value={resultado?.C ?? null} />
            <MetricaCard label="Ctr" value={resultado?.Ctr ?? null} />
          </div>
        </div>

      </div>
    </form>
  );
}
