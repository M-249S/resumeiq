import type { ReactNode } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

interface LegalLayoutProps {
  title: string;
  updated: string;
  children: ReactNode;
}

export function LegalLayout({ title, updated, children }: LegalLayoutProps) {
  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="font-display text-3xl font-medium text-ink">{title}</h1>
        <p className="mt-2 text-sm text-ink-faint">Last updated: {updated}</p>
        <div className="mt-10 space-y-8">{children}</div>
      </main>
      <Footer />
    </div>
  );
}

export function LegalSection({
  heading,
  children,
}: {
  heading: string;
  children: ReactNode;
}) {
  return (
    <section>
      <h2 className="font-display text-xl font-medium text-ink">{heading}</h2>
      <div className="mt-3 space-y-3 leading-relaxed text-ink-muted">{children}</div>
    </section>
  );
}
