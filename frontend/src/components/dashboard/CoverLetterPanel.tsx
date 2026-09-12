import { useState } from "react";
import { Mail, Download } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  generateCoverLetter,
  downloadCoverLetterDocx,
  saveBlobAsFile,
} from "@/services/resume";

interface CoverLetterPanelProps {
  file: File;
  jobDescription: string;
  onError: (message: string) => void;
}

export function CoverLetterPanel({
  file,
  jobDescription,
  onError,
}: CoverLetterPanelProps) {
  const [letter, setLetter] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState(false);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const text = await generateCoverLetter(file, jobDescription);
      setLetter(text);
    } catch {
      onError("Couldn't generate a cover letter right now. Please try again.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleDownload() {
    setDownloading(true);
    try {
      const blob = await downloadCoverLetterDocx(file, jobDescription);
      saveBlobAsFile(blob, "cover-letter.docx");
    } catch {
      onError("Couldn't download the cover letter. Please try again.");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <Card className="p-6 sm:p-8">
      <div className="mb-4 flex items-center gap-2">
        <Mail className="h-5 w-5 text-accent" />
        <h3 className="font-medium text-ink">Cover letter</h3>
      </div>

      {letter ? (
        <div className="space-y-4">
          <textarea
            value={letter}
            onChange={(e) => setLetter(e.target.value)}
            rows={12}
            className="w-full rounded-md border border-border-strong bg-paper px-3.5 py-2.5 text-sm leading-relaxed text-ink focus:border-ink focus:outline-none focus:ring-2 focus:ring-accent/20"
          />
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={handleGenerate}
              loading={generating}
            >
              Regenerate
            </Button>
            <Button
              onClick={handleDownload}
              loading={downloading}
              icon={<Download className="h-4 w-4" />}
            >
              Download .docx
            </Button>
          </div>
        </div>
      ) : (
        <div>
          <p className="mb-4 text-sm text-ink-muted">
            Generate a cover letter based on this resume
            {jobDescription ? " and the job description above" : ""}.
          </p>
          <Button onClick={handleGenerate} loading={generating}>
            Generate cover letter
          </Button>
        </div>
      )}
    </Card>
  );
}
