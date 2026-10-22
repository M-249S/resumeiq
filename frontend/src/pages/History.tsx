import { useEffect, useState, useCallback } from "react";
import { isAxiosError } from "axios";
import { ArrowLeft, FileText, Trash2 } from "lucide-react";
import { Navbar } from "@/components/landing/Navbar";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { AnalysisResults } from "@/components/dashboard/AnalysisResults";
import {
  getResumeHistory,
  getResumeHistoryDetail,
  deleteResumeHistoryEntry,
} from "@/services/resume";
import type { ResumeHistoryItem, ResumeHistoryDetail } from "@/types/resume";

function friendlyErrorMessage(err: unknown): string {
  if (isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
  }
  return "Something went wrong. Please try again.";
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function History() {
  const [items, setItems] = useState<ResumeHistoryItem[] | null>(null);
  const [selected, setSelected] = useState<ResumeHistoryDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const loadHistory = useCallback(async () => {
    try {
      const data = await getResumeHistory();
      setItems(data);
    } catch (err) {
      setError(friendlyErrorMessage(err));
    }
  }, []);

  useEffect(() => {
    // This is a fetch-on-mount effect: the setState calls inside
    // loadHistory only run after the `await` resolves, not synchronously
    // during this callback, so there's no cascading-render risk here.
    // oxlint's static check can't see past the async boundary though, so:
    // oxlint-disable-next-line react/set-state-in-effect
    void loadHistory();
  }, [loadHistory]);

  async function handleOpen(id: number) {
    setError("");
    setLoadingDetail(true);
    try {
      const detail = await getResumeHistoryDetail(id);
      setSelected(detail);
    } catch (err) {
      setError(friendlyErrorMessage(err));
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleDelete(id: number) {
    setError("");
    setDeletingId(id);
    try {
      await deleteResumeHistoryEntry(id);
      setItems((prev) => prev?.filter((item) => item.id !== id) ?? null);
      if (selected?.id === id) setSelected(null);
    } catch (err) {
      setError(friendlyErrorMessage(err));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-12">
        {selected ? (
          <div>
            <button
              type="button"
              onClick={() => setSelected(null)}
              className="mb-6 inline-flex items-center gap-2 text-sm text-ink-muted hover:text-ink"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to history
            </button>

            <div className="mb-6">
              <h1 className="font-display text-2xl font-medium text-ink">
                {selected.filename}
              </h1>
              <p className="mt-1 text-sm text-ink-faint">
                Analyzed {formatDate(selected.created_at)}
              </p>
            </div>

            <AnalysisResults analysis={selected.analysis} />
          </div>
        ) : (
          <div>
            <div className="mb-8">
              <h1 className="font-display text-2xl font-medium text-ink">
                Resume history
              </h1>
              <p className="mt-1 text-ink-muted">
                Every resume you've analyzed, with its scores at the time.
              </p>
            </div>

            {error && (
              <p className="mb-4 text-sm text-danger">{error}</p>
            )}

            {items === null && (
              <p className="text-sm text-ink-faint">Loading…</p>
            )}

            {items !== null && items.length === 0 && (
              <Card className="flex flex-col items-center gap-3 p-10 text-center">
                <FileText className="h-8 w-8 text-ink-faint" />
                <p className="text-ink-muted">
                  No analyses yet — upload a resume from the dashboard to get started.
                </p>
              </Card>
            )}

            {items !== null && items.length > 0 && (
              <ul className="space-y-3">
                {items.map((item) => (
                  <li key={item.id}>
                    <Card className="flex items-center justify-between gap-4 p-5">
                      <button
                        type="button"
                        onClick={() => handleOpen(item.id)}
                        disabled={loadingDetail}
                        className="flex min-w-0 flex-1 items-center gap-4 text-left"
                      >
                        <FileText className="h-5 w-5 shrink-0 text-ink-faint" />
                        <div className="min-w-0">
                          <p className="truncate font-medium text-ink">
                            {item.filename}
                          </p>
                          <p className="text-sm text-ink-faint">
                            {formatDate(item.created_at)}
                          </p>
                        </div>
                      </button>

                      <div className="flex shrink-0 items-center gap-3">
                        <Badge variant="accent">{item.score} overall</Badge>
                        <Badge variant="neutral">{item.match_score} match</Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          loading={deletingId === item.id}
                          onClick={() => handleDelete(item.id)}
                          aria-label={`Delete analysis of ${item.filename}`}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </Card>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
