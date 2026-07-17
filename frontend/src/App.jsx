import Header from "./components/Header";
import UploadCard from "./components/UploadCard";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-200">

      <div className="max-w-6xl mx-auto px-6 py-12">

        <Header />

        <div className="mt-10">
          <UploadCard />
        </div>

        {/* Features */}

        <div className="grid md:grid-cols-3 gap-6 mt-16">

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-4xl mb-4">📄</div>

            <h2 className="text-xl font-bold mb-3">
              ATS Resume Analysis
            </h2>

            <p className="text-gray-600">
              Analyze your resume using AI and receive an ATS compatibility
              score with strengths, weaknesses, and missing keywords.
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-4xl mb-4">✨</div>

            <h2 className="text-xl font-bold mb-3">
              AI Resume Rewrite
            </h2>

            <p className="text-gray-600">
              Instantly rewrite your resume with professional wording while
              preserving your real experience and achievements.
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-4xl mb-4">💼</div>

            <h2 className="text-xl font-bold mb-3">
              AI Cover Letter
            </h2>

            <p className="text-gray-600">
              Generate a personalized cover letter tailored to the job
              description in just a few seconds.
            </p>
          </div>

        </div>

        {/* Footer */}

        <footer className="mt-20 border-t pt-8 text-center text-gray-500">

          <p className="font-semibold text-gray-700">
            AI Resume Optimizer
          </p>

          <p className="mt-2">
            Built with ❤️ using FastAPI, React & Gemini AI
          </p>

          <p className="mt-4 text-sm">
            Version 1.0.0
          </p>

        </footer>

      </div>

    </div>
  );
}