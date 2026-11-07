import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";

/** Decorative placeholder block. Hidden from screen readers on purpose. */
export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      aria-hidden
      className={cn("rounded-md bg-accent-soft motion-safe:animate-pulse", className)}
      {...props}
    />
  );
}
