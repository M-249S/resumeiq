import {
  CircularProgressbar,
  buildStyles,
} from "react-circular-progressbar";

import "react-circular-progressbar/dist/styles.css";

import { FaTrophy } from "react-icons/fa";

export default function ScoreCard({
  score,
  title = "ATS Resume Score",
}) {
  let color = "#ef4444";
  let label = "Needs Improvement";

  if (score >= 80) {
    color = "#22c55e";
    label = "Excellent";
  } else if (score >= 60) {
    color = "#f59e0b";
    label = "Good";
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">

      <div className="flex items-center gap-3 mb-6">
        <FaTrophy className="text-yellow-500 text-3xl" />

        <h2 className="text-2xl font-bold">
          {title}
        </h2>
      </div>

      <div className="flex flex-col items-center">

        <div className="w-56 h-56">
          <CircularProgressbar
            value={score}
            text={`${score}%`}
            styles={buildStyles({
              textSize: "20px",
              pathColor: color,
              textColor: color,
              trailColor: "#e5e7eb",
              strokeLinecap: "round",
            })}
          />
        </div>

        <div className="mt-6 text-center">

          <p
            className="text-3xl font-extrabold"
            style={{ color }}
          >
            {score}/100
          </p>

          <p
            className="text-xl font-semibold mt-2"
            style={{ color }}
          >
            {label}
          </p>

        </div>

        <div className="w-full mt-8">

          <div className="flex justify-between text-sm text-gray-500 mb-2">
            <span>0</span>
            <span>50</span>
            <span>100</span>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3">

            <div
              className="h-3 rounded-full transition-all duration-700"
              style={{
                width: `${score}%`,
                backgroundColor: color,
              }}
            />

          </div>

        </div>

      </div>

    </div>
  );
}