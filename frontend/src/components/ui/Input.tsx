import { forwardRef, useId, useState } from "react";
import type { InputHTMLAttributes } from "react";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/cn";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, id, className, type, ...props }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const isPassword = type === "password";
    const [visible, setVisible] = useState(false);

    return (
      <div>
        <label htmlFor={inputId} className="text-sm font-medium text-ink">
          {label}
        </label>
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            type={isPassword && visible ? "text" : type}
            aria-invalid={!!error}
            aria-describedby={error ? `${inputId}-error` : undefined}
            className={cn(
              "mt-1.5 block w-full rounded-md border border-border-strong bg-paper-raised px-3 py-2 text-sm text-ink placeholder:text-ink-faint",
              "focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent",
              error && "border-danger focus:ring-danger/30 focus:border-danger",
              isPassword && "pr-10",
              className,
            )}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setVisible((v) => !v)}
              aria-label={visible ? "Hide password" : "Show password"}
              aria-pressed={visible}
              className="absolute right-2 top-[0.375rem] flex h-8 w-8 items-center justify-center rounded text-ink-muted hover:text-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
            >
              {visible ? <EyeOff size={18} aria-hidden /> : <Eye size={18} aria-hidden />}
            </button>
          )}
        </div>
        {error && (
          <p id={`${inputId}-error`} className="mt-1.5 text-sm text-danger">
            {error}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = "Input";
