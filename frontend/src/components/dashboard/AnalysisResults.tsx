import { Check, X, Download } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ScoreBar } from "@/components/dashboard/ScoreBar";
import { ScoreRing } from "@/components/dashboard/ScoreRing";
import { CollapsibleCard } from "@/components/dashboard/CollapsibleCard";
import type { ResumeAnalysis } from "@/types/resume";

interface AnalysisResultsProps {
  analysis: ResumeAnalysis;
  // Omitted when viewing a past analysis from history, where the
  // original uploaded file (needed to regenerate the improved PDF)
  // is no longer available — only the stored analysis is.
  onDownload?: () => void;
  downloading?: boolean;
}

/**
 * Without a job description the model reports a 0 match and an "N/A" level.
 * Showing "0/100" would read as a bad result rather than "not measured".
 */
function isMissingJobDescription(analysis: ResumeAnalysis): boolean {
  return (
    analysis.match_score === 0 &&
    /n\/a|no job description/i.test(`${analysis.ats_level} ${analysis.summary}`)
  );
}

export function AnalysisResults({
  analysis,
  onDownload,
  downloading = false,
}: AnalysisResultsProps) {
  const subScores: Array<[string, number]> = [
    ["Formatting", analysis.formatting_score],
    ["Keywords", analysis.keyword_score],
    ["Experience", analysis.experience_score],
    ["Skills", analysis.skills_score],
    ["Education", analysis.education_score],
    ["Readability", analysis.readability_score],
  ];

  const hasJobMatch = !isMissingJobDescription(analysis);

  return (
    <div className="space-y-6">
      <Card className="p-6 sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
          <div className="flex items-center gap-4">
            <ScoreRing value={analysis.score} label="overall" />
            {hasJobMatch && (
              <ScoreRing value={analysis.match_score} label="job match" size={96} />
            )}
          </div>

          <div className="min-w-0">
            <Badge variant={hasJobMatch ? "accent" : "neutral"}>
              {hasJobMatch ? analysis.ats_level : "No job description"}
            </Badge>
            <p className="mt-3 max-w-xl text-ink-muted">{analysis.summary}</p>
            {!hasJobMatch && (
              <p className="mt-2 text-sm text-ink-faint">
                Add a job description to see how well this resume matches a role.
              </p>
            )}
          </div>
        </div>

        <div className="mt-8 grid gap-x-8 gap-y-5 sm:grid-cols-2">
          {subScores.map(([label, value]) => (
            <ScoreBar key={label} label={label} value={value} />
          ))}
        </div>
      </Card>

      <div className="grid items-start gap-6 sm:grid-cols-2">
        <CollapsibleCard title="Strengths" count={analysis.strengths.length}>
          <ul className="space-y-2">
            {analysis.strengths.map((item) => (
              <li key={item} className="flex gap-2 text-sm text-ink-muted">
                <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                {item}
              </li>
            ))}
          </ul>
        </CollapsibleCard>

        <CollapsibleCard title="Weaknesses" count={analysis.weaknesses.length}>
          <ul className="space-y-2">
            {analysis.weaknesses.map((item) => (
              <li key={item} className="flex gap-2 text-sm text-ink-muted">
                <X className="mt-0.5 h-4 w-4 shrink-0 text-danger" />
                {item}
              </li>
            ))}
          </ul>
        </CollapsibleCard>
      </div>

      {(analysis.matching_skills.length > 0 || analysis.missing_skills.length > 0) && (
        <CollapsibleCard
          title="Keyword match"
          count={analysis.matching_skills.length + analysis.missing_skills.length}
        >
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
        </CollapsibleCard>
      )}

      <CollapsibleCard title="Suggestions" count={analysis.suggestions.length}>
        <ul className="list-disc space-y-1.5 pl-5 text-sm text-ink-muted">
          {analysis.suggestions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </CollapsibleCard>

      {onDownload && (
        <Button
          onClick={onDownload}
          loading={downloading}
          icon={<Download className="h-4 w-4" />}
        >
          Download improved resume
        </Button>
      )}
    </div>
  );
}
