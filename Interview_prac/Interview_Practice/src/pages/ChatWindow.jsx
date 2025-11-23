import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useInterview } from "../utils/InterviewContext.jsx";
import { api } from "../api.js";
import QuestionDisplay from "../components/QuestionDisplay";
import InterviewerAvatar from "../components/InterviewerAvatar";
import Timer from "../components/Timer";
import { speak, playTypingSound, playDoneSound } from "../utils/audio";
import { analyzeSpeech } from "../utils/speech";

const ProgressBar = ({ progress }) => (
  <div className="w-full bg-gray-200 h-2 mt-2 rounded">
    <div className="bg-blue-600 h-2 transition-all duration-300 rounded" style={{ width: `${progress}%` }} />
  </div>
);

export default function ChatWindow() {
  const navigate = useNavigate();
  const { addMessage, chat, setScoreBreakdown, role, experience, difficulty, resumeText } = useInterview();
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [input, setInput] = useState("");
  const [progress, setProgress] = useState(15);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [conversationHistory, setConversationHistory] = useState(null);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(600);
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const recognitionRef = useRef(null);
  const scrollRef = useRef(null);
  const timerIntervalRef = useRef(null);

  useEffect(() => {
    const startInterview = async () => {
      try {
        setLoading(true);
        const newSessionId = `session_${Date.now()}`;
        setSessionId(newSessionId);
        const response = await api.post("/crew-interview-start", {
          session_id: newSessionId,
          role: role || "Software Engineer",
          experience: experience || "2-3",
          difficulty: difficulty || "Medium",
          resume_text: resumeText || ""
        });
        if (response.success && response.question) {
          setConversationHistory([{ role: "interviewer", content: response.question }]);
          const welcomeMsg = "Welcome! Lets start your mock interview.";
          setMessages([
            { sender: "bot", text: welcomeMsg },
            { sender: "bot", text: response.question }
          ]);
          addMessage("bot", welcomeMsg);
          setTimeout(() => speakQuestion(response.question), 500);
          setInterviewStarted(true);
        } else {
          throw new Error("Failed to start interview");
        }
      } catch (err) {
        console.error("Error starting interview:", err);
        setError("Failed to start interview. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    startInterview();
  }, [role, experience, difficulty, resumeText]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!interviewStarted) return;
    setIsInterviewActive(true);
    setTimeRemaining(600);
    timerIntervalRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timerIntervalRef.current);
          concludeInterview();
          return 0;
        }
        const percentageRemaining = ((prev - 1) / 600) * 100;
        setProgress(Math.max(15, percentageRemaining));
        return prev - 1;
      });
    }, 1000);
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [interviewStarted]);

  const concludeInterview = async () => {
    setIsInterviewActive(false);
    const conclusionMsg = "Thank you for completing the interview! Your time is up. Let me summarize your performance and provide final feedback.";
    setMessages(prev => [...prev, { sender: "bot", text: conclusionMsg }]);
    addMessage("bot", conclusionMsg);
    speakQuestion(conclusionMsg);
    try {
      const reportResponse = await api.post("/crew-interview-end", { session_id: sessionId });
      if (reportResponse.success && reportResponse.report) {
        localStorage.setItem("finalReport", JSON.stringify(reportResponse.report));
        localStorage.setItem("interviewSummary", JSON.stringify(reportResponse.summary));
        if (reportResponse.pdf_filename) {
          localStorage.setItem("pdfFilename", reportResponse.pdf_filename);
        }
      }
    } catch (err) {
      console.error("Error fetching final report:", err);
    }
    setTimeout(() => navigate("/summary"), 3000);
  };

  useEffect(() => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      console.error("Speech recognition not supported in this browser");
      return;
    }
    
    const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    const recog = new SpeechRecognition();
    
    recog.continuous = true;
    recog.interimResults = true;
    recog.lang = "en-US";
    
    recog.onstart = () => {
      console.log("Speech recognition started");
      setIsListening(true);
    };
    
    recog.onresult = (e) => {
      console.log("Speech recognition result received");
      let interimTranscript = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const transcript = e.results[i][0].transcript;
        if (e.results[i].isFinal) {
          console.log("Final transcript:", transcript);
          if (transcript.trim()) {
            handleUserResponse(transcript);
          }
        } else {
          interimTranscript += transcript;
        }
      }
    };
    
    recog.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      if (event.error !== "no-speech") {
        setIsListening(false);
      }
    };
    
    recog.onend = () => {
      console.log("Speech recognition ended");
    };
    
    recognitionRef.current = recog;
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [conversationHistory]);

  const speakQuestion = (text) => {
    setIsSpeaking(true);
    playTypingSound();
    speak(text, () => setIsSpeaking(false));
  };

  const handleUserResponse = async (text) => {
    const cleanText = text.trim();
    if (!cleanText) return;
    setMessages(prev => [...prev, { sender: "user", text: cleanText }]);
    addMessage("user", cleanText);
    const analysis = analyzeSpeech(cleanText);
    setScoreBreakdown(prev => ({
      ...prev,
      communication: Math.round((prev.communication + analysis.clarityScore) / 2),
      confidence: Math.round((prev.confidence + analysis.confidenceScore) / 2),
      fillerWords: Math.round((prev.fillerWords + (100 - analysis.fillerRatio * 100)) / 2)
    }));
    playDoneSound();
    
    // Add acknowledgment message
    const acknowledgments = [
      "That's a great answer!",
      "Nice, I like that perspective.",
      "Good explanation, thanks for sharing.",
      "Alright, that makes sense.",
      "Excellent point!",
      "I appreciate that insight.",
      "Well said!",
      "That's solid reasoning."
    ];
    const randomAck = acknowledgments[Math.floor(Math.random() * acknowledgments.length)];
    setMessages(prev => [...prev, { sender: "bot", text: randomAck }]);
    addMessage("bot", randomAck);
    speakQuestion(randomAck);
    
    setTimeout(async () => {
      try {
        const response = await api.post("/crew-interview-answer", {
          session_id: sessionId,
          role: role || "Software Engineer",
          experience: experience || "2-3",
          difficulty: difficulty || "Medium",
          resume_text: resumeText || "",
          user_message: cleanText,
          conversation_history: conversationHistory
        });
        if (response.success) {
          if (!isInterviewActive) return;
          const updatedHistory = [...conversationHistory, { role: "user", content: cleanText }];
          if (response.feedback) {
            setMessages(prev => [...prev, { sender: "bot", text: `Feedback: ${response.feedback}` }]);
            addMessage("bot", `Feedback: ${response.feedback}`);
          }
          if (response.score) {
            setMessages(prev => [...prev, { sender: "bot", text: `Score: ${response.score}/100` }]);
            addMessage("bot", `Score: ${response.score}/100`);
          }
          if (response.question) {
            updatedHistory.push({ role: "interviewer", content: response.question });
            setConversationHistory(updatedHistory);
            setMessages(prev => [...prev, { sender: "bot", text: response.question }]);
            addMessage("bot", response.question);
            speakQuestion(response.question);
          }
        }
      } catch (err) {
        console.error("Error getting next question:", err);
        setError("Failed to get next question. Please try again.");
      }
    }, 3000);
  };

  const sendText = () => {
    if (input.trim()) {
      handleUserResponse(input);
      setInput("");
    }
  };

  const startListening = () => {
    try {
      console.log("Starting speech recognition...");
      if (recognitionRef.current) {
        recognitionRef.current.start();
      } else {
        console.error("Recognition not initialized");
      }
    } catch (error) {
      console.error("Error starting speech recognition:", error);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    try {
      console.log("Stopping speech recognition...");
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
    } catch (error) {
      console.error("Error stopping speech recognition:", error);
    }
  };

  const endInterview = async () => {
    recognitionRef.current?.stop();
    try {
      if (!sessionId) {
        localStorage.setItem("finalReport", JSON.stringify({
          overall_assessment: "Interview completed",
          strengths: [],
          weak_areas: [],
          recommendations: []
        }));
        localStorage.setItem("interviewSummary", JSON.stringify({
          total_questions: messages.filter(m => m.sender === "bot").length,
          total_interactions: messages.length,
          average_score: 0,
          topics_covered: []
        }));
        navigate("/summary");
        return;
      }
      const response = await api.post("/crew-interview-end", { session_id: sessionId });
      if (response.report) {
        localStorage.setItem("finalReport", JSON.stringify(response.report));
      } else {
        localStorage.setItem("finalReport", JSON.stringify({
          overall_assessment: "Interview completed",
          strengths: [],
          weak_areas: [],
          recommendations: []
        }));
      }
      if (response.summary) {
        localStorage.setItem("interviewSummary", JSON.stringify(response.summary));
      } else {
        localStorage.setItem("interviewSummary", JSON.stringify({
          total_questions: messages.filter(m => m.sender === "bot").length,
          total_interactions: messages.length,
          average_score: 0,
          topics_covered: []
        }));
      }
      if (response.pdf_filename) {
        localStorage.setItem("pdfFilename", response.pdf_filename);
      }
    } catch (err) {
      console.error("Error ending interview:", err);
      localStorage.setItem("finalReport", JSON.stringify({
        overall_assessment: "Interview completed",
        strengths: [],
        weak_areas: [],
        recommendations: []
      }));
      localStorage.setItem("interviewSummary", JSON.stringify({
        total_questions: messages.filter(m => m.sender === "bot").length,
        total_interactions: messages.length,
        average_score: 0,
        topics_covered: []
      }));
    }
    navigate("/summary");
  };

  const currentQuestion = messages.filter(m => m.sender === "bot").pop()?.text || "";

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-400 mx-auto mb-6"></div>
          <h2 className="text-2xl font-bold mb-2">Generating Interview Questions...</h2>
          <p className="text-cyan-300">Preparing {role || "Software Engineer"} interview tailored to your experience level</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black text-white p-4 md:p-8">
      {error && (
        <div className="max-w-3xl mx-auto mb-4 bg-red-600/20 border border-red-500 rounded-lg p-4 text-red-200">
          {error}
        </div>
      )}
      <div className="max-w-3xl mx-auto">
        <ProgressBar progress={progress} />
      </div>
      <div className="max-w-3xl mx-auto mt-8 space-y-8">
        <div className="flex justify-center">
          <InterviewerAvatar isSpeaking={isSpeaking} size="large" />
        </div>
        <QuestionDisplay question={currentQuestion} />
        <div className="flex justify-center">
          <Timer initialMinutes={10} timeRemaining={timeRemaining} />
        </div>
        <div className="flex gap-3">
          <input
            className="flex-1 bg-white/20 border border-cyan-500/50 rounded-xl px-4 py-3 placeholder-cyan-200 focus:outline-none focus:border-cyan-300"
            placeholder="Type your answer here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendText()}
          />
          <button onClick={sendText} className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-medium transition">
            Send
          </button>
        </div>
        <div className="flex justify-center gap-4">
          <button
            onClick={startListening}
            disabled={isListening}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition ${isListening ? "bg-green-600 animate-pulse" : "bg-green-500 hover:bg-green-600"}`}
          >
            {isListening ? "Listening..." : "Start Mic"}
          </button>
          <button onClick={stopListening} disabled={!isListening} className="bg-yellow-500 hover:bg-yellow-600 px-6 py-3 rounded-xl font-medium transition">
            Stop Mic
          </button>
          <button onClick={endInterview} className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-xl font-medium transition">
            End Interview
          </button>
        </div>
      </div>
    </div>
  );
}
