import { Card } from "@/components/ui/Card";
import type { ResumeHistoryItem } from "@/types/resume";

interface ScoreTrendProps {
  /** Analyses of one resume, oldest first. */
  series: ResumeHistoryItem[];
}

const W = 240;
const H = 56;
const PAD = 6;

/** Small line chart of the overall score across analyses of the same resume. */
export function ScoreTrend({ series }: ScoreTrendProps) {
  const first = series[0];
  const last = series[series.length - 1];
  const change = last.score - first.score;

  const points = series.map((item, i) => {
    const x = PAD + (i / (series.length - 1)) * (W - PAD * 2);
    const y = PAD + (1 - item.score / 100) * (H - PAD * 2);
    return { x, y };
  });
  const path = points.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");

  return (
    <Card className="mb-6 flex flex-wrap items-center justify-between gap-4 p-5">
      <div className="min-w-0">
        <p className="text-sm text-ink-faint">Your progress</p>
        <p className="truncate font-medium text-ink">{last.filename}</p>
        <p className="mt-1 text-sm text-ink-muted">
          {first.score} → {last.score} over {series.length} analyses
          {change !== 0 && (
            <span className={change > 0 ? "text-success" : "text-danger"}>
              {" "}
              ({change > 0 ? "+" : "−"}
              {Math.abs(change)})
            </span>
          )}
        </p>
      </div>
      <svg
        width={W}
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`Overall score went from ${first.score} to ${last.score} across ${series.length} analyses`}
        className="max-w-full text-accent"
      >
        <path d={path} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        {points.map((p, i) => (
          <circle key={series[i].id} cx={p.x} cy={p.y} r={3} fill="currentColor" />
        ))}
      </svg>
    </Card>
  );
}
