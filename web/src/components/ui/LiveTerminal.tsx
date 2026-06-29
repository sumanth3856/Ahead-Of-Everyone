"use client";

import { useState, useEffect } from "react";
import { Terminal } from "lucide-react";
import { motion } from "framer-motion";
import { SpatialCard } from "@/components/ui/SpatialCard";

const LOGS = [
  "> Initializing intelligence pipeline...",
  "> Establishing secure connection to sources...",
  "> Scanning HackerNews, TechCrunch, ArXiv...",
  "> 12,453 new articles detected.",
  "> Filtering signal from noise...",
  "> Signal-to-noise ratio: 0.02%",
  "> Extracting core insights...",
  "> Synthesizing cross-references...",
  "> Compiling daily digest...",
  "> Finalizing premium magazine layout...",
  "> Broadcast ready. Awaiting command."
];

export function LiveTerminal() {
  const [logs, setLogs] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex >= LOGS.length) {
      const timeout = setTimeout(() => {
        setLogs([]);
        setCurrentIndex(0);
      }, 5000);
      return () => clearTimeout(timeout);
    }

    const delay = Math.random() * 800 + 400; // Random delay between 400ms and 1200ms
    const timer = setTimeout(() => {
      setLogs((prev) => [...prev, LOGS[currentIndex]]);
      setCurrentIndex((prev) => prev + 1);
    }, delay);

    return () => clearTimeout(timer);
  }, [currentIndex]);

  return (
    <SpatialCard depth={5} className="w-full max-w-lg mx-auto mt-16 rounded-xl border border-border-subtle bg-surface/80 overflow-hidden shadow-2xl backdrop-blur-xl">
      {/* Terminal Header */}
      <div className="flex items-center px-4 py-2 bg-surface border-b border-border-subtle">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500/80" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
          <div className="w-3 h-3 rounded-full bg-green-500/80" />
        </div>
        <div className="flex-1 flex justify-center items-center gap-2 text-muted">
          <Terminal size={14} />
          <span className="text-xs font-mono tracking-widest font-bold">pipeline_v2.sh</span>
        </div>
      </div>
      
      {/* Terminal Body */}
      <div className="p-4 h-48 overflow-y-auto font-mono text-sm flex flex-col gap-1 text-left bg-black/90">
        {logs.map((log, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className={`${i === LOGS.length - 1 ? 'text-green-400 font-bold' : 'text-brand-light'}`}
          >
            {log}
          </motion.div>
        ))}
        {currentIndex < LOGS.length && (
          <motion.div 
            animate={{ opacity: [1, 0] }}
            transition={{ repeat: Infinity, duration: 0.8 }}
            className="w-2 h-4 bg-brand-light mt-1"
          />
        )}
      </div>
    </SpatialCard>
  );
}
