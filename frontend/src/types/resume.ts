export interface ResumeAnalysis {
  score: number;
  match_score: number;

  ats_level: string;
  summary: string;

  formatting_score: number;
  keyword_score: number;
  experience_score: number;
  skills_score: number;
  education_score: number;
  readability_score: number;

  strengths: string[];
  weaknesses: string[];

  matching_skills: string[];
  missing_skills: string[];

  suggestions: string[];
}

export interface ResumeUploadResponse {
  filename: string;
  pages: number;
  analysis: ResumeAnalysis;
}

export interface CoverLetterResponse {
  cover_letter: string;
}
