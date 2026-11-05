import { cn } from "@/lib/cn";

const LEVELS = [
  { label: "Too short", bar: "bg-danger", text: "text-danger" },
  { label: "Weak", bar: "bg-danger", text: "text-danger" },
  { label: "Fair", bar: "bg-warning", text: "text-warning" },
  { label: "Good", bar: "bg-success", text: "text-success" },
  { label: "Strong", bar: "bg-success", text: "text-success" },
] as const;

/** 0 = too short, 1-4 = weak..strong. Simple heuristic, not a security check. */
function scorePassword(password: string, minLength = 8): number {
  if (password.length < minLength) return 0;
  let score = 1;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password) && /[^A-Za-z0-9]/.test(password)) score++;
  return Math.min(score, 4);
}

export function PasswordStrength({ password }: { password: string }) {
  if (!password) return null;
  const score = scorePassword(password);
  const level = LEVELS[score];

  return (
    <div className="-mt-2" aria-live="polite">
      <div className="flex gap-1" aria-hidden>
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={cn(
              "h-1.5 flex-1 rounded-full bg-border transition-colors",
              i <= score && level.bar,
            )}
          />
        ))}
      </div>
      <p className={cn("mt-1 text-xs", level.text)}>Password strength: {level.label}</p>
    </div>
  );
}
