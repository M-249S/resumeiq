import type { ResumeHistoryItem } from "@/types/resume";

/** Files are grouped case-insensitively so "CV.pdf" and "cv.PDF" count as one resume. */
export function fileKey(filename: string): string {
  return filename.trim().toLowerCase();
}

/**
 * Score change versus the previous analysis of the same file.
 * `items` must be newest first (as the API returns them). Returns a map of
 * analysis id to delta. A previous score of 0 is skipped: older analyses that
 * were run without a job description were stored as 0 and would show a
 * misleading jump.
 */
export function scoreDeltas(items: ResumeHistoryItem[]): Map<number, number> {
  const deltas = new Map<number, number>();
  const seen = new Map<string, ResumeHistoryItem[]>();
  for (const item of items) {
    const key = fileKey(item.filename);
    const group = seen.get(key) ?? [];
    group.push(item);
    seen.set(key, group);
  }
  for (const group of seen.values()) {
    group.forEach((item, i) => {
      const previous = group[i + 1];
      if (previous && previous.score > 0 && item.score > 0) {
        deltas.set(item.id, item.score - previous.score);
      }
    });
  }
  return deltas;
}

/**
 * The resume with the most scored analyses (at least two), oldest first,
 * for the progress chart. Ties go to the most recently analysed file.
 */
export function mostImprovedSeries(items: ResumeHistoryItem[]): ResumeHistoryItem[] {
  const groups = new Map<string, ResumeHistoryItem[]>();
  for (const item of items) {
    if (item.score <= 0) continue;
    const key = fileKey(item.filename);
    groups.set(key, [...(groups.get(key) ?? []), item]);
  }
  let best: ResumeHistoryItem[] = [];
  for (const group of groups.values()) {
    if (group.length >= 2 && group.length > best.length) best = group;
  }
  return [...best].reverse();
}
