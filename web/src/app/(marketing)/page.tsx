"use client";

import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Zap, Database, Cpu, Shield, Globe } from "lucide-react";
import { motion, useScroll, useTransform } from "framer-motion";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { useRef } from "react";

export default function Home() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  // Parallax effects
  const yBg = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const yText = useTransform(scrollYProgress, [0, 1], ["0%", "-50%"]);
  const opacityText = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  const staggerContainer = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
      },
    },
  };

  const fadeUp = {
    hidden: { opacity: 0, y: 50 },
    show: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" as any } },
  };

  return (
    <div ref={containerRef} className="flex flex-col items-center overflow-hidden bg-background">
      
      {/* Immersive 3D Hero Section */}
      <section className="relative w-full h-[100svh] flex items-center justify-center perspective-[1200px] transform-style-3d">
        
        {/* Parallax Background Orb */}
        <motion.div 
          className="absolute inset-0 w-full h-full -z-20 pointer-events-none flex items-center justify-center"
          style={{ y: yBg }}
        >
           <div className="relative w-[400px] h-[400px] sm:w-[600px] sm:h-[600px] transform-style-3d" style={{ transform: "translateZ(-150px)" }}>
             {/* Orbital Rings */}
             <motion.div 
               animate={{ rotateX: 360, rotateY: 180, rotateZ: 360 }}
               transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
               className="absolute inset-0 rounded-full border-[1px] border-brand/20 shadow-[inset_0_0_60px_rgba(139,92,246,0.1)]"
             />
             <motion.div 
               animate={{ rotateX: -360, rotateY: 360, rotateZ: -180 }}
               transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
               className="absolute inset-4 rounded-full border-[1px] border-brand-light/20"
             />
             {/* Glowing Core */}
             <motion.div 
                animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.3, 0.7, 0.3] }}
                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                className="absolute top-1/4 left-1/4 right-1/4 bottom-1/4 rounded-full bg-brand blur-[80px]"
             />
             <motion.div 
                animate={{ scale: [1, 1.5, 1], opacity: [0.1, 0.4, 0.1] }}
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                className="absolute top-1/4 left-1/4 right-1/4 bottom-1/4 rounded-full bg-foreground blur-[100px]"
             />
           </div>
        </motion.div>

        {/* Foreground Content with Parallax */}
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          style={{ y: yText, opacity: opacityText, transform: "translateZ(100px)" }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center w-full"
        >
          <motion.div variants={fadeUp} className="inline-block mb-8 px-6 py-2 rounded-full border border-brand/30 bg-background/50 backdrop-blur-xl text-brand font-bold tracking-widest uppercase shadow-spatial">
            Intelligence Pipeline Active
          </motion.div>
          
          <motion.h1 
            variants={fadeUp}
            className="text-6xl sm:text-8xl lg:text-[10rem] font-black tracking-tighter mb-6 leading-[0.9] text-foreground"
          >
            Spatial. <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-b from-foreground to-foreground/30 relative inline-block pb-4">
              Intelligence.
            </span>
          </motion.h1>
          
          <motion.p variants={fadeUp} className="text-lg sm:text-2xl text-muted max-w-3xl mx-auto mb-12 leading-relaxed font-light px-2 sm:px-0">
            A fully autonomous, AI-powered tech journalism pipeline. We scrape, analyze, and deliver a premium magazine straight to you.
          </motion.p>
          
          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row justify-center gap-6 w-full sm:w-auto px-4 sm:px-0">
            <Link href="/services" className="w-full sm:w-auto px-10 py-5 rounded-2xl bg-foreground text-background font-bold tracking-wider hover:bg-foreground/90 shadow-spatial hover:shadow-foreground/20 active:scale-95 transition-all duration-300 flex items-center justify-center gap-3 group">
              Access Protocols <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Services Spatial Stagger Section */}
      <section className="w-full py-32 relative z-20">
        {/* Background depth for services */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-surface/50 to-background -z-10" />
        
        <motion.div 
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 perspective-[1200px]"
        >
          <motion.div variants={fadeUp} className="text-center mb-20">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tighter mb-6 text-foreground">Core <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light text-glow">Protocols</span></h2>
            <p className="text-muted text-lg sm:text-xl font-light">Our expanding suite of intelligence services.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-6 gap-8 sm:gap-12 auto-rows-fr">
            {/* Daily Tech Digest Card - Large Span */}
            <motion.div variants={fadeUp} className="md:col-span-4 h-full transform-style-3d">
              <SpatialCard depth={15} className="h-full p-10 sm:p-14 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer">
                <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-brand/10 flex items-center justify-center mb-8 transition-colors duration-500 shadow-inner">
                  <Zap className="text-brand" size={36} />
                </div>
                <h3 className="text-3xl sm:text-4xl font-bold mb-4 sm:mb-6 text-foreground tracking-tight">Daily Tech Digest</h3>
                <p className="text-muted text-base sm:text-xl mb-8 sm:mb-10 flex-grow leading-relaxed font-light">
                  Our flagship product. A stunning light-mode PDF magazine delivered to Telegram every morning, curated by our Multi-Model AI Cascade.
                </p>
                <Link href="/services" aria-label="Access Protocol for Daily Tech Digest" className="text-brand font-bold tracking-widest uppercase flex items-center gap-3 group-hover:gap-5 transition-all duration-300 w-fit text-sm">
                  Access Protocol <ArrowRight size={18} />
                </Link>
              </SpatialCard>
            </motion.div>

            {/* Placeholder Service 1 - Small Span */}
            <motion.div variants={fadeUp} className="md:col-span-2 h-full transform-style-3d">
              <SpatialCard depth={25} className="h-full p-10 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer bg-surface/50">
                <div className="w-16 h-16 rounded-2xl bg-surface-hover flex items-center justify-center mb-8 group-hover:bg-brand/10 transition-colors duration-500">
                  <Database className="text-muted group-hover:text-brand transition-colors duration-500" size={32} />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-foreground tracking-tight">Data Scraping</h3>
                <p className="text-muted text-base flex-grow mb-8 font-light">
                  Real-time autonomous data extraction.
                </p>
                <span className="text-muted text-xs font-bold uppercase tracking-widest bg-background px-4 py-2 rounded-full w-fit border border-border-subtle">Beta Phase</span>
              </SpatialCard>
            </motion.div>

            {/* Placeholder Service 2 - Medium Span */}
            <motion.div variants={fadeUp} className="md:col-span-3 h-full transform-style-3d">
              <SpatialCard depth={20} className="h-full p-10 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer bg-surface/50">
                <div className="w-16 h-16 rounded-2xl bg-surface-hover flex items-center justify-center mb-8 group-hover:bg-brand/10 transition-colors duration-500">
                  <Cpu className="text-muted group-hover:text-brand transition-colors duration-500" size={32} />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-foreground tracking-tight">Model Cascade</h3>
                <p className="text-muted text-base flex-grow mb-8 font-light">
                  Intelligent routing of prompts across specialized neural networks for optimal output.
                </p>
                <span className="text-muted text-xs font-bold uppercase tracking-widest bg-background px-4 py-2 rounded-full w-fit border border-border-subtle">Restricted</span>
              </SpatialCard>
            </motion.div>

            {/* New Service - Medium Span */}
            <motion.div variants={fadeUp} className="md:col-span-3 h-full transform-style-3d">
              <SpatialCard depth={20} className="h-full p-10 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer bg-surface/50">
                <div className="w-16 h-16 rounded-2xl bg-surface-hover flex items-center justify-center mb-8 group-hover:bg-brand/10 transition-colors duration-500">
                  <Globe className="text-muted group-hover:text-brand transition-colors duration-500" size={32} />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-foreground tracking-tight">Global Sentiment</h3>
                <p className="text-muted text-base flex-grow mb-8 font-light">
                  Worldwide tech sentiment analysis powered by predictive LLM pipelines.
                </p>
                <span className="text-muted text-xs font-bold uppercase tracking-widest bg-background px-4 py-2 rounded-full w-fit border border-border-subtle">Restricted</span>
              </SpatialCard>
            </motion.div>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
