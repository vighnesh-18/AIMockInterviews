import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useInterview } from "../utils/InterviewContext.jsx";

const difficultyLevels = [
  { label: "Easy", value: "easy", desc: "Basic-level questions" },
  { label: "Medium", value: "medium", desc: "Moderate difficulty" },
  { label: "Hard", value: "hard", desc: "Advanced interview questions" },
  { label: "Expert", value: "expert", desc: "For senior-level challenge" },
];

const DifficultySelector = () => {
  const navigate = useNavigate();
  const { difficulty, setDifficulty } = useInterview();
  const [selectedDifficulty, setSelectedDifficulty] = useState(difficulty || "");
  const [error, setError] = useState("");

  const handleContinue = async () => {
    if (!selectedDifficulty) {
      setError("Please choose a difficulty level.");
      return;
    }

    setError("");

    // Save to context
    setDifficulty(selectedDifficulty);

    // Save difficulty to backend session
    await api.post("/set-difficulty", { difficulty: selectedDifficulty });

    navigate("/resume-upload");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black text-white flex items-center justify-center px-4 py-10">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }}></div>
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        {/* Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/30 shadow-2xl">

          {/* Heading */}
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
              Choose Difficulty
            </h1>
            <p className="text-cyan-200">Select the challenge level for your interview</p>
          </div>

          {/* Difficulty Cards */}
          <div className="grid grid-cols-1 gap-4 mb-6">
            {difficultyLevels.map((item, index) => (
              <button
                key={index}
                onClick={() => setSelectedDifficulty(item.value)}
                className={`w-full p-5 border-2 rounded-xl text-left transition-all transform hover:scale-105 ${
                  selectedDifficulty === item.value
                    ? "bg-gradient-to-r from-cyan-500 to-blue-600 border-cyan-400 text-white shadow-lg shadow-cyan-500/50"
                    : "bg-white/5 border-cyan-500/30 text-cyan-100 hover:bg-white/10 hover:border-cyan-400"
                }`}
              >
                <h3 className="font-bold text-lg">{item.label}</h3>
                <p
                  className={`text-sm mt-1 ${
                    selectedDifficulty === item.value
                      ? "text-cyan-100"
                      : "text-cyan-300/70"
                  }`}
                >
                  {item.desc}
                </p>
              </button>
            ))}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm font-medium mb-4 text-center">
              {error}
            </div>
          )}

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-xl hover:from-cyan-400 hover:to-blue-500 transition transform hover:scale-105 shadow-lg"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default DifficultySelector;
