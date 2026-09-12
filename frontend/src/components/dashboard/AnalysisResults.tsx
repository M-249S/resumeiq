import { Check, X, Download } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ScoreBar } from "@/components/dashboard/ScoreBar";
import type { ResumeAnalysis } from "@/types/resume";

interface AnalysisResultsProps {
  analysis: ResumeAnalysis;
  onDownload: () => void;
  downloading: boolean;
}

export function AnalysisResults({
  analysis,
  onDownload,
  downloading,
}: AnalysisResultsProps) {
  const subScores: Array<[string, number]> = [
    ["Formatting", analysis.formatting_score],
    ["Keywords", analysis.keyword_score],
    ["Experience", analysis.experience_score],
    ["Skills", analysis.skills_score],
    ["Education", analysis.education_score],
    ["Readability", analysis.readability_score],
  ];

  return (
    <div className="space-y-6">
      <Card className="p-6 sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Badge variant="accent">{analysis.ats_level}</Badge>
            <p className="mt-3 max-w-xl text-ink-muted">{analysis.summary}</p>
          </div>

          <div className="flex gap-4">
            <div className="flex flex-col items-center rounded-md border border-accent-soft bg-accent-soft px-5 py-3">
              <span className="font-display text-2xl font-semibold text-accent">
                {analysis.score}
              </span>
              <span className="text-xs text-accent/80">overall</span>
            </div>
            <div className="flex flex-col items-center rounded-md border border-border px-5 py-3">
              <span className="font-display text-2xl font-semibold text-ink">
                {analysis.match_score}
              </span>
              <span className="text-xs text-ink-faint">job match</span>
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-x-8 gap-y-5 sm:grid-cols-2">
          {subScores.map(([label, value]) => (
            <ScoreBar key={label} label={label} value={value} />
          ))}
        </div>
      </Card>

      <div className="grid gap-6 sm:grid-cols-2">
        <Card className="p-6">
          <h3 className="mb-3 font-medium text-ink">Strengths</h3>
          <ul className="space-y-2">
            {analysis.strengths.map((item) => (
              <li key={item} className="flex gap-2 text-sm text-ink-muted">
                <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                {item}
              </li>
            ))}
          </ul>
        </Card>

        <Card className="p-6">
          <h3 className="mb-3 font-medium text-ink">Weaknesses</h3>
          <ul className="space-y-2">
            {analysis.weaknesses.map((item) => (
              <li key={item} className="flex gap-2 text-sm text-ink-muted">
                <X className="mt-0.5 h-4 w-4 shrink-0 text-danger" />
                {item}
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="mb-3 font-medium text-ink">Keyword match</h3>
        <div className="flex flex-wrap gap-2">
          {analysis.matching_skills.map((skill) => (
            <Badge key={skill} variant="success">
              {skill}
            </Badge>
          ))}
          {analysis.missing_skills.map((skill) => (
            <Badge key={skill} variant="neutral" className="line-through opacity-60">
              {skill}
            </Badge>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-3 font-medium text-ink">Suggestions</h3>
        <ul className="list-disc space-y-1.5 pl-5 text-sm text-ink-muted">
          {analysis.suggestions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </Card>

      <Button
        onClick={onDownload}
        loading={downloading}
        icon={<Download className="h-4 w-4" />}
      >
        Download improved resume
      </Button>
    </div>
  );
}
