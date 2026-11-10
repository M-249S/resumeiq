import { useEffect, useRef, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { isAxiosError } from "axios";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { UploadPanel } from "@/components/dashboard/UploadPanel";
import { AnalysisResults } from "@/components/dashboard/AnalysisResults";
import { AnalysisSkeleton } from "@/components/dashboard/AnalysisSkeleton";
import { SignupPrompt } from "@/components/dashboard/SignupPrompt";
import { useAuth } from "@/hooks/useAuth";
import { friendlyErrorMessage } from "@/lib/errors";
import { analyzeResumeDemo } from "@/services/resume";
import type { ResumeAnalysis } from "@/types/resume";

const QUOTA_MESSAGE =
  "You've used the free demo analyses for now. Create a free account to keep going.";

/** Public page: analyze one resume without an account. Nothing is saved. */
export function Try() {
  const { isAuthenticated } = useAuth();
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (analyzing || analysis) {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [analyzing, analysis]);

  // Signed-in users have the full dashboard; the demo would only confuse.
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  async function handleAnalyze(file: File, jobDescription: string) {
    setError("");
    setAnalysis(null);
    setAnalyzing(true);
    try {
      const result = await analyzeResumeDemo(file, jobDescription);
      setAnalysis(result.analysis);
    } catch (err) {
      if (isAxiosError(err) && err.response?.status === 429) {
        // The server's detail distinguishes "daily budget used up" from the
        // per-visitor limit, whose body has no detail field.
        const detail = err.response.data?.detail;
        setError(typeof detail === "string" ? detail : QUOTA_MESSAGE);
      } else {
        setError(
          friendlyErrorMessage(
            err,
            "Something went wrong while analyzing your resume. Please try again.",
          ),
        );
      }
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-8">
          <h1 className="font-display text-2xl font-medium text-ink">
            Try ResumeIQ, no account needed
          </h1>
          <p className="mt-1 text-ink-muted">
            Upload a PDF and, optionally, a job description. Nothing is saved.
            Have an account?{" "}
            <Link to="/login" className="text-accent underline-offset-4 hover:underline">
              Log in
            </Link>
          </p>
        </div>

        <UploadPanel
          onSubmit={handleAnalyze}
          loading={analyzing}
          error={error}
          maxSizeLabel="2MB"
        />

        <p className="mt-3 text-xs text-ink-faint">
          Free demo limits: one PDF up to 2MB and 4 pages, a few analyses per hour.{" "}
          Your text is sent to AI providers to produce the result; see the{" "}
          <Link to="/privacy" className="underline underline-offset-2">
            Privacy Policy
          </Link>
          .
        </p>

        <div ref={resultsRef} className="scroll-mt-24">
          {analyzing && (
            <div className="mt-8">
              <AnalysisSkeleton />
            </div>
          )}

          {!analyzing && analysis && (
            <div className="mt-8 space-y-8">
              <AnalysisResults analysis={analysis} />
              <SignupPrompt />
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
