import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useInterview } from "../utils/InterviewContext.jsx";
import { api } from "../api.js";
import * as pdfjsLib from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

// Use worker from node_modules
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

const MAX_FILE_SIZE = 5 * 1024 * 1024;

export default function ResumeUpload() {
  const navigate = useNavigate();
  const { setResumeText, setResumeFile } = useInterview();

  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");

  const extractTextFromPDF = async (file) => {
    setLoading(true);
    setProgress(20);
    setError("");

    try {
      const arrayBuffer = await file.arrayBuffer();
      
      // Validate file is not empty
      if (arrayBuffer.byteLength === 0) {
        setError("File is empty. Please upload a valid PDF.");
        setLoading(false);
        return;
      }
      
      setProgress(40);

      // Load PDF document
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      
      // Validate PDF has pages
      if (!pdf.numPages || pdf.numPages === 0) {
        setError("PDF has no pages. Please upload a valid PDF.");
        setLoading(false);
        return;
      }
      
      setProgress(60);

      // Extract text from all pages
      let text = "";
      for (let i = 1; i <= pdf.numPages; i++) {
        try {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          text += content.items.map(item => item.str).join(" ") + "\n\n";
        } catch (pageErr) {
          console.warn(`Warning: Could not extract text from page ${i}:`, pageErr);
          // Continue with other pages instead of failing
        }
        setProgress(60 + (i / pdf.numPages) * 35);
      }

      // Validate extracted text is not empty
      const trimmedText = text.trim();
      if (!trimmedText || trimmedText.length < 10) {
        setError("No text found in PDF. It might be a scanned image. Try uploading a text-based PDF or use 'Build Resume' instead.");
        setLoading(false);
        return;
      }

      setProgress(90);
      setResumeText(trimmedText);
      setResumeFile(file);
      
      // Send resume to preview endpoint to show what will be extracted
      try {
        console.log("📤 Sending resume to backend for preview...");
        const previewResponse = await api.post("/preview-interview", {
          role: "Software Engineer", // Default role for preview
          experience: "2-3",
          difficulty: "Medium",
          resume_text: trimmedText,
          user_message: "start",
          conversation_history: null
        });
        
        if (previewResponse.success) {
          console.log("✅ Resume preview received!");
          console.log("📝 Summary:", previewResponse.resume_summary);
          console.log("🛠️  Skills:", previewResponse.skills);
          console.log("🚀 Projects:", previewResponse.projects);
          console.log("💼 Experience:", previewResponse.experience);
          console.log("❓ First Question:", previewResponse.first_question);
        }
      } catch (previewErr) {
        console.warn("Preview request failed (non-critical):", previewErr);
      }
      
      setProgress(100);
      setTimeout(() => navigate("/interview"), 1000);
    } catch (err) {
      console.error("PDF Parsing Error:", err);
      console.error("Error name:", err.name);
      console.error("Error message:", err.message);
      
      // Provide specific error messages based on error type
      if (err.message.includes("Invalid PDF")) {
        setError("Invalid PDF file. Please ensure the file is a valid PDF.");
      } else if (err.message.includes("Corrupted")) {
        setError("PDF file appears to be corrupted. Try re-saving it.");
      } else if (err.message.includes("worker")) {
        setError("PDF worker failed to load. Check your internet connection and try again.");
      } else if (err.message.includes("CORS")) {
        setError("CORS error: Cannot load PDF worker. Try using 'Build Resume' instead.");
      } else {
        setError(`Failed to read PDF: ${err.message || "Unknown error"}. Try 'Build Resume' instead.`);
      }
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  const handleFile = (file) => {
    if (!file) return;
    if (file.size > MAX_FILE_SIZE) return setError("File too large");
    if (file.type !== "application/pdf") return setError("Only PDF allowed");
    setFileName(file.name);
    extractTextFromPDF(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black text-white flex items-center justify-center px-4 py-10">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }}></div>
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        {/* Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/30 shadow-2xl">
          
          {/* Heading */}
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
              Upload Your Resume
            </h1>
            <p className="text-cyan-200">PDF file to personalize your interview experience</p>
          </div>

          {/* Upload Area */}
          <div
            className="border-2 border-dashed border-cyan-500/50 rounded-xl p-12 hover:border-cyan-400 hover:bg-white/5 transition-all cursor-pointer relative mb-6"
            onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
            onDragOver={(e) => e.preventDefault()}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => handleFile(e.target.files?.[0])}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
            <div className="text-center">
              <div className="text-6xl mb-4">📄</div>
              <p className="text-xl font-bold text-cyan-300 mb-2">
                {loading ? "Reading PDF..." : "Drop your PDF here"}
              </p>
              <p className="text-cyan-200/70 text-sm">or click to browse</p>
              {fileName && (
                <p className="text-green-400 font-semibold mt-4">✅ Selected: {fileName}</p>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          {loading && (
            <div className="mb-6">
              <div className="bg-white/10 border border-cyan-500/30 rounded-full h-3 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 transition-all duration-300" 
                  style={{ width: `${progress}%` }} 
                />
              </div>
              <p className="text-center text-cyan-300 text-sm mt-2 font-semibold">{progress}%</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm font-medium mb-6 text-center">
              {error}
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-4 flex-col sm:flex-row">
            <button
              onClick={() => { setResumeText("No resume"); navigate("/interview"); }}
              className="flex-1 py-3 border-2 border-cyan-500/50 text-cyan-300 font-bold rounded-xl hover:bg-cyan-500/20 hover:border-cyan-400 transition transform hover:scale-105"
            >
              Skip for Now
            </button>
            <button
              onClick={() => navigate("/build-resume")}
              className="flex-1 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-xl hover:from-cyan-400 hover:to-blue-500 transition transform hover:scale-105 shadow-lg"
            >
              Build Resume
            </button>
          </div>

          {/* Info Text */}
          <p className="text-center text-cyan-300/60 text-xs mt-6">
            Max file size: 5MB • PDF format only
          </p>
        </div>
      </div>
    </div>
  );
}