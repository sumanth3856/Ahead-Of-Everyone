"use client";

import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Zap, Database, Cpu } from "lucide-react";
import { motion } from "framer-motion";

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
      <section className="relative w-full min-h-[100svh] flex items-center justify-center pt-24 pb-12 sm:pt-32">
        {/* Background glow effects */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] sm:w-[600px] sm:h-[600px] lg:w-[800px] lg:h-[800px] bg-brand/20 rounded-full blur-[80px] sm:blur-[120px] -z-10 pointer-events-none" 
        />
        
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center w-full"
        >
          <motion.div variants={fadeUp} className="inline-block mb-6 px-4 py-1.5 rounded-full border border-brand/30 bg-brand/10 text-brand-light text-xs font-semibold tracking-widest uppercase shadow-[0_0_15px_rgba(113,27,209,0.3)]">
            Intelligence Pipeline Active
          </motion.div>
          
          <motion.h1 variants={fadeUp} className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold tracking-tight mb-6 sm:mb-8">
            <span className="text-foreground">Five minutes.</span>
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light text-glow leading-tight sm:leading-tight block pb-2 sm:pb-4 mt-2 sm:mt-0">
              ahead of everyone.
            </span>
          </motion.h1>
          
          <motion.p variants={fadeUp} className="text-base sm:text-xl text-muted max-w-2xl mx-auto mb-8 sm:mb-10 leading-relaxed px-2 sm:px-0">
            A fully autonomous, AI-powered tech journalism pipeline. We scrape, analyze, and deliver a premium cyberpunk magazine straight to you.
          </motion.p>
          
          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row justify-center gap-4 w-full sm:w-auto px-4 sm:px-0">
            <Link href="/services" className="w-full sm:w-auto px-8 py-4 rounded-lg bg-brand text-white font-semibold tracking-wider hover:bg-brand-light bg-glow transition-all duration-300 flex items-center justify-center gap-2 group">
              Explore Services <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/about" className="w-full sm:w-auto px-8 py-4 rounded-lg glass text-foreground font-semibold tracking-wider hover:bg-white/10 transition-all duration-300 text-center">
              How it works
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Services Preview Section */}
      <section className="w-full py-24 sm:py-32 bg-surface/30 border-t border-brand/10 relative">
        <div className="absolute left-0 top-0 w-full sm:w-1/3 h-full bg-gradient-to-b sm:bg-gradient-to-r from-brand/5 to-transparent -z-10 pointer-events-none" />
        
        <motion.div 
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
        >
          <motion.div variants={fadeUp} className="text-center mb-16 sm:mb-20">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-wider mb-4">Core <span className="text-brand text-glow">Protocols</span></h2>
            <p className="text-muted text-base sm:text-lg">Our expanding suite of intelligence services.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {/* Daily Tech Digest Card */}
            <motion.div variants={fadeUp} className="glass p-8 sm:p-10 rounded-2xl border border-brand/40 hover:border-brand shadow-[0_0_30px_rgba(113,27,209,0.1)] hover:shadow-[0_0_40px_rgba(113,27,209,0.2)] transition-all duration-500 group hover:-translate-y-2 relative overflow-hidden flex flex-col">
              <div className="absolute top-0 right-0 w-24 h-24 sm:w-32 sm:h-32 bg-brand/10 rounded-bl-full -z-10 group-hover:bg-brand/20 transition-colors duration-500" />
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-brand/20 flex items-center justify-center mb-6 sm:mb-8 group-hover:bg-brand/40 transition-colors duration-500">
                <Zap className="text-brand-light" size={28} />
              </div>
              <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground tracking-wide">Daily Tech Digest</h3>
              <p className="text-muted text-sm sm:text-base mb-6 sm:mb-8 flex-grow leading-relaxed">
                Our flagship product. A stunning dark-mode PDF magazine delivered to Telegram every morning, curated by our Multi-Model AI Cascade.
              </p>
              <Link href="/services" aria-label="Access Protocol for Daily Tech Digest" className="text-brand-light font-medium tracking-wide flex items-center gap-2 group-hover:gap-4 transition-all duration-300 w-fit">
                Access Protocol <ArrowRight size={18} />
              </Link>
            </motion.div>

            {/* Placeholder Service 1 */}
            <motion.div variants={fadeUp} className="glass p-8 sm:p-10 rounded-2xl border border-white/5 hover:border-brand/30 transition-all duration-500 group hover:-translate-y-2 relative overflow-hidden flex flex-col">
              <div className="absolute top-0 right-0 w-24 h-24 sm:w-32 sm:h-32 bg-white/5 rounded-bl-full -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-white/5 flex items-center justify-center mb-6 sm:mb-8 group-hover:bg-brand/20 transition-colors duration-500">
                <Database className="text-muted group-hover:text-brand-light transition-colors duration-500" size={28} />
              </div>
              <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground opacity-90 tracking-wide">B2B Data API</h3>
              <p className="text-muted text-sm sm:text-base mb-6 sm:mb-8 flex-grow opacity-90 leading-relaxed">
                Direct access to our aggregated tech data and synthesized insights. Build your own dashboards and customized intelligence alerts.
              </p>
              <span className="text-xs uppercase tracking-widest text-brand-light border border-brand/20 bg-brand/5 px-4 py-2 rounded-full font-semibold w-fit self-start">Coming Soon</span>
            </motion.div>

            {/* Placeholder Service 2 */}
            <motion.div variants={fadeUp} className="glass p-8 sm:p-10 rounded-2xl border border-white/5 hover:border-brand/30 transition-all duration-500 group hover:-translate-y-2 relative overflow-hidden flex flex-col">
              <div className="absolute top-0 right-0 w-24 h-24 sm:w-32 sm:h-32 bg-white/5 rounded-bl-full -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-white/5 flex items-center justify-center mb-6 sm:mb-8 group-hover:bg-brand/20 transition-colors duration-500">
                <Cpu className="text-muted group-hover:text-brand-light transition-colors duration-500" size={28} />
              </div>
              <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-foreground opacity-90 tracking-wide">AI Consultation</h3>
              <p className="text-muted text-sm sm:text-base mb-6 sm:mb-8 flex-grow opacity-90 leading-relaxed">
                Leverage our architecture for your own autonomous pipelines. Serverless, zero-maintenance, and designed for infinite scale.
              </p>
              <span className="text-xs uppercase tracking-widest text-brand-light border border-brand/20 bg-brand/5 px-4 py-2 rounded-full font-semibold w-fit self-start">Coming Soon</span>
            </motion.div>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
