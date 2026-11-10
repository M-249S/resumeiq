import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { Card } from "@/components/ui/Card";

interface CollapsibleCardProps {
  title: string;
  /** Small count shown next to the title, e.g. number of items. */
  count?: number;
  defaultOpen?: boolean;
  children: ReactNode;
}

/**
 * A card whose body can be folded away. Built on <details>, so it is
 * keyboard-operable and announced correctly by screen readers for free.
 */
export function CollapsibleCard({
  title,
  count,
  defaultOpen = true,
  children,
}: CollapsibleCardProps) {
  return (
    <Card>
      <details className="group" open={defaultOpen}>
        <summary className="flex cursor-pointer list-none items-center justify-between gap-3 rounded-card p-6 [&::-webkit-details-marker]:hidden">
          <h3 className="flex items-center gap-2 font-medium text-ink">
            {title}
            {count !== undefined && (
              <span className="rounded-full bg-paper px-2 py-0.5 text-xs font-normal text-ink-faint">
                {count}
              </span>
            )}
          </h3>
          <ChevronDown
            className="h-4 w-4 text-ink-faint transition-transform group-open:rotate-180 motion-reduce:transition-none"
            aria-hidden="true"
          />
        </summary>
        <div className="px-6 pb-6">{children}</div>
      </details>
    </Card>
  );
}
