"use client";

import { m as motion, useScroll } from "framer-motion";

export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  
  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-1 bg-brand origin-left z-50 shadow-[0_0_15px_rgba(139,92,246,0.8)]"
      style={{ scaleX: scrollYProgress }}
    />
  );
}
