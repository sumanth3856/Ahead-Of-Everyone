"use client";

import { motion, useScroll } from "framer-motion";

export default function Template({ children }: { children: React.ReactNode }) {
  const { scrollYProgress } = useScroll();
  
  return (
    <>
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-brand origin-left z-50 shadow-[0_0_15px_rgba(139,92,246,0.8)]"
        style={{ scaleX: scrollYProgress }}
      />
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="flex-1 flex flex-col"
      >
        {children}
      </motion.div>
    </>
  );
}
