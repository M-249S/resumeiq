import { useState } from "react";
import api from "../services/api";
import ScoreCard from "./ScoreCard";

import {
  FaCheckCircle,
  FaExclamationTriangle,
  FaLightbulb,
  FaTools,
} from "react-icons/fa";

export default function UploadCard() {
  const [file, setFile] =useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const [result, setResult] = useState(null);
  const [coverLetter, setCoverLetter] = useState("");

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);

    try {
      setLoading(true);

      const response = await api.post(
        "/resume/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log(response.data);

      setResult(response.data.analysis);
    } catch (error) {
      console.error(error);
      alert("Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleCoverLetter = async () => {
    if (!file) {
      alert("Please select a PDF.");
      return;
    }

    if (!jobDescription.trim()) {
      alert("Please paste the job description.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);

    try {
      setLoading(true);

      const response = await api.post(
        "/resume/cover-letter",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log(response.data);

      setCoverLetter(response.data.cover_letter);
    } catch (error) {
      console.error(error);
      alert("Failed to generate Cover Letter.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl p-8">

      <h2 className="text-3xl font-bold text-slate-800 mb-6">
        Upload Resume
      </h2>

      <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-xl p-10 cursor-pointer hover:border-blue-500 transition">

        <input
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <p className="text-slate-500 text-lg">
          {file ? file.name : "Click here or drag your PDF resume"}
        </p>

      </label>

      <div className="mt-6">
        <label className="block text-lg font-semibold mb-2">
          Job Description
        </label>

        <textarea
          rows={8}
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the job description here..."
          className="w-full border rounded-xl p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        onClick={handleUpload}
        disabled={loading}
        className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-xl transition disabled:bg-gray-400"
      >
        {loading ? "Analyzing..." : "Analyze Resume"}
      </button>

      <button
        onClick={handleCoverLetter}
        disabled={loading}
        className="w-full mt-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 rounded-xl transition disabled:bg-gray-400"
      >
        {loading ? "Generating..." : "Generate Cover Letter"}
      </button>

      {result && (
        <div className="mt-10 border-t pt-8">

          <div className="grid md:grid-cols-2 gap-6 mb-8">

            <ScoreCard
              score={result.score}
              title="Resume Score"
            />

            <ScoreCard
              score={result.match_score}
              title="Job Match"
            />

          </div>

          <div className="mb-8">
            <h3 className="flex items-center gap-2 text-green-600 font-bold text-xl mb-4">
              <FaCheckCircle />
              Strengths
            </h3>

            <ul className="space-y-3">
              {result.strengths.map((item, index) => (
                <li
                  key={index}
                  className="bg-green-50 rounded-lg p-4"
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="mb-8">
            <h3 className="flex items-center gap-2 text-orange-500 font-bold text-xl mb-4">
              <FaExclamationTriangle />
              Weaknesses
            </h3>

            <ul className="space-y-3">
              {result.weaknesses.map((item, index) => (
                <li
                  key={index}
                  className="bg-orange-50 rounded-lg p-4"
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="mb-8">
            <h3 className="flex items-center gap-2 text-green-600 font-bold text-xl mb-4">
              <FaCheckCircle />
              Matching Skills
            </h3>

            <ul className="space-y-3">
              {result.matching_skills.map((item, index) => (
                <li
                  key={index}
                  className="bg-green-50 rounded-lg p-4"
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="mb-8">
            <h3 className="flex items-center gap-2 text-red-500 font-bold text-xl mb-4">
              <FaTools />
              Missing Skills
            </h3>

            <ul className="space-y-3">
              {result.missing_skills.map((item, index) => (
                <li
                  key={index}
                  className="bg-red-50 rounded-lg p-4"
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="mb-8">
            <h3 className="flex items-center gap-2 text-blue-600 font-bold text-xl mb-4">
              <FaLightbulb />
              Suggestions
            </h3>

            <ul className="space-y-3">
              {result.suggestions.map((item, index) => (
                <li
                  key={index}
                  className="bg-blue-50 rounded-lg p-4"
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>

        </div>
      )}

      {coverLetter && (
        <div className="mt-10 border-t pt-8">

          <h3 className="text-2xl font-bold mb-4">
            Cover Letter
          </h3>

          <textarea
            readOnly
            value={coverLetter}
            className="w-full h-[500px] rounded-xl border p-5 bg-gray-50 font-mono"
          />

        </div>
      )}

    </div>
  );
}