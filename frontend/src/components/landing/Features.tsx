import { ScanSearch, PenLine, Mail, FileDown } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/Card";

interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

const features: Feature[] = [
  {
    icon: ScanSearch,
    title: "ATS match analysis",
    description:
      "See your match score against a specific job description, with a keyword-by-keyword breakdown of what's missing.",
  },
  {
    icon: PenLine,
    title: "Line-by-line rewrites",
    description:
      "Weak, passive bullet points get rewritten into specific, achievement-driven language you can accept or edit.",
  },
  {
    icon: Mail,
    title: "Matching cover letters",
    description:
      "Generate a cover letter that actually reflects your resume and the role — not a generic template.",
  },
  {
    icon: FileDown,
    title: "Clean exports",
    description:
      "Download a polished PDF or DOCX in an ATS-safe format, ready to submit.",
  },
];

export function Features() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-6 py-20 md:py-28">
      <div className="mb-14 max-w-xl">
        <h2 className="font-display text-3xl font-medium text-ink md:text-4xl">
          Everything between "upload" and "interview"
        </h2>
        <p className="mt-3 text-ink-muted">
          One workflow, from a raw resume to an application you're confident
          in.
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {features.map(({ icon: Icon, title, description }) => (
          <Card key={title} className="p-6">
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-md bg-accent-soft">
              <Icon className="h-5 w-5 text-accent" />
            </div>
            <h3 className="font-medium text-ink">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">
              {description}
            </p>
          </Card>
        ))}
      </div>
    </section>
  );
}
