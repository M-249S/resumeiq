import { useEffect, useRef, useState } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { UploadPanel } from "@/components/dashboard/UploadPanel";
import { AnalysisResults } from "@/components/dashboard/AnalysisResults";
import { CoverLetterPanel } from "@/components/dashboard/CoverLetterPanel";
import { AnalysisSkeleton } from "@/components/dashboard/AnalysisSkeleton";
import { useToast } from "@/hooks/useToast";
import { friendlyErrorMessage } from "@/lib/errors";
import { uploadResume, downloadImprovedResume, saveBlobAsFile } from "@/services/resume";
import type { ResumeAnalysis } from "@/types/resume";

export function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");
  const toast = useToast();
  const resultsRef = useRef<HTMLDivElement>(null);

  // Bring the skeleton / results into view: on small screens they start
  // below the fold, so without this the click appears to do nothing.
  useEffect(() => {
    if (analyzing || analysis) {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [analyzing, analysis]);

  async function handleAnalyze(selectedFile: File, description: string) {
    setError("");
    setAnalyzing(true);
    try {
      const result = await uploadResume(selectedFile, description);
      setFile(selectedFile);
      setJobDescription(description);
      setAnalysis(result.analysis);
    } catch (err) {
      setError(
        friendlyErrorMessage(
          err,
          "Something went wrong while analyzing your resume. Please try again.",
        ),
      );
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
      toast.show(friendlyErrorMessage(err, "Couldn't download the improved resume. Please try again."));
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-8">
          <h1 className="font-display text-2xl font-medium text-ink">
            Analyze your resume
          </h1>
          <p className="mt-1 text-ink-muted">
            Upload a PDF and, optionally, a job description to score your match.
          </p>
        </div>

        <UploadPanel onSubmit={handleAnalyze} loading={analyzing} error={error} />

        <div ref={resultsRef} className="scroll-mt-24">
        {analyzing && (
          <div className="mt-8">
            <AnalysisSkeleton />
          </div>
        )}

        {!analyzing && analysis && (
          <div className="mt-8 space-y-8">
            <AnalysisResults
              analysis={analysis}
              onDownload={handleDownload}
              downloading={downloading}
            />

            {file && (
              <CoverLetterPanel file={file} jobDescription={jobDescription} />
            )}
          </div>
        )}
        </div>
      </main>
    </div>
  );
}
