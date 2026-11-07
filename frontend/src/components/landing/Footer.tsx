import { Link } from "react-router-dom";
import { Logo } from "@/components/ui/Logo";

const linkClass = "text-sm text-ink-muted transition-colors hover:text-ink";

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 md:flex-row">
        <Logo className="text-base" />

        <nav aria-label="Footer" className="flex items-center gap-6">
          <Link to="/privacy" className={linkClass}>
            Privacy
          </Link>
          <Link to="/terms" className={linkClass}>
            Terms
          </Link>
          <a
            href="https://github.com/M-249S/resumeiq"
            target="_blank"
            rel="noopener noreferrer"
            className={linkClass}
          >
            GitHub
          </a>
        </nav>

        <p className="text-sm text-ink-faint">
          Built by Mujahid Adam &middot; {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}
