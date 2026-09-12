import { cn } from "@/lib/cn";

interface LogoProps {
  className?: string;
}

export function Logo({ className }: LogoProps) {
  return (
    <span className={cn("font-display text-xl font-semibold tracking-tight text-ink", className)}>
      Resume<span className="text-accent">IQ</span>
    </span>
  );
}
