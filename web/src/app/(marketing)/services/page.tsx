"use client";

import { Zap, Database, Cpu, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { motion, Variants } from "framer-motion";
import { SpotlightCard } from "@/components/ui/SpotlightCard";

export default function ServicesPage() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const cardVariants: Variants = {
    hidden: { opacity: 0, y: 50 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: ("easeOut" as any) } },
  };

  return (
    <div className="pt-24 pb-12 sm:pt-28 sm:pb-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 overflow-hidden bg-background">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: ("easeOut" as any) }}
        className="text-center mb-10 sm:mb-14"
      >
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tighter mb-4 sm:mb-6 leading-tight text-foreground">
          Intelligence <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand via-brand-light to-brand text-glow block sm:inline pb-2">Protocols</span>
        </h1>
        <p className="text-lg sm:text-xl text-muted max-w-2xl mx-auto px-2">
          Choose the level of access you need to stay ahead of the curve.
        </p>
      </motion.div>

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-6 gap-6 sm:gap-8"
      >
        {/* Tier 1: Daily Digest */}
        <motion.div variants={cardVariants} className="md:col-span-6 lg:col-span-4 h-full">
          <SpotlightCard className="h-full rounded-3xl p-6 sm:p-10 border border-brand/30 shadow-sm hover:shadow-lg transition-all duration-500 flex flex-col group hover:-translate-y-1">
            <div className="absolute top-0 right-0 w-full h-1 bg-gradient-to-r from-brand to-brand-light opacity-80 group-hover:opacity-100 transition-opacity" />
            
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-xl bg-brand/10 flex items-center justify-center group-hover:bg-brand/20 transition-colors duration-300">
                <Zap className="text-brand" size={28} />
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-wide text-foreground">The Digest</h2>
            </div>
            
            <p className="text-muted text-sm sm:text-lg mb-8 flex-grow leading-relaxed max-w-2xl">
              The core protocol. A daily, highly-curated tech magazine sent directly to your Telegram. Built for executives and engineers who value their time.
            </p>
            
            <div className="mb-8 flex items-baseline">
              <span className="text-4xl sm:text-5xl font-extrabold text-foreground tracking-tight">₹0</span>
              <span className="text-muted ml-2 font-medium tracking-wider">/forever</span>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-8 sm:gap-16 mb-10 flex-grow">
              <ul className="space-y-4">
                {['Daily PDF delivery', 'Multi-Model AI curation'].map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm sm:text-base text-foreground/90">
                    <CheckCircle2 className="text-brand shrink-0 mt-1" size={18} /> 
                    <span className="leading-tight">{feature}</span>
                  </li>
                ))}
              </ul>
              <ul className="space-y-4">
                {['Crisp light-mode typography', 'Telegram integration'].map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm sm:text-base text-foreground/90">
                    <CheckCircle2 className="text-brand shrink-0 mt-1" size={18} /> 
                    <span className="leading-tight">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <Link href="/login" aria-label="Initialize Daily Digest Protocol" className="w-full sm:w-1/2 py-4 rounded-xl bg-brand text-white text-center font-bold tracking-widest uppercase hover:opacity-90 hover:shadow-md active:scale-95 transition-all duration-300 flex justify-center items-center gap-2 mt-auto">
              Initialize <Zap size={18} className="fill-current opacity-50" />
            </Link>
          </SpotlightCard>
        </motion.div>

        {/* Tier 2 & 3 wrapper for Desktop */}
        <div className="md:col-span-6 lg:col-span-2 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 gap-6 sm:gap-8 h-full">
          {/* Tier 2: B2B API */}
          <motion.div variants={cardVariants} className="h-full">
            <SpotlightCard className="h-full rounded-3xl p-6 border border-border-subtle shadow-sm transition-all duration-500 flex flex-col group grayscale hover:grayscale-0">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-lg bg-surface-hover flex items-center justify-center group-hover:bg-brand/10 transition-colors duration-300">
                  <Database className="text-muted group-hover:text-brand transition-colors" size={20} />
                </div>
                <h2 className="text-xl font-bold tracking-wide text-foreground">Data API</h2>
              </div>
              
              <p className="text-muted text-sm mb-4 flex-grow leading-relaxed">
                Raw firehose access. Plug our scraped intelligence directly into your own dashboards.
              </p>
              
              <div className="mb-4">
                <span className="text-2xl font-extrabold text-foreground opacity-80 tracking-tight">TBA</span>
              </div>
              
              <button disabled aria-label="Data API Coming Soon" className="w-full py-3 rounded-lg bg-surface border border-border-subtle text-muted text-center font-bold text-xs tracking-widest uppercase cursor-not-allowed mt-auto">
                Coming Soon
              </button>
            </SpotlightCard>
          </motion.div>

          {/* Tier 3: Consulting */}
          <motion.div variants={cardVariants} className="h-full">
            <SpotlightCard className="h-full rounded-3xl p-6 border border-border-subtle shadow-sm transition-all duration-500 flex flex-col group grayscale hover:grayscale-0">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-lg bg-surface-hover flex items-center justify-center group-hover:bg-brand/10 transition-colors duration-300">
                  <Cpu className="text-muted group-hover:text-brand transition-colors" size={20} />
                </div>
                <h2 className="text-xl font-bold tracking-wide text-foreground">Architecture</h2>
              </div>
              
              <p className="text-muted text-sm mb-4 flex-grow leading-relaxed">
                Bespoke engineering. We build a fully autonomous, serverless pipeline for your niche.
              </p>
              
              <div className="mb-4">
                <span className="text-2xl font-extrabold text-foreground opacity-80 tracking-tight">Custom</span>
              </div>
              
              <button disabled aria-label="Architecture Consulting Waitlist Full" className="w-full py-3 rounded-lg bg-surface border border-border-subtle text-muted text-center font-bold text-xs tracking-widest uppercase cursor-not-allowed mt-auto">
                Waitlist Full
              </button>
            </SpotlightCard>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
