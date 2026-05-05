type ResultsDisplayProps = {
  projectId: string;
  weightedIndex: number;
};

export function ResultsDisplay({ projectId, weightedIndex }: ResultsDisplayProps): JSX.Element {
  return (
    <div className="rounded border border-slate-200 bg-surface p-4">
      <p className="text-sm text-slate-600">Proyecto {projectId}</p>
      <p className="mt-1 text-3xl font-semibold text-ink">{weightedIndex} dB</p>
    </div>
  );
}
