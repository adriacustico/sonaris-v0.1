"use client";

import type { FormEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Plus, Trash2 } from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface CatalogoMaterial {
  nombre: string;
  densidad: number;
  tipo: string;
  categoria: string;
}

interface PanelLayer {
  nombre: string;
  densidad: number;
  tipo: string;
  espesorUnitarioMm: number;
  cantidad: number;
}

interface UnionConfig {
  rellenoNombre: string | null;
  rellenoEspesorMm: number;
  camaraAireMm: number;
  tipoMontantes: string;
}

interface Resultado {
  Rw: number;
  C: number;
  Ctr: number;
  R_frecuencias: Record<string, number>;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const FALLBACK_RIGID: CatalogoMaterial[] = [
  { nombre: "Placa yeso 15mm",        densidad: 850,  tipo: "rigido",    categoria: "rigid" },
  { nombre: "OSB 15mm",               densidad: 620,  tipo: "rigido",    categoria: "rigid" },
  { nombre: "Hormigon 200mm",         densidad: 2400, tipo: "rigido",    categoria: "rigid" },
  { nombre: "Ladrillo ceramico 120mm",densidad: 1800, tipo: "rigido",    categoria: "rigid" },
  { nombre: "Fibrocemento 10mm",      densidad: 1350, tipo: "rigido",    categoria: "rigid" },
  { nombre: "Contrachapado 18mm",     densidad: 600,  tipo: "rigido",    categoria: "rigid" },
];

const FALLBACK_FILLING: CatalogoMaterial[] = [
  { nombre: "Lana mineral 50mm",   densidad: 30,  tipo: "poroso", categoria: "filling" },
  { nombre: "Lana de vidrio 50mm", densidad: 25,  tipo: "poroso", categoria: "filling" },
  { nombre: "Lana de roca 70mm",   densidad: 70,  tipo: "poroso", categoria: "filling" },
  { nombre: "Espuma acustica 25mm",densidad: 40,  tipo: "poroso", categoria: "filling" },
];

const FRECUENCIAS_CHART = [125, 200, 315, 500, 800, 1250, 2000, 3150, 5000];

const OPCIONES_MONTANTES = [
  { value: "montantes_metal",  label: "Metal (Metalcon)" },
  { value: "montantes_madera", label: "Madera" },
  { value: "canal_resiliente", label: "Canal resiliente" },
  { value: "rigida",           label: "Rígida (sin cavidad)" },
  { value: "aire",             label: "Flotante (sin contacto)" },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function defaultEspesorMm(nombre: string): number {
  const m = nombre.match(/(\d+(?:[.,]\d+)?)\s*mm/i);
  return m ? parseInt(m[1]) : 100;
}

function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL;
  return base ? `${base}${path}` : path;
}

function abreviarFrecuencia(hz: number): string {
  return hz >= 1000 ? `${hz / 1000}k` : String(hz);
}

// ─── EsquemaTabique ───────────────────────────────────────────────────────────

function EsquemaTabique({
  capa1,
  union,
  capa2,
}: {
  capa1: PanelLayer[];
  union: UnionConfig;
  capa2: PanelLayer[];
}): JSX.Element {
  const SVG_H = 160;
  const LABEL_H = 36;
  const MAX_W = 280;
  const GAP = 2;
  const MIN_W = 8;

  const hasContent = capa1.length > 0 || capa2.length > 0;

  if (!hasContent) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-slate-400">
        Añade materiales para ver el esquema
      </div>
    );
  }

  // Build a list of "sections" (left-to-right)
  type Section = { label: string; mm: number; fill: string; stroke: string; pattern?: string };
  const sections: Section[] = [];

  for (const l of capa1) {
    sections.push({
      label: l.nombre.replace(/\s+\d+mm$/i, "").slice(0, 12),
      mm: l.espesorUnitarioMm * l.cantidad,
      fill: "url(#hatch-rigid)",
      stroke: "#64748b",
    });
  }

  const totalCavidad = (union.rellenoNombre ? union.rellenoEspesorMm : 0) + union.camaraAireMm;
  if (totalCavidad > 0) {
    const lbl = union.rellenoNombre
      ? union.rellenoNombre.replace(/\s+\d+mm$/i, "").slice(0, 12)
      : "Cámara aire";
    sections.push({
      label: lbl,
      mm: totalCavidad,
      fill: union.rellenoNombre ? "#e2e8f0" : "none",
      stroke: "#94a3b8",
    });
  }

  for (const l of capa2) {
    sections.push({
      label: l.nombre.replace(/\s+\d+mm$/i, "").slice(0, 12),
      mm: l.espesorUnitarioMm * l.cantidad,
      fill: "url(#hatch-rigid)",
      stroke: "#64748b",
    });
  }

  const totalMm = sections.reduce((s, x) => s + x.mm, 0);
  const available = MAX_W - GAP * (sections.length - 1);
  const scale = Math.min(1, available / Math.max(totalMm, 1));
  const widths = sections.map((s) => Math.max(MIN_W, s.mm * scale));
  const totalW = widths.reduce((a, b) => a + b, 0) + GAP * (sections.length - 1);
  const startX = (MAX_W - totalW) / 2 + 4;

  const positions = widths.map((w, i) => ({
    x: startX + widths.slice(0, i).reduce((a, b) => a + b, 0) + GAP * i,
    w,
  }));

  return (
    <svg
      viewBox={`0 0 ${MAX_W + 8} ${SVG_H + LABEL_H}`}
      className="mx-auto h-auto w-full max-w-[320px]"
      aria-label="Sección transversal del tabique"
    >
      <defs>
        <pattern id="hatch-rigid" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="6" stroke="#94a3b8" strokeWidth="1.5" />
        </pattern>
      </defs>

      {sections.map((sec, i) => {
        const { x, w } = positions[i];
        return (
          <g key={`${sec.label}-${i}`}>
            <rect
              x={x} y={0} width={w} height={SVG_H}
              fill={sec.fill}
              stroke={sec.stroke}
              strokeWidth={1}
              strokeDasharray={sec.fill === "none" ? "4 3" : undefined}
              rx={2}
            />
            <text x={x + w / 2} y={SVG_H + 14} textAnchor="middle" className="fill-slate-600" fontSize={8}>
              {sec.label}
            </text>
            <text x={x + w / 2} y={SVG_H + 26} textAnchor="middle" className="fill-slate-400" fontSize={7}>
              {sec.mm} mm
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// ─── GraficoR ─────────────────────────────────────────────────────────────────

function GraficoR({ data }: { data: Array<{ frecuencia: number; valor: number }> }): JSX.Element {
  const ML = 44; const MR = 16; const MT = 20; const MB = 36;
  const W = 520; const H = 200;
  const innerW = W - ML - MR; const innerH = H - MT - MB;
  const F_MIN = 100; const F_MAX = 5000; const Y_MAX = 100;
  const Y_TICKS = [0, 25, 50, 75, 100];

  const xPos = (hz: number) =>
    ML + ((Math.log10(hz) - Math.log10(F_MIN)) / (Math.log10(F_MAX) - Math.log10(F_MIN))) * innerW;
  const yPos = (db: number) => MT + innerH - (db / Y_MAX) * innerH;

  const linePath = data.length < 2
    ? ""
    : data.map((p, i) => `${i === 0 ? "M" : "L"} ${xPos(p.frecuencia).toFixed(1)} ${yPos(p.valor).toFixed(1)}`).join(" ");

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" aria-label="Gráfico R(f)">
      {Y_TICKS.map((db) => (
        <g key={db}>
          <line x1={ML} x2={W - MR} y1={yPos(db)} y2={yPos(db)} stroke={db === 0 ? "#cbd5e1" : "#f1f5f9"} strokeWidth={1} />
          <text x={ML - 6} y={yPos(db) + 4} textAnchor="end" fontSize={10} fill="#94a3b8">{db}</text>
        </g>
      ))}
      <line x1={ML} x2={ML} y1={MT} y2={H - MB} stroke="#cbd5e1" strokeWidth={1} />
      <line x1={ML} x2={W - MR} y1={H - MB} y2={H - MB} stroke="#cbd5e1" strokeWidth={1} />
      {FRECUENCIAS_CHART.map((hz) => (
        <text key={hz} x={xPos(hz)} y={H - MB + 14} textAnchor="middle" fontSize={9} fill="#94a3b8">
          {abreviarFrecuencia(hz)}
        </text>
      ))}
      <text x={ML - 32} y={MT + innerH / 2} textAnchor="middle" fontSize={10} fill="#64748b" transform={`rotate(-90, ${ML - 32}, ${MT + innerH / 2})`}>R (dB)</text>
      <text x={ML + innerW / 2} y={H - 2} textAnchor="middle" fontSize={10} fill="#64748b">Frecuencia (Hz)</text>
      {linePath && <path d={linePath} fill="none" stroke="#2563eb" strokeWidth={2} strokeLinejoin="round" />}
      {data.map((p) => (
        <circle key={p.frecuencia} cx={xPos(p.frecuencia)} cy={yPos(p.valor)} r={3} fill="#2563eb" />
      ))}
      {data.length === 0 && (
        <text x={ML + innerW / 2} y={MT + innerH / 2} textAnchor="middle" fontSize={12} fill="#cbd5e1">Sin datos</text>
      )}
    </svg>
  );
}

// ─── TablaResultados ──────────────────────────────────────────────────────────

function TablaResultados({ data }: { data: Array<{ frecuencia: number; valor: number }> }): JSX.Element {
  if (data.length === 0) {
    return (
      <p className="py-4 text-center text-xs text-slate-400">Sin datos. Pulsa Calcular.</p>
    );
  }
  return (
    <div className="overflow-auto rounded-lg border border-slate-200">
      <table className="w-full text-xs">
        <thead className="bg-slate-50 text-[10px] uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-3 py-1.5 text-right">Hz</th>
            <th className="px-3 py-1.5 text-right">R (dB)</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.frecuencia} className="border-t border-slate-100">
              <td className="px-3 py-1 text-right tabular-nums text-ink">{row.frecuencia}</td>
              <td className="px-3 py-1 text-right tabular-nums font-medium text-ink">{row.valor.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── MetricaCard ──────────────────────────────────────────────────────────────

function MetricaCard({ label, value }: { label: string; value: number | null }): JSX.Element {
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

// ─── CapaSection ─────────────────────────────────────────────────────────────

function CapaSection({
  title,
  accent,
  capas,
  catalogo,
  onAgregar,
  onEliminar,
  onCambiarMaterial,
  onCambiarEspesor,
  onCambiarCantidad,
}: {
  title: string;
  accent: string;
  capas: PanelLayer[];
  catalogo: CatalogoMaterial[];
  onAgregar: () => void;
  onEliminar: (i: number) => void;
  onCambiarMaterial: (i: number, nombre: string) => void;
  onCambiarEspesor: (i: number, mm: number) => void;
  onCambiarCantidad: (i: number, qty: number) => void;
}): JSX.Element {
  return (
    <div className={`rounded-lg border-2 ${accent} p-3 space-y-2`}>
      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">{title}</p>

      {capas.length === 0 && (
        <p className="rounded border border-dashed border-slate-200 p-2 text-center text-[10px] text-slate-400">
          Sin materiales
        </p>
      )}

      {capas.map((capa, i) => (
        <div key={i} className="grid grid-cols-[1fr_44px_36px_auto] items-end gap-1.5">
          <div>
            {i === 0 && <p className="mb-0.5 text-[9px] text-slate-400">MATERIAL</p>}
            <select
              value={capa.nombre}
              onChange={(e) => onCambiarMaterial(i, e.target.value)}
              className="h-8 w-full rounded border border-slate-300 bg-white px-1.5 text-[10px] text-ink focus:border-signal focus:outline-none"
            >
              {catalogo.map((m) => (
                <option key={m.nombre} value={m.nombre}>{m.nombre}</option>
              ))}
            </select>
          </div>
          <div>
            {i === 0 && <p className="mb-0.5 text-[9px] text-slate-400">ESP (mm)</p>}
            <input
              type="number" min={1} max={999} step={1}
              value={capa.espesorUnitarioMm}
              onChange={(e) => onCambiarEspesor(i, parseInt(e.target.value) || 1)}
              className="h-8 w-full rounded border border-slate-300 bg-white px-1 text-center text-[10px] text-ink focus:border-signal focus:outline-none"
            />
          </div>
          <div>
            {i === 0 && <p className="mb-0.5 text-[9px] text-slate-400">QTY</p>}
            <input
              type="number" min={1} max={10} step={1}
              value={capa.cantidad}
              onChange={(e) => onCambiarCantidad(i, parseInt(e.target.value) || 1)}
              className="h-8 w-full rounded border border-slate-300 bg-white px-1 text-center text-[10px] text-ink focus:border-signal focus:outline-none"
            />
          </div>
          <button
            type="button"
            onClick={() => onEliminar(i)}
            className="mb-0 h-8 rounded px-1 text-slate-400 hover:text-red-500"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      ))}

      <button
        type="button"
        onClick={onAgregar}
        className="flex w-full items-center justify-center gap-1 rounded border border-dashed border-slate-300 py-1 text-[10px] text-slate-500 hover:border-signal hover:text-signal"
      >
        <Plus className="h-3 w-3" /> Añadir
      </button>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

type CalculatorProps = { projectId?: string };

export function Calculator({ projectId = "1" }: CalculatorProps = {}): JSX.Element {
  const [catalogoRigido, setCatalogoRigido] = useState<CatalogoMaterial[]>(FALLBACK_RIGID);
  const [catalogoRelleno, setCatalogoRelleno] = useState<CatalogoMaterial[]>(FALLBACK_FILLING);
  const [capa1, setCapa1] = useState<PanelLayer[]>([]);
  const [capa2, setCapa2] = useState<PanelLayer[]>([]);
  const [union, setUnion] = useState<UnionConfig>({
    rellenoNombre: null,
    rellenoEspesorMm: 50,
    camaraAireMm: 0,
    tipoMontantes: "montantes_metal",
  });
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load catalogs
  const cargarCatalogos = useCallback(async (): Promise<void> => {
    try {
      const [resR, resF] = await Promise.all([
        fetch(apiUrl("/api/materiales/?categoria=rigid")),
        fetch(apiUrl("/api/materiales/?categoria=filling")),
      ]);
      if (resR.ok) setCatalogoRigido(await resR.json() as CatalogoMaterial[]);
      if (resF.ok) setCatalogoRelleno(await resF.json() as CatalogoMaterial[]);
    } catch { /* fallback lists remain */ }
  }, []);

  useEffect(() => { void cargarCatalogos(); }, [cargarCatalogos]);

  // ── Capa helpers ─────────────────────────────────────────────────────────

  function buildDefaultLayer(cat: CatalogoMaterial[]): PanelLayer {
    const m = cat[0] ?? FALLBACK_RIGID[0];
    return { nombre: m.nombre, densidad: m.densidad, tipo: m.tipo, espesorUnitarioMm: defaultEspesorMm(m.nombre), cantidad: 1 };
  }

  function layerFromMaterial(nombre: string, cat: CatalogoMaterial[]): PanelLayer {
    const m = cat.find((x) => x.nombre === nombre) ?? cat[0] ?? FALLBACK_RIGID[0];
    return { nombre: m.nombre, densidad: m.densidad, tipo: m.tipo, espesorUnitarioMm: defaultEspesorMm(m.nombre), cantidad: 1 };
  }

  function agregar(set: React.Dispatch<React.SetStateAction<PanelLayer[]>>, cat: CatalogoMaterial[]): void {
    set((prev) => { if (prev.length >= 6) return prev; return [...prev, buildDefaultLayer(cat)]; });
    setResultado(null);
  }

  function eliminar(set: React.Dispatch<React.SetStateAction<PanelLayer[]>>, i: number): void {
    set((prev) => prev.filter((_, idx) => idx !== i));
    setResultado(null);
  }

  function cambiarMaterial(set: React.Dispatch<React.SetStateAction<PanelLayer[]>>, i: number, nombre: string, cat: CatalogoMaterial[]): void {
    set((prev) => prev.map((c, idx) => idx === i ? layerFromMaterial(nombre, cat) : c));
    setResultado(null);
  }

  function cambiarEspesor(set: React.Dispatch<React.SetStateAction<PanelLayer[]>>, i: number, mm: number): void {
    set((prev) => prev.map((c, idx) => idx === i ? { ...c, espesorUnitarioMm: Math.max(1, mm) } : c));
    setResultado(null);
  }

  function cambiarCantidad(set: React.Dispatch<React.SetStateAction<PanelLayer[]>>, i: number, qty: number): void {
    set((prev) => prev.map((c, idx) => idx === i ? { ...c, cantidad: Math.max(1, qty) } : c));
    setResultado(null);
  }

  // ── Chart / table data ───────────────────────────────────────────────────

  const chartData = useMemo(() => {
    if (!resultado) return [];
    return Object.entries(resultado.R_frecuencias)
      .map(([f, v]) => ({ frecuencia: Number(f), valor: Number(v) }))
      .sort((a, b) => a.frecuencia - b.frecuencia);
  }, [resultado]);

  // ── Calculation ───────────────────────────────────────────────────────────

  async function calcular(): Promise<void> {
    if (capa1.length === 0 && capa2.length === 0) return;
    setCargando(true);
    setError(null);
    try {
      const body = {
        proyecto_id: Number(projectId) || 1,
        nombre: "Calculo estructurado",
        capa1: capa1.map((c) => ({ nombre: c.nombre, cantidad: c.cantidad, espesor_unitario_mm: c.espesorUnitarioMm })),
        union: {
          relleno_nombre: union.rellenoNombre || null,
          relleno_espesor_mm: union.rellenoNombre ? union.rellenoEspesorMm : null,
          camara_aire_mm: union.camaraAireMm,
          tipo_montantes: union.tipoMontantes,
        },
        capa2: capa2.map((c) => ({ nombre: c.nombre, cantidad: c.cantidad, espesor_unitario_mm: c.espesorUnitarioMm })),
      };
      const res = await fetch(apiUrl("/api/calculations/structured/"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
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

  const puedeCalcular = (capa1.length > 0 || capa2.length > 0) && !cargando;

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-[340px_1fr_1fr]">

        {/* ── Columna izquierda: Configurador ── */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4">
          <div>
            <h2 className="text-sm font-semibold text-ink">Configurador de Tabique</h2>
            <p className="mt-0.5 text-xs text-slate-400">Define capas rígidas y unión entre ellas.</p>
          </div>

          {/* Capa 1 */}
          <CapaSection
            title="Capa 1"
            accent="border-slate-300"
            capas={capa1}
            catalogo={catalogoRigido}
            onAgregar={() => agregar(setCapa1, catalogoRigido)}
            onEliminar={(i) => eliminar(setCapa1, i)}
            onCambiarMaterial={(i, n) => cambiarMaterial(setCapa1, i, n, catalogoRigido)}
            onCambiarEspesor={(i, mm) => cambiarEspesor(setCapa1, i, mm)}
            onCambiarCantidad={(i, q) => cambiarCantidad(setCapa1, i, q)}
          />

          {/* Unión */}
          <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 space-y-2">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              Unión entre capas
            </p>

            {/* Relleno selector */}
            <div>
              <p className="mb-0.5 text-[9px] text-slate-400">RELLENO</p>
              <select
                value={union.rellenoNombre ?? ""}
                onChange={(e) => { setUnion((u) => ({ ...u, rellenoNombre: e.target.value || null })); setResultado(null); }}
                className="h-8 w-full rounded border border-slate-300 bg-white px-1.5 text-[10px] text-ink focus:border-signal focus:outline-none"
              >
                <option value="">Sin relleno (cámara de aire)</option>
                {catalogoRelleno.map((m) => (
                  <option key={m.nombre} value={m.nombre}>{m.nombre}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {union.rellenoNombre && (
                <div>
                  <p className="mb-0.5 text-[9px] text-slate-400">ESP. RELLENO (mm)</p>
                  <input
                    type="number" min={10} max={500} step={5}
                    value={union.rellenoEspesorMm}
                    onChange={(e) => { setUnion((u) => ({ ...u, rellenoEspesorMm: parseInt(e.target.value) || 50 })); setResultado(null); }}
                    className="h-8 w-full rounded border border-slate-300 bg-white px-2 text-center text-[10px] text-ink focus:border-signal focus:outline-none"
                  />
                </div>
              )}
              <div>
                <p className="mb-0.5 text-[9px] text-slate-400">CÁMARA AIRE (mm)</p>
                <input
                  type="number" min={0} max={500} step={5}
                  value={union.camaraAireMm}
                  onChange={(e) => { setUnion((u) => ({ ...u, camaraAireMm: parseInt(e.target.value) || 0 })); setResultado(null); }}
                  className="h-8 w-full rounded border border-slate-300 bg-white px-2 text-center text-[10px] text-ink focus:border-signal focus:outline-none"
                />
              </div>
            </div>

            {/* Tipo montantes */}
            <div>
              <p className="mb-0.5 text-[9px] text-slate-400">MONTANTES</p>
              <select
                value={union.tipoMontantes}
                onChange={(e) => { setUnion((u) => ({ ...u, tipoMontantes: e.target.value })); setResultado(null); }}
                className="h-8 w-full rounded border border-slate-300 bg-white px-1.5 text-[10px] text-ink focus:border-signal focus:outline-none"
              >
                {OPCIONES_MONTANTES.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Capa 2 */}
          <CapaSection
            title="Capa 2"
            accent="border-slate-300"
            capas={capa2}
            catalogo={catalogoRigido}
            onAgregar={() => agregar(setCapa2, catalogoRigido)}
            onEliminar={(i) => eliminar(setCapa2, i)}
            onCambiarMaterial={(i, n) => cambiarMaterial(setCapa2, i, n, catalogoRigido)}
            onCambiarEspesor={(i, mm) => cambiarEspesor(setCapa2, i, mm)}
            onCambiarCantidad={(i, q) => cambiarCantidad(setCapa2, i, q)}
          />

          {error && (
            <p className="rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>
          )}

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
            <EsquemaTabique capa1={capa1} union={union} capa2={capa2} />
          </div>
        </div>

        {/* ── Columna derecha: Gráfico + tabla + métricas ── */}
        <div className="flex flex-col gap-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-2 text-sm font-semibold text-ink">Aislamiento Acústico R</h2>
            <GraficoR data={chartData} />
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Espectro R(f) — tercios de octava
            </h2>
            <TablaResultados data={chartData} />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <MetricaCard label="Rw"  value={resultado?.Rw  ?? null} />
            <MetricaCard label="C"   value={resultado?.C   ?? null} />
            <MetricaCard label="Ctr" value={resultado?.Ctr ?? null} />
          </div>
        </div>

      </div>
    </form>
  );
}
