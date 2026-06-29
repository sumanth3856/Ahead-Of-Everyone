"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCcw, Home } from "lucide-react";

// Global error must define its own HTML and Body tags
export default function GlobalError({
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
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-[#0a0f1d] text-[#f7fafc] font-sans">
        <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
          {/* Background glow effects */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-500/10 blur-[120px] rounded-full pointer-events-none" />
          
          <div className="bg-[#1a202c]/50 backdrop-blur-xl rounded-[2rem] p-8 md:p-12 max-w-lg w-full text-center border border-red-500/20 shadow-2xl relative z-10">
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-red-500/20 blur-xl rounded-full" />
                <AlertTriangle className="h-20 w-20 text-red-500 relative z-10" />
              </div>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold tracking-widest uppercase mb-2">
              CRITICAL FAILURE
            </h1>
            
            <p className="text-[#a0aec0] text-sm md:text-base mb-8">
              A catastrophic layout error occurred. Our systems are attempting to recover.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={handleRetry}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-[#2d3748] border border-[#4a5568]/30 text-white font-bold tracking-wide hover:bg-[#4a5568] transition-colors cursor-pointer"
              >
                <RefreshCcw className="h-5 w-5" />
                Attempt Recovery
              </button>
              
              <button
                onClick={handleGoHome}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-[#22c55e] text-white font-bold tracking-wide hover:opacity-90 transition-opacity cursor-pointer"
              >
                <Home className="h-5 w-5" />
                Go Home
              </button>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
