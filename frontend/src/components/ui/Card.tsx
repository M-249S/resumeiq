import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-card border border-border bg-paper-raised shadow-[0_1px_2px_rgba(20,33,61,0.04),0_8px_24px_rgba(20,33,61,0.06)]",
        className,
      )}
      {...props}
    />
  );
}
