"use client";

import { Zap, Database, Cpu, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function ServicesPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 50 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <div className="pt-24 pb-16 sm:pt-32 sm:pb-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 overflow-hidden">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="text-center mb-16 sm:mb-20"
      >
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-4 sm:mb-6 leading-tight">
          Intelligence <span className="text-brand text-glow block sm:inline mt-2 sm:mt-0">Protocols</span>
        </h1>
        <p className="text-lg sm:text-xl text-muted max-w-2xl mx-auto px-2">
          Choose the level of access you need to stay ahead of the curve.
        </p>
      </motion.div>

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8"
      >
        {/* Tier 1: Daily Digest */}
        <motion.div variants={cardVariants} className="glass rounded-3xl p-6 sm:p-8 border border-brand/40 shadow-[0_0_30px_rgba(113,27,209,0.15)] hover:shadow-[0_0_50px_rgba(113,27,209,0.3)] transition-all duration-500 relative overflow-hidden flex flex-col group hover:-translate-y-2">
          <div className="absolute top-0 right-0 w-full h-1 bg-gradient-to-r from-brand to-brand-light opacity-80 group-hover:opacity-100 transition-opacity" />
          <div className="absolute -top-32 -right-32 w-64 h-64 bg-brand/10 rounded-full blur-[60px] -z-10 group-hover:bg-brand/20 transition-colors duration-500" />
          
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-brand/20 flex items-center justify-center group-hover:bg-brand/40 transition-colors duration-300">
              <Zap className="text-brand-light text-glow" size={24} />
            </div>
            <h2 className="text-2xl font-bold tracking-wide">The Digest</h2>
          </div>
          
          <p className="text-muted text-sm sm:text-base mb-8 flex-grow leading-relaxed">
            The core protocol. A daily, highly-curated tech magazine sent directly to your Telegram.
          </p>
          
          <div className="mb-8 flex items-baseline">
            <span className="text-4xl sm:text-5xl font-extrabold text-foreground tracking-tight">$0</span>
            <span className="text-muted ml-2 font-medium tracking-wider">/forever</span>
          </div>
          
          <ul className="space-y-4 mb-10 flex-grow">
            {['Daily PDF delivery', 'Multi-Model AI curation', 'Dark-mode typography', 'Telegram integration'].map((feature, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-foreground/90">
                <CheckCircle2 className="text-brand-light shrink-0 mt-0.5" size={18} /> 
                <span className="leading-tight">{feature}</span>
              </li>
            ))}
          </ul>
          
          <Link href="/login" aria-label="Initialize Daily Digest Protocol" className="w-full py-4 rounded-xl bg-brand text-white text-center font-bold tracking-widest uppercase hover:bg-brand-light hover:shadow-[0_0_20px_rgba(113,27,209,0.5)] transition-all duration-300 flex justify-center items-center gap-2 mt-auto">
            Initialize <Zap size={18} className="fill-current opacity-50" />
          </Link>
        </motion.div>

        {/* Tier 2: B2B API */}
        <motion.div variants={cardVariants} className="glass rounded-3xl p-6 sm:p-8 border border-white/5 hover:border-brand/30 transition-all duration-500 relative overflow-hidden flex flex-col group opacity-70 hover:opacity-100 grayscale hover:grayscale-0">
          <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 rounded-bl-full -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
          
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-brand/20 transition-colors duration-300">
              <Database className="text-muted group-hover:text-brand-light transition-colors" size={24} />
            </div>
            <h2 className="text-2xl font-bold tracking-wide">Data API</h2>
          </div>
          
          <p className="text-muted text-sm sm:text-base mb-8 flex-grow leading-relaxed">
            Raw firehose access. Plug our scraped intelligence directly into your own dashboards.
          </p>
          
          <div className="mb-8">
            <span className="text-4xl sm:text-5xl font-extrabold text-foreground opacity-80 tracking-tight">TBA</span>
          </div>
          
          <ul className="space-y-4 mb-10 flex-grow">
            {['REST & GraphQL endpoints', 'Real-time webhooks', 'Historical archive access', 'High rate limits'].map((feature, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-muted">
                <CheckCircle2 className="text-muted/50 shrink-0 mt-0.5" size={18} /> 
                <span className="leading-tight">{feature}</span>
              </li>
            ))}
          </ul>
          
          <button disabled aria-label="Data API Coming Soon" className="w-full py-4 rounded-xl bg-surface/50 border border-white/10 text-muted text-center font-bold tracking-widest uppercase cursor-not-allowed mt-auto overflow-hidden relative">
            <div className="absolute inset-0 bg-repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.02) 10px, rgba(255,255,255,0.02) 20px)"></div>
            <span className="relative z-10">Coming Soon</span>
          </button>
        </motion.div>

        {/* Tier 3: Consulting */}
        <motion.div variants={cardVariants} className="glass rounded-3xl p-6 sm:p-8 border border-white/5 hover:border-brand/30 transition-all duration-500 relative overflow-hidden flex flex-col group opacity-70 hover:opacity-100 grayscale hover:grayscale-0">
          <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 rounded-bl-full -z-10 group-hover:bg-brand/10 transition-colors duration-500" />
          
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-brand/20 transition-colors duration-300">
              <Cpu className="text-muted group-hover:text-brand-light transition-colors" size={24} />
            </div>
            <h2 className="text-2xl font-bold tracking-wide">Architecture</h2>
          </div>
          
          <p className="text-muted text-sm sm:text-base mb-8 flex-grow leading-relaxed">
            Bespoke engineering. We build a fully autonomous, serverless AI pipeline for your specific niche.
          </p>
          
          <div className="mb-8">
            <span className="text-4xl sm:text-5xl font-extrabold text-foreground opacity-80 tracking-tight">Custom</span>
          </div>
          
          <ul className="space-y-4 mb-10 flex-grow">
            {['Custom data sources', 'Dedicated LLM routing', 'White-labeled delivery', 'Zero-maintenance setup'].map((feature, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-muted">
                <CheckCircle2 className="text-muted/50 shrink-0 mt-0.5" size={18} /> 
                <span className="leading-tight">{feature}</span>
              </li>
            ))}
          </ul>
          
          <button disabled aria-label="Architecture Consulting Waitlist Full" className="w-full py-4 rounded-xl bg-surface/50 border border-white/10 text-muted text-center font-bold tracking-widest uppercase cursor-not-allowed mt-auto overflow-hidden relative">
            <div className="absolute inset-0 bg-repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.02) 10px, rgba(255,255,255,0.02) 20px)"></div>
            <span className="relative z-10">Waitlist Full</span>
          </button>
        </motion.div>
      </motion.div>
    </div>
  );
}
