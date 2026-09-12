import { UploadCloud, Wand2, FileDown } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface Step {
  icon: LucideIcon;
  title: string;
  description: string;
}

const steps: Step[] = [
  {
    icon: UploadCloud,
    title: "Upload",
    description: "Drop in your resume and the job description you're targeting.",
  },
  {
    icon: Wand2,
    title: "Analyze & rewrite",
    description: "ResumeIQ scores your match and rewrites the weakest sections.",
  },
  {
    icon: FileDown,
    title: "Export",
    description: "Download a polished, ATS-ready resume and cover letter.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="border-t border-border bg-paper-raised">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
        <h2 className="font-display text-3xl font-medium text-ink md:text-4xl">
          How it works
        </h2>

        <div className="mt-12 grid gap-10 sm:grid-cols-3">
          {steps.map(({ icon: Icon, title, description }, index) => (
            <div key={title} className="relative">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border-strong">
                  <Icon className="h-4 w-4 text-ink" />
                </div>
                <span className="font-display text-sm text-ink-faint">
                  0{index + 1}
                </span>
              </div>
              <h3 className="font-medium text-ink">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-muted">
                {description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
