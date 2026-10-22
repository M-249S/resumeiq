import { api } from "@/lib/api";
import type {
  ResumeUploadResponse,
  CoverLetterResponse,
  ResumeHistoryItem,
  ResumeHistoryDetail,
} from "@/types/resume";

/**
 * POST /resume/upload — multipart/form-data. Do NOT set a Content-Type
 * header manually here: axios/the browser sets the correct
 * `multipart/form-data; boundary=...` value automatically when the body
 * is a FormData instance, and overriding it breaks the upload.
 */
export async function uploadResume(
  file: File,
  jobDescription: string,
): Promise<ResumeUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_description", jobDescription);

  const { data } = await api.post<ResumeUploadResponse>(
    "/resume/upload",
    formData,
  );
  return data;
}

/**
 * POST /resume/download — same file, rewritten and returned as a PDF
 * binary stream. Requires `responseType: "blob"` or axios will try (and
 * fail) to parse the binary response as text/JSON.
 */
export async function downloadImprovedResume(file: File): Promise<Blob> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/resume/download", formData, {
    responseType: "blob",
  });
  return response.data as Blob;
}

/** Triggers a browser "Save As" for a Blob without a full page navigation. */
export function saveBlobAsFile(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/** POST /resume/cover-letter — same file + job description, returns text. */
export async function generateCoverLetter(
  file: File,
  jobDescription: string,
): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_description", jobDescription);

  const { data } = await api.post<CoverLetterResponse>(
    "/resume/cover-letter",
    formData,
  );
  return data.cover_letter;
}

/** POST /resume/cover-letter/download — same inputs, returns a DOCX blob. */
export async function downloadCoverLetterDocx(
  file: File,
  jobDescription: string,
): Promise<Blob> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_description", jobDescription);

  const response = await api.post("/resume/cover-letter/download", formData, {
    responseType: "blob",
  });
  return response.data as Blob;
}

/** GET /resume/history — the signed-in user's past analyses, newest first. */
export async function getResumeHistory(): Promise<ResumeHistoryItem[]> {
  const { data } = await api.get<ResumeHistoryItem[]>("/resume/history");
  return data;
}

/** GET /resume/history/{id} — a single past analysis, full breakdown included. */
export async function getResumeHistoryDetail(
  id: number,
): Promise<ResumeHistoryDetail> {
  const { data } = await api.get<ResumeHistoryDetail>(`/resume/history/${id}`);
  return data;
}

/** DELETE /resume/history/{id} — removes one past analysis permanently. */
export async function deleteResumeHistoryEntry(id: number): Promise<void> {
  await api.delete(`/resume/history/${id}`);
}
