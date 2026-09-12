import { useState } from "react";
import { isAxiosError } from "axios";
import { Navbar } from "@/components/landing/Navbar";
import { UploadPanel } from "@/components/dashboard/UploadPanel";
import { AnalysisResults } from "@/components/dashboard/AnalysisResults";
import { CoverLetterPanel } from "@/components/dashboard/CoverLetterPanel";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { uploadResume, downloadImprovedResume, saveBlobAsFile } from "@/services/resume";
import type { ResumeAnalysis } from "@/types/resume";

function friendlyErrorMessage(err: unknown): string {
  if (isAxiosError(err)) {
    if (err.response?.status === 429) {
      return "You've hit the analysis limit for now — please wait a minute and try again.";
    }
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
  }
  return "Something went wrong while analyzing your resume. Please try again.";
}

export function Dashboard() {
  const { user, logout } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze(selectedFile: File, description: string) {
    setError("");
    setAnalyzing(true);
    try {
      const result = await uploadResume(selectedFile, description);
      setFile(selectedFile);
      setJobDescription(description);
      setAnalysis(result.analysis);
    } catch (err) {
      setError(friendlyErrorMessage(err));
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleDownload() {
    if (!file) return;
    setDownloading(true);
    try {
      const blob = await downloadImprovedResume(file);
      saveBlobAsFile(blob, "improved-resume.pdf");
    } catch (err) {
      setError(friendlyErrorMessage(err));
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="font-display text-2xl font-medium text-ink">
              Analyze your resume
            </h1>
            <p className="mt-1 text-ink-muted">
              Upload a PDF and, optionally, a job description to score your match.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {user && <span className="text-sm text-ink-faint">{user.full_name}</span>}
            <Button variant="ghost" size="sm" onClick={logout}>
              Log out
            </Button>
          </div>
        </div>

        <UploadPanel onSubmit={handleAnalyze} loading={analyzing} error={error} />

        {analysis && (
          <div className="mt-8 space-y-8">
            <AnalysisResults
              analysis={analysis}
              onDownload={handleDownload}
              downloading={downloading}
            />

            {file && (
              <CoverLetterPanel
                file={file}
                jobDescription={jobDescription}
                onError={setError}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}
