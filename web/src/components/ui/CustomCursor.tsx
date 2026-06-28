"use client";

import { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

export function CustomCursor() {
  const [isMounted, setIsMounted] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

  // Position for the glowing orb
  const cursorX = useMotionValue(-100);
  const cursorY = useMotionValue(-100);
  
  // Smooth spring physics for a fluid, floating feel
  const springConfig = { damping: 30, stiffness: 200, mass: 0.8 };
  const smoothX = useSpring(cursorX, springConfig);
  const smoothY = useSpring(cursorY, springConfig);

  useEffect(() => {
    setIsMounted(true);
    
    const moveCursor = (e: MouseEvent) => {
      // Offset by half the width/height (w-32 h-32 = 128px / 2 = 64)
      cursorX.set(e.clientX - 64);
      cursorY.set(e.clientY - 64);
    };

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName.toLowerCase() === "button" ||
        target.tagName.toLowerCase() === "a" ||
        target.closest("button") ||
        target.closest("a") ||
        target.classList.contains("interactive")
      ) {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };

    window.addEventListener("mousemove", moveCursor);
    window.addEventListener("mouseover", handleMouseOver);

    return () => {
      window.removeEventListener("mousemove", moveCursor);
      window.removeEventListener("mouseover", handleMouseOver);
    };
  }, [cursorX, cursorY]);

  if (!isMounted) return null;

  // Don't render on mobile/touch devices
  if (typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches) {
    return null;
  }

  return (
    <motion.div
      className="fixed top-0 left-0 w-32 h-32 rounded-full pointer-events-none z-[9999] mix-blend-screen flex items-center justify-center blur-[30px]"
      style={{ x: smoothX, y: smoothY }}
      animate={{
        scale: isHovering ? 1.5 : 1,
        backgroundColor: isHovering ? "rgba(167, 139, 250, 0.4)" : "rgba(139, 92, 246, 0.15)",
      }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    />
  );
}
