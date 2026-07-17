import { useState } from "react";
import api from "../services/api";
import ReactMarkdown from "react-markdown";
import { FaMagic, FaCopy } from "react-icons/fa";

export default function RewriteResume({ file }) {
  const [loading, setLoading] = useState(false);
  const [resume, setResume] = useState("");

  const handleRewrite = async () => {
    if (!file) {
      alert("Please upload a resume first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await api.post(
        "/resume/improve",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResume(response.data.resume);

    } catch (error) {
      console.error(error);
      alert("Failed to rewrite resume.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(resume);
      alert("Resume copied successfully!");
    } catch (err) {
      console.error(err);
      alert("Failed to copy.");
    }
  };

  return (
    <div className="mt-12">

      <button
        onClick={handleRewrite}
        disabled={loading}
        className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 rounded-xl transition disabled:bg-gray-400"
      >
        {loading ? (
          "Improving..."
        ) : (
          <span className="flex justify-center items-center gap-2">
            <FaMagic />
            Improve Resume with AI
          </span>
        )}
      </button>

      {resume && (
        <div className="mt-10">

          <div className="flex justify-between items-center mb-6">

            <h2 className="text-3xl font-bold">
              AI Improved Resume
            </h2>

            <button
              onClick={handleCopy}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
            >
              <FaCopy />
              Copy
            </button>

          </div>

          <div className="prose prose-lg max-w-none bg-white border rounded-xl shadow-md p-8">

            <ReactMarkdown>
              {resume}
            </ReactMarkdown>

          </div>

        </div>
      )}

    </div>
  );
}