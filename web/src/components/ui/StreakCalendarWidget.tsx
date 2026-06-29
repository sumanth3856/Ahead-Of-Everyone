"use client";

import { useState, useEffect } from "react";
import { SpatialCard } from "./SpatialCard";
import { Calendar } from "lucide-react";
import { motion } from "framer-motion";

export function StreakCalendarWidget() {
  const [days, setDays] = useState<{date: Date, read: boolean}[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const today = new Date();
    const generatedDays = Array.from({ length: 30 }, (_, i) => {
      const d = new Date(today);
      d.setDate(d.getDate() - (29 - i));
      const read = Math.random() > 0.3;
      return { date: d, read };
    });
    setDays(generatedDays);
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle flex flex-col shadow-sm min-h-[250px]">
        <div className="flex items-center gap-3 mb-2">
          <Calendar className="h-5 w-5 text-brand" />
          <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Reading Activity</h3>
        </div>
        <p className="text-xs text-brand font-semibold mb-6">Current Streak: 4 Days 🔥</p>
        <div className="flex-1 flex items-center justify-center">
           <div className="w-6 h-6 border-2 border-brand border-t-transparent rounded-full animate-spin"></div>
        </div>
      </SpatialCard>
    );
  }

  return (
    <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle flex flex-col shadow-sm">
      <div className="flex items-center gap-3 mb-2">
        <Calendar className="h-5 w-5 text-brand" />
        <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Reading Activity</h3>
      </div>
      <p className="text-xs text-brand font-semibold mb-6">Current Streak: 4 Days 🔥</p>
      
      <div className="flex-1 w-full relative z-10 flex flex-col justify-end pb-4">
        <div className="grid grid-cols-7 gap-2">
          {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, i) => (
            <div key={i} className="text-[10px] font-bold text-muted text-center">{day}</div>
          ))}
          {/* Empty slots for month start alignment (simplified) */}
          {Array.from({ length: days[0].date.getDay() }).map((_, i) => (
            <div key={`empty-${i}`} className="aspect-square rounded-md bg-transparent" />
          ))}
          {days.map((day, i) => (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.02, type: "spring", stiffness: 300, damping: 20 }}
              key={i}
              className={`aspect-square rounded-md ${day.read ? "bg-brand shadow-[0_0_10px_rgba(139,92,246,0.5)]" : "bg-surface-hover border border-border-subtle"}`}
              title={day.date.toDateString()}
            />
          ))}
        </div>
      </div>
    </SpatialCard>
  );
}
