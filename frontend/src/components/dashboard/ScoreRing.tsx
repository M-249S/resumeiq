import { useEffect, useState } from "react";
import { cn } from "@/lib/cn";

interface ScoreRingProps {
  value: number;
  label: string;
  /** Diameter in px. */
  size?: number;
  className?: string;
}

function tone(value: number): string {
  if (value >= 60) return "text-accent";
  if (value >= 40) return "text-warning";
  return "text-danger";
}

/**
 * Circular score gauge. The arc fills in once on mount; users who prefer
 * reduced motion get the final state immediately.
 */
export function ScoreRing({ value, label, size = 132, className }: ScoreRingProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(value)));
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;

  const [filled, setFilled] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setFilled(true));
    return () => cancelAnimationFrame(id);
  }, []);

  const offset = circumference * (1 - (filled ? clamped : 0) / 100);

  return (
    <div
      role="img"
      aria-label={`${label}: ${clamped} out of 100`}
      className={cn("relative shrink-0", tone(clamped), className)}
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={stroke}
          className="stroke-border"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          stroke="currentColor"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          className="transition-[stroke-dashoffset] duration-1000 ease-out motion-reduce:transition-none"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-3xl font-semibold leading-none text-ink">
          {clamped}
        </span>
        <span className="mt-1 text-xs text-ink-faint">{label}</span>
      </div>
    </div>
  );
}
