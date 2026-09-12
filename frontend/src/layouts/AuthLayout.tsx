import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Logo } from "@/components/ui/Logo";
import { Card } from "@/components/ui/Card";

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}

export function AuthLayout({ title, subtitle, children, footer }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-paper px-6 py-12">
      <Link to="/" className="mb-8">
        <Logo />
      </Link>

      <Card className="w-full max-w-sm p-8">
        <h1 className="font-display text-2xl font-medium text-ink">{title}</h1>
        <p className="mt-1 text-sm text-ink-muted">{subtitle}</p>

        <div className="mt-6">{children}</div>
      </Card>

      <p className="mt-6 text-sm text-ink-muted">{footer}</p>
    </div>
  );
}
