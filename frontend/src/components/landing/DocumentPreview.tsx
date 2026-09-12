import { ArrowRight, Check } from "lucide-react";
import { Card } from "@/components/ui/Card";

/**
 * A stylized resume-document mockup used as the hero visual. Deliberately
 * built from real product mechanics (a before/after rewrite, a match
 * score) instead of an abstract gradient shape — the visual should look
 * like the product, not like decoration.
 */
export function DocumentPreview() {
  return (
    <Card className="relative w-full max-w-md p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="h-2.5 w-32 rounded-full bg-ink/80" />
          <div className="mt-2 h-2 w-24 rounded-full bg-ink-faint/60" />
        </div>
        <div className="flex flex-col items-center rounded-md border border-accent-soft bg-accent-soft px-3 py-1.5">
          <span className="font-display text-lg font-semibold text-accent">92</span>
          <span className="text-[10px] text-accent/80">match</span>
        </div>
      </div>

      <div className="space-y-2.5">
        <div className="h-2 w-full rounded-full bg-ink-faint/30" />
        <div className="h-2 w-5/6 rounded-full bg-ink-faint/30" />
        <div className="h-2 w-full rounded-full bg-ink-faint/30" />
      </div>

      <div className="my-6 border-t border-dashed border-border" />

      <div className="space-y-3">
        <p className="text-xs font-medium text-ink-faint">Before</p>
        <p className="rounded-md bg-[#faf1f1] px-3 py-2 text-sm text-ink-muted line-through decoration-danger/40">
          Responsible for managing a small team
        </p>

        <div className="flex justify-center text-ink-faint">
          <ArrowRight className="h-4 w-4" />
        </div>

        <p className="text-xs font-medium text-ink-faint">After</p>
        <p className="rounded-md bg-accent-soft px-3 py-2 text-sm text-ink">
          Led a 6-person team, cutting delivery time 30%
        </p>
      </div>

      <div className="mt-6 flex items-center gap-2 text-sm text-ink-muted">
        <Check className="h-4 w-4 text-success" />
        11 of 13 keywords matched
      </div>
    </Card>
  );
}
