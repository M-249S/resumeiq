import { Link } from "react-router-dom";
import { Check } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

const BENEFITS = [
  "Download your improved resume as a PDF",
  "Generate and edit a matching cover letter",
  "Keep a history of every analysis",
];

/** Shown to guests after their demo analysis: the natural next step. */
export function SignupPrompt() {
  return (
    <Card className="p-6 sm:p-8">
      <h2 className="font-display text-xl font-medium text-ink">
        Want to do more with this resume?
      </h2>
      <p className="mt-1 text-ink-muted">
        This was a one-off preview and nothing was saved. A free account adds:
      </p>
      <ul className="mt-4 space-y-2">
        {BENEFITS.map((benefit) => (
          <li key={benefit} className="flex items-start gap-2 text-sm text-ink">
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" aria-hidden />
            {benefit}
          </li>
        ))}
      </ul>
      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <Link to="/signup">
          <Button className="w-full sm:w-auto">Create a free account</Button>
        </Link>
        <Link to="/login">
          <Button variant="secondary" className="w-full sm:w-auto">
            I already have an account
          </Button>
        </Link>
      </div>
    </Card>
  );
}
