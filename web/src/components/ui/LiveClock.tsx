"use client";

import { useState, useEffect } from "react";
import { Clock } from "lucide-react";

export function LiveClock() {
  const [time, setTime] = useState<Date | null>(null);

  useEffect(() => {
    setTime(new Date());
    const interval = setInterval(() => {
      setTime(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!time) {
    // Prevent hydration mismatch by rendering a placeholder matching the size
    return <div className="h-4 w-32 animate-pulse bg-surface rounded"></div>;
  }

  const formattedDate = time.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  const formattedTime = time.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <div className="flex items-center gap-2 text-muted text-sm font-medium">
      <Clock className="w-4 h-4 text-brand" />
      <span>{formattedDate} • {formattedTime}</span>
    </div>
  );
}
