"use client";

import { m as motion, HTMLMotionProps } from "framer-motion";

interface SpatialCardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  depth?: number; // kept for compatibility
}

export function SpatialCard({ children, className = "", depth = 10, ...props }: SpatialCardProps) {
  return (
    <motion.div
      className={`glass relative shadow-sm ${className}`}
      {...props}
    >
      {/* Deep inner shadow to emphasize 3D */}
      <div className="absolute inset-0 rounded-3xl pointer-events-none" style={{ boxShadow: "var(--spatial-inset)" }} />
      
      {/* Noise Texture Overlay */}
      <div className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none mix-blend-overlay noise-bg rounded-3xl" />
      
      <div className="relative w-full h-full">
        {children}
      </div>
    </motion.div>
  );
}
