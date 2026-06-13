"use client";

import Image from "next/image";
import { motion, Variants } from "framer-motion";

export default function AboutPage() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <motion.div 
      initial="hidden"
      animate="show"
      variants={containerVariants}
      className="pt-24 pb-16 sm:pt-32 sm:pb-24 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 overflow-hidden"
    >
      <motion.div variants={itemVariants} className="mb-12 sm:mb-16 text-center sm:text-left">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-4 sm:mb-6 leading-tight">
          The <span className="text-brand text-glow block sm:inline mt-2 sm:mt-0">Philosophy</span>
        </h1>
        <p className="text-lg sm:text-xl text-muted leading-relaxed max-w-2xl sm:mx-0 mx-auto">
          In an era of information overload, speed and signal-to-noise ratio are the ultimate competitive advantages. 
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="glass rounded-3xl p-6 sm:p-8 md:p-12 border border-brand/20 shadow-[0_0_40px_rgba(113,27,209,0.05)] relative overflow-hidden mb-12 sm:mb-16 group hover:border-brand/40 transition-colors duration-500">
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-brand/20 rounded-full blur-[80px] -z-10 group-hover:bg-brand/30 transition-colors duration-700" />
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-brand/10 rounded-full blur-[80px] -z-10" />
        
        <h2 className="text-2xl sm:text-3xl font-bold mb-6 text-foreground tracking-wide leading-tight">
          Five minutes.<br className="sm:hidden" /> Then you are ahead of everyone.
        </h2>
        
        <div className="space-y-6 text-muted leading-relaxed text-sm sm:text-base">
          <p>
            The tech industry moves at breakneck speed. Every day, thousands of articles, press releases, and HackerNews threads are generated. Reading them all is impossible. Missing them is a liability.
          </p>
          <p>
            <strong>Ahead Of Everyone</strong> was built as an autonomous solution to this problem. Our core pipeline operates 100% serverlessly. It scrapes the global tech news ecosystem every 24 hours and feeds the raw data into a Multi-Model AI Cascade.
          </p>
          <p>
            The AI acts as an elite editorial team, stripping away the fluff and synthesizing the pure signal into a premium, dark-mode magazine.
          </p>
        </div>
      </motion.div>

      <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
        <motion.div variants={itemVariants} className="glass rounded-3xl p-6 sm:p-8 border border-white/5 relative overflow-hidden group hover:border-brand/30 transition-all duration-500">
          <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 rounded-bl-full -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
          <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Zero Maintenance</h3>
          <p className="text-muted text-sm sm:text-base leading-relaxed">
            The architecture is designed to run indefinitely without human intervention. Automated cron schedules, fallback LLM routing, and resilient database queries ensure the intelligence keeps flowing.
          </p>
        </motion.div>
        
        <motion.div variants={itemVariants} className="glass rounded-3xl p-6 sm:p-8 border border-white/5 relative overflow-hidden group hover:border-brand/30 transition-all duration-500">
          <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 rounded-bl-full -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
          <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Premium UX</h3>
          <p className="text-muted text-sm sm:text-base leading-relaxed">
            We believe data shouldn't just be accurate; it should be beautiful. From our custom PDF generation engine using Montserrat typography, to this very web interface.
          </p>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
