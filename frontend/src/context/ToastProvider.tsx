import { useCallback, useMemo, useRef, useState, type ReactNode } from "react";
import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";
import { ToastContext, type ToastVariant } from "@/context/ToastContext";
import { cn } from "@/lib/cn";

interface ToastItem {
  id: number;
  message: string;
  variant: ToastVariant;
}

const DISMISS_AFTER_MS = 6000;
const MAX_VISIBLE = 3;

const variantStyles: Record<ToastVariant, { border: string; icon: ReactNode }> = {
  error: {
    border: "border-l-danger",
    icon: <AlertCircle className="h-5 w-5 shrink-0 text-danger" aria-hidden />,
  },
  success: {
    border: "border-l-success",
    icon: <CheckCircle2 className="h-5 w-5 shrink-0 text-success" aria-hidden />,
  },
  info: {
    border: "border-l-accent",
    icon: <Info className="h-5 w-5 shrink-0 text-accent" aria-hidden />,
  },
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const nextId = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const show = useCallback(
    (message: string, variant: ToastVariant = "error") => {
      const id = nextId.current++;
      setToasts((current) => [...current.slice(-(MAX_VISIBLE - 1)), { id, message, variant }]);
      window.setTimeout(() => dismiss(id), DISMISS_AFTER_MS);
    },
    [dismiss],
  );

  const value = useMemo(() => ({ show }), [show]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-4 bottom-4 z-50 flex flex-col gap-2 sm:left-auto sm:right-4 sm:w-96">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role={toast.variant === "error" ? "alert" : "status"}
            className={cn(
              "pointer-events-auto flex items-start gap-3 rounded-md border border-border border-l-4 bg-paper-raised px-4 py-3 text-sm text-ink shadow-[0_8px_24px_rgba(20,33,61,0.12)]",
              variantStyles[toast.variant].border,
            )}
          >
            {variantStyles[toast.variant].icon}
            <p className="flex-1">{toast.message}</p>
            <button
              type="button"
              onClick={() => dismiss(toast.id)}
              aria-label="Dismiss notification"
              className="text-ink-faint hover:text-ink"
            >
              <X className="h-4 w-4" aria-hidden />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
