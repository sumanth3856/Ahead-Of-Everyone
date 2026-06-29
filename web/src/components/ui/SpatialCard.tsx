"use client";

import { useRef, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform, useMotionTemplate, HTMLMotionProps } from "framer-motion";

interface SpatialCardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  depth?: number;
}

export function SpatialCard({ children, className = "", depth = 10, ...props }: SpatialCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const rectRef = useRef<DOMRect | null>(null);
  
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const [isHovered, setIsHovered] = useState(false);

  // Smooth out the tilt with springs for premium feel
  const springConfig = { damping: 20, stiffness: 150 };
  const smoothX = useSpring(x, springConfig);
  const smoothY = useSpring(y, springConfig);

  const rotateX = useTransform(smoothY, [-0.5, 0.5], [depth, -depth]);
  const rotateY = useTransform(smoothX, [-0.5, 0.5], [-depth, depth]);

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    if (!ref.current || !rectRef.current) return;
    const rect = rectRef.current;
    
    // Normalize coordinates from -0.5 to 0.5
    const width = rect.width;
    const height = rect.height;
    
    const mouseXPos = e.clientX - rect.left;
    const mouseYPos = e.clientY - rect.top;

    const xPct = mouseXPos / width - 0.5;
    const yPct = mouseYPos / height - 0.5;

    x.set(xPct);
    y.set(yPct);
    
    // For spotlight
    mouseX.set(mouseXPos);
    mouseY.set(mouseYPos);
  }

  function handleMouseEnter() {
    setIsHovered(true);
    if (ref.current) {
      rectRef.current = ref.current.getBoundingClientRect();
    }
  }

  function handleMouseLeave() {
    setIsHovered(false);
    rectRef.current = null;
    x.set(0);
    y.set(0);
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX,
        rotateY,
      }}
      className={`glass relative group transition-shadow duration-500 ${
        isHovered ? "shadow-spatial" : "shadow-sm"
      } ${className}`}
      {...props}
    >
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-3xl opacity-0 transition duration-500 group-hover:opacity-100 z-0"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              600px circle at ${mouseX}px ${mouseY}px,
              var(--color-brand-glow),
              transparent 80%
            )
          `,
        }}
      />
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

