type ChartProps = {
  values: number[];
};

export function Chart({ values }: ChartProps): JSX.Element {
  const max = Math.max(...values, 1);

  return (
    <div className="flex h-48 items-end gap-3 rounded border border-slate-200 bg-white p-4">
      {values.map((value, index) => (
        <div
          // Example: replace this placeholder with a charting library when results are final.
          key={`${value}-${index}`}
          className="flex-1 rounded-t bg-signal"
          style={{ height: `${(value / max) * 100}%` }}
          title={`${value} dB`}
        />
      ))}
    </div>
  );
}
