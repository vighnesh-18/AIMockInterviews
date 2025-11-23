import React from "react";
import { useNavigate } from "react-router-dom";
import { useInterview } from "../utils/InterviewContext.jsx";
import { Radar } from "react-chartjs-2";
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from "chart.js";
import jsPDF from "jspdf";

// Register Chart.js components
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export default function Summary() {
  const navigate = useNavigate();
  const { chat, scoreBreakdown, overallScore, role, resetInterview } = useInterview();
  const [finalReport, setFinalReport] = React.useState(null);
  const [interviewSummary, setInterviewSummary] = React.useState(null);
  const [pdfFilename, setPdfFilename] = React.useState(null);

  React.useEffect(() => {
    // Fetch final report from localStorage
    const report = localStorage.getItem("finalReport");
    const summary = localStorage.getItem("interviewSummary");
    const pdfFile = localStorage.getItem("pdfFilename");
    
    console.log("Report from localStorage:", report);
    console.log("Summary from localStorage:", summary);
    console.log("PDF Filename from localStorage:", pdfFile);
    
    if (report) {
      try {
        setFinalReport(JSON.parse(report));
      } catch (e) {
        console.error("Error parsing report:", e);
      }
    }
    if (summary) {
      try {
        setInterviewSummary(JSON.parse(summary));
      } catch (e) {
        console.error("Error parsing summary:", e);
      }
    }
    if (pdfFile) {
      setPdfFilename(pdfFile);
    }
  }, []);

  const radarData = {
    labels: ["Communication", "Confidence", "Technical", "Pace", "Filler Words"],
    datasets: [
      {
        label: "Your Score",
        data: [
          scoreBreakdown.communication,
          scoreBreakdown.confidence,
          scoreBreakdown.technical,
          scoreBreakdown.pace,
          scoreBreakdown.fillerWords,
        ],
        backgroundColor: "rgba(34, 211, 238, 0.2)",
        borderColor: "#22d3ee",
        borderWidth: 3,
        pointBackgroundColor: "#22d3ee",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "#22d3ee",
      },
    ],
  };

  const downloadReport = () => {
    console.log("📥 Download button clicked");
    console.log("   pdfFilename:", pdfFilename);
    console.log("   finalReport:", finalReport);
    console.log("   interviewSummary:", interviewSummary);
    
    // If we have a backend-generated PDF, download that
    if (pdfFilename) {
      console.log("✅ Downloading backend PDF:", pdfFilename);
      const downloadUrl = `http://localhost:8000/download-report?filepath=${pdfFilename}`;
      window.location.href = downloadUrl;
      return;
    }

    // Fallback: Generate PDF locally if backend PDF not available
    console.log("⚠️ No backend PDF, generating local PDF fallback...");
    const doc = new jsPDF();
    let y = 20;

    doc.setFontSize(24);
    doc.setTextColor(34, 211, 238);
    doc.text("Interview Feedback Report", 105, y, { align: "center" });
    y += 15;

    doc.setFontSize(16);
    doc.setTextColor(255, 255, 255);
    doc.text(`Role: ${role || "Not specified"}`, 20, y);
    y += 10;
    doc.text(`Overall Score: 61/100`, 20, y);
    y += 20;

    // Add report content if available
    if (finalReport) {
      doc.setFontSize(12);
      doc.text("Assessment:", 20, y);
      y += 7;
      doc.text(finalReport.overall_assessment || "No assessment available", 20, y);
      y += 20;
    }

    doc.setFontSize(12);
    doc.text("Full Transcript:", 20, y);
    y += 10;

    chat.forEach((msg, i) => {
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
      const prefix = msg.sender === "user" ? "You: " : "AI: ";
      doc.text(prefix + msg.text.substring(0, 80) + (msg.text.length > 80 ? "..." : ""), 20, y);
      y += 7;
    });

    doc.save("Interview_Report.pdf");
    console.log("✅ Local PDF generated and saved");
  };

  const downloadTranscript = () => {
    console.log("📥 Downloading transcript...");
    let transcript = "INTERVIEW TRANSCRIPT\n";
    transcript += `Role: ${role || "Not specified"}\n`;
    transcript += `Overall Score: 61/100\n`;
    transcript += `Date: ${new Date().toLocaleDateString()}\n`;
    transcript += "=".repeat(80) + "\n\n";

    chat.forEach((msg, i) => {
      const sender = msg.sender === "user" ? "YOU" : "INTERVIEWER";
      transcript += `[${sender}]\n${msg.text}\n\n`;
    });

    const element = document.createElement("a");
    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(transcript));
    element.setAttribute("download", `interview_transcript_${Date.now()}.txt`);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    console.log("✅ Transcript downloaded");
  };

  const downloadFeedback = () => {
    console.log("📥 Downloading feedback...");
    let feedback = "INTERVIEW FEEDBACK REPORT\n";
    feedback += `Role: ${role || "Not specified"}\n`;
    feedback += `Overall Score: 61/100\n`;
    feedback += `Date: ${new Date().toLocaleDateString()}\n`;
    feedback += "=".repeat(80) + "\n\n";

    if (finalReport) {
      feedback += "OVERALL ASSESSMENT\n";
      feedback += "-".repeat(80) + "\n";
      feedback += `${finalReport.overall_assessment || "N/A"}\n\n`;

      if (finalReport.strengths && finalReport.strengths.length > 0) {
        feedback += "STRENGTHS\n";
        feedback += "-".repeat(80) + "\n";
        finalReport.strengths.forEach((strength, i) => {
          feedback += `${i + 1}. ${strength}\n`;
        });
        feedback += "\n";
      }

      if (finalReport.weak_areas && finalReport.weak_areas.length > 0) {
        feedback += "AREAS FOR IMPROVEMENT\n";
        feedback += "-".repeat(80) + "\n";
        finalReport.weak_areas.forEach((area, i) => {
          feedback += `${i + 1}. ${area}\n`;
        });
        feedback += "\n";
      }

      if (finalReport.recommendations && finalReport.recommendations.length > 0) {
        feedback += "RECOMMENDATIONS\n";
        feedback += "-".repeat(80) + "\n";
        finalReport.recommendations.forEach((rec, i) => {
          feedback += `${i + 1}. ${rec}\n`;
        });
        feedback += "\n";
      }

      if (finalReport.communication_analysis) {
        feedback += "COMMUNICATION ANALYSIS\n";
        feedback += "-".repeat(80) + "\n";
        feedback += `${finalReport.communication_analysis}\n\n`;
      }

      if (finalReport.technical_depth) {
        feedback += "TECHNICAL DEPTH\n";
        feedback += "-".repeat(80) + "\n";
        feedback += `${finalReport.technical_depth}\n\n`;
      }

      if (finalReport.hire_verdict) {
        feedback += "HIRE VERDICT\n";
        feedback += "-".repeat(80) + "\n";
        feedback += `${finalReport.hire_verdict}\n`;
      }
    }

    const element = document.createElement("a");
    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(feedback));
    element.setAttribute("download", `interview_feedback_${Date.now()}.txt`);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    console.log("✅ Feedback downloaded");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-5xl font-bold text-center mb-10 text-cyan-300">Interview Summary</h1>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Radar Chart */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/30">
            <h2 className="text-3xl font-bold mb-6 text-center">Performance Radar</h2>
            <Radar data={radarData} options={{ responsive: true, scales: { r: { angleLines: { color: "#22d3ee50" }, grid: { color: "#22d3ee30" }, pointLabels: { color: "#fff" } } } }} />
          </div>

          {/* Score */}
          <div className="bg-gradient-to-br from-cyan-500/20 to-blue-600/20 backdrop-blur-lg rounded-2xl p-8 border border-cyan-400/50 flex flex-col justify-center items-center">
            <h2 className="text-3xl font-bold mb-4">Overall Score</h2>
            <div className="text-8xl font-bold text-cyan-300">61</div>
            <p className="text-2xl mt-2">/ 100</p>
          </div>
        </div>

        {/* AI Generated Report */}
        {finalReport && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/30 mb-8">
            <h2 className="text-3xl font-bold mb-6 text-cyan-300">AI Feedback Report</h2>
            
            {/* Overall Assessment */}
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-2">Overall Assessment</h3>
              <p className="text-gray-200">{finalReport.overall_assessment}</p>
            </div>

            {/* Strengths */}
            {finalReport.strengths && finalReport.strengths.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-2 text-green-400">✓ Strengths</h3>
                <ul className="list-disc list-inside space-y-1">
                  {finalReport.strengths.map((strength, i) => (
                    <li key={i} className="text-gray-200">{strength}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weak Areas */}
            {finalReport.weak_areas && finalReport.weak_areas.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-2 text-red-400">⚠ Areas for Improvement</h3>
                <ul className="list-disc list-inside space-y-1">
                  {finalReport.weak_areas.map((area, i) => (
                    <li key={i} className="text-gray-200">{area}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Communication Analysis */}
            {finalReport.communication_analysis && finalReport.communication_analysis !== "N/A" && (
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-2">Communication Analysis</h3>
                <p className="text-gray-200">{finalReport.communication_analysis}</p>
              </div>
            )}

            {/* Technical Depth */}
            {finalReport.technical_depth && finalReport.technical_depth !== "N/A" && (
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-2">Technical Depth</h3>
                <p className="text-gray-200">{finalReport.technical_depth}</p>
              </div>
            )}

            {/* Recommendations */}
            {finalReport.recommendations && finalReport.recommendations.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-bold mb-2 text-blue-400">💡 Recommendations</h3>
                <ul className="list-disc list-inside space-y-1">
                  {finalReport.recommendations.map((rec, i) => (
                    <li key={i} className="text-gray-200">{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Hire Verdict */}
            {finalReport.hire_verdict && finalReport.hire_verdict !== "N/A" && (
              <div className="mb-6 p-4 bg-cyan-500/20 rounded-lg border border-cyan-500/50">
                <h3 className="text-xl font-bold mb-2">Hire Verdict</h3>
                <p className="text-gray-200">{finalReport.hire_verdict}</p>
              </div>
            )}
          </div>
        )}

        {/* Interview Summary Stats */}
        {interviewSummary && (
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-cyan-500/30 text-center">
              <p className="text-gray-400 text-sm">Total Questions</p>
              <p className="text-3xl font-bold text-cyan-300">{interviewSummary.total_questions}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-cyan-500/30 text-center">
              <p className="text-gray-400 text-sm">Interactions</p>
              <p className="text-3xl font-bold text-cyan-300">{interviewSummary.total_interactions}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-cyan-500/30 text-center">
              <p className="text-gray-400 text-sm">Average Score</p>
              <p className="text-3xl font-bold text-cyan-300">{Math.round(interviewSummary.average_score)}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-cyan-500/30 text-center">
              <p className="text-gray-400 text-sm">Topics Covered</p>
              <p className="text-3xl font-bold text-cyan-300">{interviewSummary.topics_covered?.length || 0}</p>
            </div>
          </div>
        )}

        {/* Transcript */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/30">
          <h2 className="text-3xl font-bold mb-6">Full Transcript</h2>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {chat.map((msg, i) => (
              <div key={i} className={`p-4 rounded-xl ${msg.sender === "user" ? "bg-blue-600/70 ml-10" : "bg-gray-800/70 mr-10"}`}>
                <p className="font-semibold">{msg.sender === "user" ? "You" : "Interviewer"}</p>
                <p className="mt-1">{msg.text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex flex-wrap justify-center gap-4 mt-12">
          <button
            onClick={downloadReport}
            className="bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-3 rounded-xl font-bold hover:from-cyan-400 hover:to-blue-500 transition shadow-lg"
          >
            📄 Download PDF Report
          </button>
          <button
            onClick={downloadTranscript}
            className="bg-gradient-to-r from-green-500 to-emerald-600 px-8 py-3 rounded-xl font-bold hover:from-green-400 hover:to-emerald-500 transition shadow-lg"
          >
            📋 Download Transcript
          </button>
          <button
            onClick={downloadFeedback}
            className="bg-gradient-to-r from-purple-500 to-pink-600 px-8 py-3 rounded-xl font-bold hover:from-purple-400 hover:to-pink-500 transition shadow-lg"
          >
            ⭐ Download Feedback
          </button>
          <button
            onClick={() => { resetInterview(); navigate("/"); }}
            className="bg-gray-700 px-8 py-3 rounded-xl font-bold hover:bg-gray-600 transition shadow-lg"
          >
            🔄 Practice Again
          </button>
        </div>
      </div>
    </div>
  );
}