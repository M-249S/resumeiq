import { isAxiosError } from "axios";

/**
 * Turns any thrown value into a message that is safe and useful to show to
 * a user. Network failures get their own wording because the free-tier
 * backend sleeps when idle, so "can't reach the server" usually means
 * "still waking up", not "broken".
 */
export function friendlyErrorMessage(
  err: unknown,
  fallback = "Something went wrong. Please try again.",
): string {
  if (isAxiosError(err)) {
    if (!err.response) {
      return "Can't reach the server. It may be waking up, so wait a few seconds and try again.";
    }
    if (err.response.status === 429) {
      return "You've hit the limit for now. Please wait a minute and try again.";
    }
    if (err.response.status === 413) {
      return "That file is too large. Please use a PDF under 5MB.";
    }
    const detail = err.response.data?.detail;
    if (typeof detail === "string") return detail;
  }
  return fallback;
}

/** True when a failed request says nothing about the credentials themselves. */
export function isServerSideFailure(err: unknown): boolean {
  if (!isAxiosError(err)) return false;
  const status = err.response?.status;
  return !err.response || status === 429 || (status !== undefined && status >= 500);
}
