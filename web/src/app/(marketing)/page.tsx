"use client";

import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Zap, Database, Cpu, Shield, Globe } from "lucide-react";
import { motion } from "framer-motion";
import { SpotlightCard } from "@/components/ui/SpotlightCard";

export default function Home() {
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
    hidden: { opacity: 0, y: 30 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <div className="flex flex-col items-center overflow-hidden">
      {/* Hero Section */}
      <section className="relative w-full min-h-[90svh] flex items-center justify-center pt-24 pb-8 sm:pt-28 bg-background z-0">
        
        {/* Ethereal Background Orbs */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
          <motion.div 
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-1/4 left-1/4 w-[400px] h-[400px] sm:w-[600px] sm:h-[600px] bg-brand/20 rounded-full blur-[100px] mix-blend-screen"
          />
          <motion.div 
            animate={{ 
              scale: [1, 1.5, 1],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 2 }}
            className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] sm:w-[500px] sm:h-[500px] bg-brand-light/10 rounded-full blur-[120px] mix-blend-screen"
          />
        </div>

        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center w-full"
        >
          <motion.div variants={fadeUp} className="inline-block mb-6 px-4 py-1.5 rounded-full border border-brand/20 bg-brand/5 text-brand font-bold tracking-widest uppercase shadow-sm">
            Intelligence Pipeline Active
          </motion.div>
          
          <motion.h1 
            variants={fadeUp}
            className="text-5xl sm:text-7xl lg:text-8xl font-black tracking-tighter mb-6 leading-[1.1] text-foreground"
          >
            Five minutes. <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand via-brand-light to-brand text-glow relative inline-block pb-2">
              Ahead of everyone.
            </span>
          </motion.h1>
          
          <motion.p variants={fadeUp} className="text-base sm:text-xl text-muted max-w-2xl mx-auto mb-6 sm:mb-8 leading-relaxed px-2 sm:px-0">
            A fully autonomous, AI-powered tech journalism pipeline. We scrape, analyze, and deliver a premium magazine straight to you.
          </motion.p>
          
          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row justify-center gap-4 w-full sm:w-auto px-4 sm:px-0">
            <Link href="/services" className="w-full sm:w-auto px-8 py-4 rounded-lg bg-brand text-white font-semibold tracking-wider hover:opacity-90 shadow-md hover:shadow-lg active:scale-95 transition-all duration-300 flex items-center justify-center gap-2 group">
              Explore Services <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/about" className="w-full sm:w-auto px-8 py-4 rounded-lg glass text-foreground font-semibold tracking-wider hover:bg-surface-hover active:scale-95 transition-all duration-300 text-center">
              How it works
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Services Preview Section */}
      <section className="w-full py-16 sm:py-20 bg-surface border-t border-border-subtle relative">
        <motion.div 
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
        >
          <motion.div variants={fadeUp} className="text-center mb-10 sm:mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-wider mb-4 text-foreground">Core <span className="text-brand">Protocols</span></h2>
            <p className="text-muted text-base sm:text-lg">Our expanding suite of intelligence services.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-6 gap-6 sm:gap-8 auto-rows-fr">
            {/* Daily Tech Digest Card - Large Span */}
            <motion.div variants={fadeUp} className="md:col-span-4 h-full">
              <SpotlightCard className="h-full p-8 sm:p-10 rounded-3xl border-border-subtle flex flex-col group cursor-pointer">
                <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-brand/10 flex items-center justify-center mb-6 sm:mb-8 transition-colors duration-500">
                  <Zap className="text-brand" size={28} />
                </div>
                <h3 className="text-2xl sm:text-3xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Daily Tech Digest</h3>
                <p className="text-muted text-sm sm:text-lg mb-6 sm:mb-8 flex-grow leading-relaxed">
                  Our flagship product. A stunning light-mode PDF magazine delivered to Telegram every morning, curated by our Multi-Model AI Cascade.
                </p>
                <Link href="/services" aria-label="Access Protocol for Daily Tech Digest" className="text-brand font-medium tracking-wide flex items-center gap-2 group-hover:gap-4 transition-all duration-300 w-fit">
                  Access Protocol <ArrowRight size={18} />
                </Link>
              </SpotlightCard>
            </motion.div>

            {/* Placeholder Service 1 - Small Span */}
            <motion.div variants={fadeUp} className="md:col-span-2 h-full">
              <SpotlightCard className="h-full p-8 sm:p-10 rounded-3xl border-border-subtle flex flex-col group cursor-pointer">
                <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-surface-hover flex items-center justify-center mb-6 sm:mb-8 group-hover:bg-brand/10 transition-colors duration-500">
                  <Database className="text-muted group-hover:text-brand transition-colors duration-500" size={28} />
                </div>
                <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Data Scraping</h3>
                <p className="text-muted text-sm flex-grow mb-6">
                  Real-time autonomous data extraction.
                </p>
                <span className="text-muted text-xs font-bold uppercase tracking-widest bg-surface px-3 py-1.5 rounded-full w-fit">Beta Phase</span>
              </SpotlightCard>
            </motion.div>

            {/* Placeholder Service 2 - Medium Span */}
            <motion.div variants={fadeUp} className="md:col-span-3 h-full">
              <SpotlightCard className="h-full p-8 sm:p-10 rounded-3xl border-border-subtle flex flex-col group cursor-pointer">
                <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-surface-hover flex items-center justify-center mb-6 sm:mb-8 group-hover:bg-brand/10 transition-colors duration-500">
                  <Cpu className="text-muted group-hover:text-brand transition-colors duration-500" size={28} />
                </div>
                <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Model Cascade</h3>
                <p className="text-muted text-sm flex-grow mb-6">
                  Intelligent routing of prompts across specialized neural networks for optimal output.
                </p>
                <span className="text-muted text-xs font-bold uppercase tracking-widest bg-surface px-3 py-1.5 rounded-full w-fit">Restricted</span>
              </SpotlightCard>
            </motion.div>

            {/* New Service - Medium Span */}
            <motion.div variants={fadeUp} className="md:col-span-3 h-full">
              <SpotlightCard className="h-full p-8 sm:p-10 rounded-3xl border-border-subtle flex flex-col group cursor-pointer">
                <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-surface-hover flex items-center justify-center mb-6 sm:mb-8 group-hover:bg-brand/10 transition-colors duration-500">
                  <Globe className="text-muted group-hover:text-brand transition-colors duration-500" size={28} />
                </div>
                <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Global Sentiment</h3>
                <p className="text-muted text-sm flex-grow mb-6">
                  Worldwide tech sentiment analysis powered by predictive LLM pipelines.
                </p>
                <span className="text-muted text-xs font-bold uppercase tracking-widest bg-surface px-3 py-1.5 rounded-full w-fit">Restricted</span>
              </SpotlightCard>
            </motion.div>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
