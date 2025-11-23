import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useInterview } from "../utils/InterviewContext.jsx";

const rolesList = [
  "Software Engineer",
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "Machine Learning Engineer",
  "Data Scientist",
  "AI Engineer",
  "DevOps Engineer",
  "Cloud Engineer",
  "Cybersecurity Analyst",
  "QA / Test Engineer",
  "Mobile App Developer",
  "UI/UX Designer",
  "Product Manager",
  "Data Analyst",
  "Blockchain Developer",
  "Game Developer",
  "Network Engineer",
  "Database Administrator",
  "IT Support Engineer",
  "Site Reliability Engineer",
  "Embedded Systems Engineer",
  "Big Data Engineer",
  "Business Analyst",
];

const RoleSelector = () => {
  const navigate = useNavigate();
  const { role, setRole } = useInterview();
  const [selectedRole, setSelectedRole] = useState(role || "");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const filteredRoles = rolesList.filter((role) =>
    role.toLowerCase().includes(search.toLowerCase())
  );

  const handleContinue = async () => {
    if (!selectedRole) {
      setError("Please select a job role.");
      return;
    }

    setError("");

    // Save to context
    setRole(selectedRole);

    // SAVE ROLE TO BACKEND SESSION
    await api.post("/set-role", { role: selectedRole });

    navigate("/experience");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black text-white flex items-center justify-center px-4 py-10">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }}></div>
      </div>

      <div className="relative z-10 w-full max-w-4xl">
        {/* Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/30 shadow-2xl">
          
          {/* Heading */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
              Select Your Role
            </h1>
            <p className="text-cyan-200">Choose the position you want to interview for</p>
          </div>

          {/* Search Bar */}
          <div className="mb-8">
            <input
              type="text"
              placeholder="🔍 Search job roles..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-5 py-3 bg-white/10 border border-cyan-500/50 rounded-xl placeholder-cyan-300/50 text-white focus:outline-none focus:border-cyan-300 focus:ring-2 focus:ring-cyan-500/30 transition"
            />
          </div>

          {/* Grid of Roles */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto pr-2 mb-6">
            {filteredRoles.length === 0 ? (
              <p className="text-center text-cyan-300 col-span-full py-8">No roles found</p>
            ) : (
              filteredRoles.map((role, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedRole(role)}
                  className={`p-4 border-2 rounded-xl text-left font-semibold transition-all transform hover:scale-105 ${
                    selectedRole === role
                      ? "bg-gradient-to-r from-cyan-500 to-blue-600 border-cyan-400 text-white shadow-lg shadow-cyan-500/50"
                      : "bg-white/5 border-cyan-500/30 text-cyan-100 hover:bg-white/10 hover:border-cyan-400"
                  }`}
                >
                  {role}
                </button>
              ))
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm font-medium mb-4">
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

export default RoleSelector;
