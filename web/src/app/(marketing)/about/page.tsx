"use client";

import Image from "next/image";
import { m as motion, Variants } from "framer-motion";
import { SpatialCard } from "@/components/ui/SpatialCard";

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
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: ("easeOut" as any) } },
  };

  return (
    <div className="relative overflow-hidden bg-background min-h-screen">
      {/* 3D Wireframe Background Element */}
      <div className="absolute top-0 right-0 -z-10 w-[800px] h-[800px] pointer-events-none perspective-[1000px]">
        <motion.div 
          animate={{ rotateX: 360, rotateY: 180, rotateZ: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          className="w-full h-full rounded-full border border-brand/5"
          style={{ transformStyle: "preserve-3d", transform: "translateZ(-200px) translateX(200px) translateY(-200px)" }}
        />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand/10 blur-[100px] rounded-full" />
      </div>

      <motion.div 
        initial="hidden"
        animate="show"
        variants={containerVariants}
        className="pt-24 pb-12 sm:pt-28 sm:pb-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 perspective-[1200px]"
      >
        <motion.div variants={itemVariants} className="mb-8 sm:mb-12 text-center sm:text-left">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-4 sm:mb-6 leading-tight text-foreground">
            The <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light text-glow block sm:inline mt-2 sm:mt-0">Philosophy</span>
          </h1>
          <p className="text-lg sm:text-xl text-muted leading-relaxed max-w-2xl sm:mx-0 mx-auto font-light">
            In an era of information overload, speed and signal-to-noise ratio are the ultimate competitive advantages. 
          </p>
        </motion.div>

        <motion.div variants={itemVariants} className="mb-8 sm:mb-12 transform-style-3d">
          <SpatialCard depth={10} className="rounded-[2.5rem] p-8 sm:p-12 border border-border-subtle shadow-sm">
            <h2 className="text-2xl sm:text-3xl font-bold mb-6 text-foreground tracking-wide leading-tight">
              Five minutes.<br className="sm:hidden" /> Then you are ahead of everyone.
            </h2>
            
            <div className="space-y-6 text-muted leading-relaxed text-sm sm:text-base font-light">
              <p>
                The tech industry moves at breakneck speed. Every day, thousands of articles, press releases, and HackerNews threads are generated. Reading them all is impossible. Missing them is a liability.
              </p>
              <p>
                <strong>Ahead Of Everyone</strong> was built as an autonomous solution to this problem. Our core pipeline operates 100% serverlessly. It scrapes the global tech news ecosystem every 24 hours and feeds the raw data into a Multi-Model AI Cascade.
              </p>
              <p>
                The AI acts as an elite editorial team, stripping away the fluff and synthesizing the pure signal into a premium magazine.
              </p>
            </div>
          </SpatialCard>
        </motion.div>

        <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
          <motion.div variants={itemVariants} className="transform-style-3d">
            <SpatialCard depth={15} className="h-full rounded-[2.5rem] p-8 border border-border-subtle group">
              <div className="absolute top-0 right-0 w-24 h-24 bg-surface-hover rounded-bl-[2.5rem] -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
              <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Zero Maintenance</h3>
              <p className="text-muted text-sm sm:text-base leading-relaxed font-light">
                The architecture is designed to run indefinitely without human intervention. Automated cron schedules, fallback LLM routing, and resilient database queries ensure the newsletter keeps flowing.
              </p>
            </SpatialCard>
          </motion.div>
        
          <motion.div variants={itemVariants} className="transform-style-3d">
            <SpatialCard depth={15} className="h-full rounded-[2.5rem] p-8 border border-border-subtle group">
              <div className="absolute top-0 right-0 w-24 h-24 bg-surface-hover rounded-bl-[2.5rem] -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
              <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Absolute Privacy</h3>
              <p className="text-muted text-sm sm:text-base leading-relaxed font-light">
                Your data is your own. The service runs directly to your secure Telegram client. No middlemen, no tracking, just pure signal.
              </p>
            </SpatialCard>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
}
