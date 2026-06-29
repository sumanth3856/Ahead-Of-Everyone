"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCcw, Home } from "lucide-react";
import { SpatialCard } from "@/components/ui/SpatialCard";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  const handleRetry = () => {
    try {
      reset();
    } catch {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-500/10 blur-[120px] rounded-full pointer-events-none" />
      
      <SpatialCard depth={10} className="glass rounded-[2rem] p-8 md:p-12 max-w-lg w-full text-center border border-red-500/20 shadow-2xl relative z-10">
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="absolute inset-0 bg-red-500/20 blur-xl rounded-full" />
            <AlertTriangle className="h-20 w-20 text-red-500 relative z-10" />
          </div>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold tracking-widest text-foreground uppercase mb-2">
          500
        </h1>
        <h2 className="text-xl md:text-2xl font-bold text-foreground mb-4">
          Internal Server Error
        </h2>
        
        <p className="text-muted text-sm md:text-base mb-8">
          A critical failure occurred in the intelligence pipeline. Our technicians have been notified. Please try again.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={handleRetry}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-surface border border-border-subtle text-foreground font-bold tracking-wide hover:bg-surface-hover transition-colors cursor-pointer"
          >
            <RefreshCcw className="h-5 w-5" />
            Try Again
          </button>
          
          <button 
            onClick={handleGoHome}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-brand text-white font-bold tracking-wide hover:opacity-90 transition-opacity cursor-pointer"
          >
            <Home className="h-5 w-5" />
            Go Home
          </button>
        </div>
      </SpatialCard>
    </div>
  );
}
