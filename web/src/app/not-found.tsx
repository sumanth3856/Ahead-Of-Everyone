"use client";

import Link from "next/link";
import { TerminalSquare, ShieldAlert } from "lucide-react";
import { SpatialCard } from "@/components/ui/SpatialCard";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand/5 blur-[120px] rounded-full pointer-events-none" />
      
      <SpatialCard depth={10} className="glass rounded-[2rem] p-8 md:p-12 max-w-lg w-full text-center border border-border-subtle shadow-2xl relative z-10">
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="absolute inset-0 bg-brand/20 blur-xl rounded-full" />
            <ShieldAlert className="h-20 w-20 text-brand relative z-10" />
          </div>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-bold tracking-widest text-foreground uppercase mb-2">
          404
        </h1>
        <h2 className="text-xl md:text-2xl font-bold text-foreground mb-4">
          Page Not Found
        </h2>
        
        <p className="text-muted text-sm md:text-base mb-8">
          The requested intel could not be located in our systems. The pipeline might have been rerouted or the link is classified.
        </p>
        
        <Link 
          href="/dashboard"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-brand text-white font-bold tracking-wide hover:opacity-90 transition-opacity"
        >
          <TerminalSquare className="h-5 w-5" />
          Return to Dashboard
        </Link>
      </SpatialCard>
    </div>
  );
}
