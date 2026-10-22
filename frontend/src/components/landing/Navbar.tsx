import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

const links = [
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Pricing", href: "#pricing" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();

  // The Features/How it works/Pricing anchors only exist on the landing
  // page itself. Once logged in (e.g. viewing this Navbar from
  // /dashboard), they'd just be dead links, so they're hidden rather
  // than shown broken.
  const navLinks = isAuthenticated ? [] : links;

  function handleLogout() {
    setOpen(false);
    logout();
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-paper/90 backdrop-saturate-150 supports-[backdrop-filter]:backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to={isAuthenticated ? "/dashboard" : "/"}>
          <Logo />
        </Link>

        {navLinks.length > 0 && (
          <nav className="hidden items-center gap-8 md:flex">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-ink-muted transition-colors hover:text-ink"
              >
                {link.label}
              </a>
            ))}
          </nav>
        )}

        {isAuthenticated && (
          <nav className="hidden items-center gap-8 md:flex">
            <Link
              to="/history"
              className="text-sm text-ink-muted transition-colors hover:text-ink"
            >
              History
            </Link>
          </nav>
        )}

        <div className="hidden items-center gap-3 md:flex">
          {isAuthenticated ? (
            <>
              {user && (
                <span className="text-sm text-ink-faint">{user.full_name}</span>
              )}
              <Button variant="ghost" size="sm" onClick={logout}>
                Log out
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="sm">
                  Log in
                </Button>
              </Link>
              <Link to="/signup">
                <Button size="sm">Get started</Button>
              </Link>
            </>
          )}
        </div>

        <button
          type="button"
          aria-label="Toggle menu"
          className="text-ink md:hidden"
          onClick={() => setOpen((prev) => !prev)}
        >
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-border bg-paper px-6 py-4 md:hidden">
          <nav className="flex flex-col gap-4">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-ink-muted"
                onClick={() => setOpen(false)}
              >
                {link.label}
              </a>
            ))}

            {isAuthenticated ? (
              <div className="mt-2 flex flex-col gap-4">
                <Link
                  to="/history"
                  className="text-sm text-ink-muted"
                  onClick={() => setOpen(false)}
                >
                  History
                </Link>
                {user && (
                  <span className="text-sm text-ink-faint">{user.full_name}</span>
                )}
                <Button variant="secondary" className="w-full" onClick={handleLogout}>
                  Log out
                </Button>
              </div>
            ) : (
              <div className="mt-2 flex flex-col gap-2">
                <Link to="/login" onClick={() => setOpen(false)}>
                  <Button variant="secondary" className="w-full">
                    Log in
                  </Button>
                </Link>
                <Link to="/signup" onClick={() => setOpen(false)}>
                  <Button className="w-full">Get started</Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
