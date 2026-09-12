import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { DocumentPreview } from "@/components/landing/DocumentPreview";

export function Hero() {
  return (
    <section className="mx-auto max-w-6xl px-6 pb-20 pt-16 md:pb-28 md:pt-24">
      <div className="grid items-center gap-16 md:grid-cols-2">
        <div>
          <div className="mb-6 inline-flex items-center gap-2 text-sm text-ink-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            AI resume analysis, without the guesswork
          </div>

          <h1 className="font-display text-4xl leading-[1.15] font-medium text-ink md:text-5xl lg:text-6xl">
            Every resume has a weaker line.{" "}
            <span className="text-accent">We find it.</span>
          </h1>

          <p className="mt-6 max-w-md text-lg leading-relaxed text-ink-muted">
            Upload your resume and a job description. ResumeIQ scores your
            match, rewrites the lines holding you back, and exports a
            recruiter-ready file — in minutes, not hours.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link to="/signup">
              <Button size="lg" icon={<ArrowRight className="h-4 w-4" />} className="w-full sm:w-auto">
                Analyze your resume
              </Button>
            </Link>
            <a href="#how-it-works">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                See how it works
              </Button>
            </a>
          </div>

          <p className="mt-4 text-sm text-ink-faint">
            Free to start. No credit card required.
          </p>
        </div>

        <div className="flex justify-center md:justify-end">
          <DocumentPreview />
        </div>
      </div>
    </section>
  );
}
