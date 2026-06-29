"use client";

import { Zap, Database, Cpu, CheckCircle2, Lock, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion, Variants } from "framer-motion";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { MagneticButton } from "@/components/ui/MagneticButton";

export default function ServicesPage() {
  const router = useRouter();
  
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
    <div className="pt-24 pb-12 sm:pt-28 sm:pb-16 min-h-screen relative overflow-hidden bg-background">
      
      {/* Background Animated Orbs */}
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-brand/10 rounded-full blur-[120px] -z-10 mix-blend-screen animate-pulse" style={{ animationDuration: '8s' }} />
      <div className="absolute top-1/2 right-1/4 w-[400px] h-[400px] bg-brand-light/10 rounded-full blur-[100px] -z-10 mix-blend-screen animate-pulse" style={{ animationDuration: '10s', animationDelay: '2s' }} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: ("easeOut" as any) }}
          className="text-center mb-16 sm:mb-24"
        >
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-brand/20 bg-brand/5 text-brand font-bold tracking-widest uppercase text-xs shadow-sm">
            Access Levels
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tighter mb-6 leading-tight text-foreground">
            Intelligence <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand via-brand-light to-brand text-glow">Protocols</span>
          </h1>
          <p className="text-lg sm:text-xl text-muted max-w-2xl mx-auto font-light leading-relaxed">
            Choose the tier that matches your required signal-to-noise ratio.
          </p>
        </motion.div>

        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="flex lg:grid flex-nowrap lg:grid-cols-3 overflow-x-auto lg:overflow-visible pb-8 lg:pb-0 snap-x snap-mandatory gap-6 perspective-[1200px] items-center -mx-4 px-4 sm:mx-0 sm:px-0 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
        >
          {/* Tier 1: Data API (Locked - Left) */}
          <motion.div variants={cardVariants} className="relative shrink-0 w-[85vw] sm:w-[400px] lg:w-full h-full snap-center lg:scale-95 z-10 hover:z-30 transition-all duration-300">
            <SpatialCard depth={10} className="h-full rounded-[2.5rem] p-8 border border-border-subtle shadow-sm flex flex-col group relative overflow-hidden bg-surface/40 backdrop-blur-sm">
              <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-background/60 backdrop-blur-[2px] transition-all duration-300 group-hover:bg-background/40">
                <div className="w-16 h-16 rounded-2xl bg-surface border border-border-subtle shadow-xl flex items-center justify-center mb-4 text-muted group-hover:scale-110 group-hover:text-foreground transition-all duration-300">
                  <Lock size={24} />
                </div>
                <span className="font-bold tracking-widest uppercase text-xs text-muted group-hover:text-foreground transition-colors">Classified Access</span>
              </div>

              <div className="opacity-40 grayscale group-hover:grayscale-[50%] transition-all duration-500">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-surface-hover flex items-center justify-center">
                    <Database className="text-muted" size={24} />
                  </div>
                  <h2 className="text-2xl font-bold tracking-wide text-foreground">Data API</h2>
                </div>
                <p className="text-muted text-sm mb-8 flex-grow leading-relaxed">
                  Raw firehose access. Plug our scraped intelligence directly into your own dashboards.
                </p>
                <div className="mb-8">
                  <span className="text-3xl font-extrabold text-foreground tracking-tight">TBA</span>
                </div>
              </div>
            </SpatialCard>
          </motion.div>

          {/* Tier 2: The Digest (Active Hero - Center) */}
          <motion.div variants={cardVariants} className="relative shrink-0 w-[85vw] sm:w-[400px] lg:w-full h-full snap-center z-20 lg:scale-105 transition-all duration-300">
            <SpatialCard depth={15} className="h-full rounded-[2.5rem] p-8 sm:p-10 border border-brand/40 shadow-[0_0_40px_rgba(113,27,209,0.15)] flex flex-col group bg-surface relative overflow-hidden">
              <div className="absolute -top-24 -right-24 w-48 h-48 bg-brand/20 blur-[50px] rounded-full pointer-events-none" />
              
              <div className="flex justify-between items-start mb-6">
                <div className="w-16 h-16 rounded-2xl bg-brand/10 border border-brand/20 flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 bg-brand/20 animate-pulse" />
                  <Zap className="text-brand relative z-10" size={28} />
                </div>
                <span className="px-3 py-1 rounded-full bg-brand/10 text-brand text-xs font-bold tracking-widest uppercase border border-brand/20">
                  Active
                </span>
              </div>
              
              <h2 className="text-3xl sm:text-4xl font-black tracking-tighter text-foreground mb-4">The Digest</h2>
              
              <p className="text-muted text-sm sm:text-base mb-8 flex-grow leading-relaxed">
                The core protocol. A daily, highly-curated tech magazine sent directly to your Telegram. Built for executives and engineers who value their time.
              </p>
              
              <div className="mb-10 flex items-baseline border-b border-border-subtle pb-8">
                <span className="text-5xl sm:text-6xl font-black text-foreground tracking-tighter">₹0</span>
                <span className="text-muted ml-2 font-medium tracking-wider text-sm">/forever</span>
              </div>
              
              <ul className="space-y-4 mb-10">
                {['Daily PDF delivery', 'Multi-Model AI curation', 'Crisp light & dark typography', 'Direct Telegram integration'].map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-foreground/90 group/item">
                    <div className="mt-0.5 relative flex items-center justify-center w-5 h-5 rounded-full bg-brand/10 group-hover/item:bg-brand/20 transition-colors">
                      <CheckCircle2 className="text-brand" size={14} /> 
                    </div>
                    <span className="leading-tight font-medium text-sm sm:text-base group-hover/item:text-brand transition-colors">{feature}</span>
                  </li>
                ))}
              </ul>
              
              <div className="mt-auto pt-4">
                <MagneticButton 
                  strength={20} 
                  onClick={() => router.push('/login')}
                  className="w-full py-5 rounded-2xl bg-foreground text-background font-bold tracking-wider uppercase text-sm shadow-spatial active:scale-95 transition-all duration-300 flex justify-center items-center gap-3 group/btn relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-brand to-brand-light opacity-0 group-hover/btn:opacity-100 transition-opacity duration-500" />
                  <span className="relative z-10 group-hover/btn:text-white transition-colors duration-300">Initialize</span>
                  <ArrowRight size={18} className="relative z-10 group-hover/btn:text-white group-hover/btn:translate-x-1 transition-all duration-300" />
                </MagneticButton>
              </div>
            </SpatialCard>
          </motion.div>

          {/* Tier 3: Architecture (Locked - Right) */}
          <motion.div variants={cardVariants} className="relative shrink-0 w-[85vw] sm:w-[400px] lg:w-full h-full snap-center lg:scale-95 z-10 hover:z-30 transition-all duration-300">
            <SpatialCard depth={10} className="h-full rounded-[2.5rem] p-8 border border-border-subtle shadow-sm flex flex-col group relative overflow-hidden bg-surface/40 backdrop-blur-sm">
              <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-background/60 backdrop-blur-[2px] transition-all duration-300 group-hover:bg-background/40">
                <div className="w-16 h-16 rounded-2xl bg-surface border border-border-subtle shadow-xl flex items-center justify-center mb-4 text-muted group-hover:scale-110 group-hover:text-foreground transition-all duration-300">
                  <Lock size={24} />
                </div>
                <span className="font-bold tracking-widest uppercase text-xs text-muted group-hover:text-foreground transition-colors">Waitlist Full</span>
              </div>

              <div className="opacity-40 grayscale group-hover:grayscale-[50%] transition-all duration-500">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-surface-hover flex items-center justify-center">
                    <Cpu className="text-muted" size={24} />
                  </div>
                  <h2 className="text-2xl font-bold tracking-wide text-foreground">Architecture</h2>
                </div>
                <p className="text-muted text-sm mb-8 flex-grow leading-relaxed">
                  Bespoke engineering. We build a fully autonomous, serverless pipeline for your niche.
                </p>
                <div className="mb-8">
                  <span className="text-3xl font-extrabold text-foreground tracking-tight">Custom</span>
                </div>
              </div>
            </SpatialCard>
          </motion.div>

        </motion.div>
      </div>
    </div>
  );
}
