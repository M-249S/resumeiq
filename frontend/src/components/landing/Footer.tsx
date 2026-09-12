import { Logo } from "@/components/ui/Logo";

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 sm:flex-row">
        <Logo className="text-base" />
        <p className="text-sm text-ink-faint">
          Built by Mujahid Elgazooly &middot; {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}
