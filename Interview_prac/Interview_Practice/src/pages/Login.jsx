import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const Login = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!form.email || !form.password) {
      setError("Please enter both email and password.");
      setLoading(false);
      return;
    }

    // API CALL
    const response = await api.post("/login", form);

    setLoading(false);

    if (response?.success) {
      navigate("/role"); // move to role selector page
    } else {
      setError(response?.message || "Invalid login. Try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black text-white flex items-center justify-center px-4 py-8">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }}></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/30 shadow-2xl">
          
          {/* Logo / Title */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
              Interview Master
            </h1>
            <p className="text-cyan-200 text-sm">Perfect your interview skills with AI</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Email Input */}
            <div>
              <label className="block text-sm font-semibold mb-2 text-cyan-300">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white/10 border border-cyan-500/50 rounded-xl placeholder-cyan-300/50 text-white focus:outline-none focus:border-cyan-300 focus:ring-2 focus:ring-cyan-500/30 transition"
                required
              />
            </div>

            {/* Password Input */}
            <div>
              <label className="block text-sm font-semibold mb-2 text-cyan-300">
                Password
              </label>
              <input
                type="password"
                name="password"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white/10 border border-cyan-500/50 rounded-xl placeholder-cyan-300/50 text-white focus:outline-none focus:border-cyan-300 focus:ring-2 focus:ring-cyan-500/30 transition"
                required
              />
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm font-medium">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-xl hover:from-cyan-400 hover:to-blue-500 transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white mr-2"></div>
                  Logging in...
                </span>
              ) : (
                "Login"
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center justify-center">
            <div className="border-t border-cyan-500/30 w-1/3"></div>
            <span className="mx-2 text-cyan-400 text-sm font-medium">or</span>
            <div className="border-t border-cyan-500/30 w-1/3"></div>
          </div>

          {/* Guest Mode */}
          <button
            onClick={() => navigate("/role")}
            className="w-full py-3 border-2 border-cyan-500/50 text-cyan-300 font-bold rounded-xl hover:bg-cyan-500/20 hover:border-cyan-400 transition transform hover:scale-105"
          >
            Continue as Guest
          </button>

          {/* Footer */}
          <p className="text-center text-cyan-300/60 text-xs mt-6">
            © 2024 Interview Master. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
