"use client";

import { useState, useEffect } from "react";
import { SpatialCard } from "./SpatialCard";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { Activity } from "lucide-react";

const data = [
  { subject: "AI & ML", A: 120, fullMark: 150 },
  { subject: "Hardware", A: 98, fullMark: 150 },
  { subject: "Software Dev", A: 86, fullMark: 150 },
  { subject: "Security", A: 99, fullMark: 150 },
  { subject: "Business", A: 85, fullMark: 150 },
  { subject: "Web3", A: 65, fullMark: 150 },
];

export function RadarChartWidget() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle flex flex-col shadow-sm min-h-[300px]">
        <div className="flex items-center gap-3 mb-2">
          <Activity className="h-5 w-5 text-brand" />
          <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Interest Radar</h3>
        </div>
        <p className="text-xs text-brand font-semibold mb-6">Topics extracted from your reads</p>
        <div className="flex-1 flex items-center justify-center">
           <div className="w-6 h-6 border-2 border-brand border-t-transparent rounded-full animate-spin"></div>
        </div>
      </SpatialCard>
    );
  }

  return (
    <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle flex flex-col shadow-sm min-h-[300px]">
      <div className="flex items-center gap-3 mb-2">
        <Activity className="h-5 w-5 text-brand" />
        <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Interest Radar</h3>
      </div>
      <p className="text-xs text-brand font-semibold mb-6">Topics extracted from your reads</p>
      
      <div className="flex-1 w-full min-h-[200px] relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
            <PolarGrid stroke="rgba(139, 92, 246, 0.2)" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: "var(--foreground)", fontSize: 10, fontWeight: 700 }} />
            <Radar
              name="Interests"
              dataKey="A"
              stroke="var(--color-brand)"
              fill="var(--color-brand)"
              fillOpacity={0.3}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </SpatialCard>
  );
}
