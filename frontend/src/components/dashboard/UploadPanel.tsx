import { useRef, useState, type FormEvent } from "react";
import { UploadCloud, FileText, X } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface UploadPanelProps {
  onSubmit: (file: File, jobDescription: string) => void;
  loading: boolean;
  error: string;
}

export function UploadPanel({ onSubmit, loading, error }: UploadPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [fileError, setFileError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(selected: File | null) {
    if (!selected) {
      setFile(null);
      return;
    }
    if (selected.type !== "application/pdf") {
      setFileError("Only PDF files are allowed.");
      setFile(null);
      return;
    }
    setFileError("");
    setFile(selected);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setFileError("Choose a resume PDF to continue.");
      return;
    }
    onSubmit(file, jobDescription);
  }

  return (
    <Card className="p-6 sm:p-8">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">
            Resume (PDF)
          </label>

          {file ? (
            <div className="flex items-center justify-between rounded-md border border-border-strong bg-paper px-4 py-3">
              <span className="flex items-center gap-2 text-sm text-ink">
                <FileText className="h-4 w-4 text-ink-faint" />
                {file.name}
              </span>
              <button
                type="button"
                aria-label="Remove file"
                onClick={() => handleFileChange(null)}
                className="text-ink-faint hover:text-ink"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="flex w-full flex-col items-center gap-2 rounded-md border border-dashed border-border-strong bg-paper px-4 py-8 text-ink-muted transition-colors hover:border-ink hover:text-ink"
            >
              <UploadCloud className="h-6 w-6" />
              <span className="text-sm">Click to choose a PDF, up to 5MB</span>
            </button>
          )}

          <input
            ref={inputRef}
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
          />

          {fileError && <p className="mt-1.5 text-sm text-danger">{fileError}</p>}
        </div>

        <div>
          <label
            htmlFor="job-description"
            className="mb-1.5 block text-sm font-medium text-ink"
          >
            Job description{" "}
            <span className="font-normal text-ink-faint">(optional)</span>
          </label>
          <textarea
            id="job-description"
            rows={5}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description to get a match score against it."
            className="w-full rounded-md border border-border-strong bg-paper-raised px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-ink focus:outline-none focus:ring-2 focus:ring-accent/20"
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}

        <Button type="submit" loading={loading} className="w-full sm:w-auto">
          Analyze resume
        </Button>
      </form>
    </Card>
  );
}
