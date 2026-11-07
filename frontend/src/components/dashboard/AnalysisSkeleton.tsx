import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";

const STEPS = [
  "Reading your resume…",
  "Scoring it against the job…",
  "Writing suggestions…",
];
const SECONDS_PER_STEP = 5;
const SLOW_AFTER_SECONDS = 12;

/**
 * Placeholder shown while an analysis request is in flight. The status line
 * advances on a timer; it is reassurance, not real progress, so it never
 * claims a percentage. After a while it explains that the free-tier server
 * may be waking up.
 */
export function AnalysisSkeleton() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => window.clearInterval(id);
  }, []);

  const step = Math.min(Math.floor(seconds / SECONDS_PER_STEP), STEPS.length - 1);

  return (
    <div className="space-y-6" aria-busy="true">
      <div role="status" aria-live="polite" className="text-sm text-ink-muted">
        <p className="font-medium text-ink">{STEPS[step]}</p>
        {seconds >= SLOW_AFTER_SECONDS && (
          <p className="mt-1">
            Still working. The server may be waking up after a quiet period, which
            can take up to a minute.
          </p>
        )}
      </div>

      <Card className="p-6 sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex-1 space-y-3">
            <Skeleton className="h-6 w-20 rounded-full" />
            <Skeleton className="h-4 w-full max-w-xl" />
            <Skeleton className="h-4 w-4/5 max-w-lg" />
          </div>
          <div className="flex gap-4">
            <Skeleton className="h-16 w-24" />
            <Skeleton className="h-16 w-24" />
          </div>
        </div>
        <div className="mt-8 grid gap-x-8 gap-y-5 sm:grid-cols-2">
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-1.5 w-full" />
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-6 sm:grid-cols-2">
        {[0, 1].map((i) => (
          <Card key={i} className="space-y-3 p-6">
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-5/6" />
            <Skeleton className="h-3 w-4/6" />
          </Card>
        ))}
      </div>
    </div>
  );
}
