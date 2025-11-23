import React, { useState, useEffect } from "react";

export default function Timer({ initialMinutes = 5, timeRemaining = null }) {
  const [seconds, setSeconds] = useState(initialMinutes * 60);

  // Use passed timeRemaining if provided, otherwise count up
  useEffect(() => {
    if (timeRemaining !== null) {
      setSeconds(timeRemaining);
    } else {
      const interval = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timeRemaining]);

  // Convert seconds → MM:SS
  const formatTime = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;

    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  // Determine color based on time remaining
  const getTimeColor = () => {
    if (timeRemaining === null) return "text-gray-700";
    if (timeRemaining <= 60) return "text-red-500 font-bold animate-pulse";
    if (timeRemaining <= 180) return "text-yellow-500 font-semibold";
    return "text-green-500 font-semibold";
  };

  return (
    <div className="flex items-center gap-2 mt-3">
      <span className={`text-lg font-semibold ${getTimeColor()}`}>
        ⏱ Time Remaining: {formatTime(seconds)}
      </span>
    </div>
  );
}
