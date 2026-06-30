"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Zap, Database, Cpu, Shield, Globe } from "lucide-react";
import { m as motion, Variants } from "framer-motion";
import dynamic from "next/dynamic";
const SpatialCard = dynamic(() => import("@/components/ui/SpatialCard").then(mod => mod.SpatialCard), { ssr: false });
import { MagneticButton } from "@/components/ui/MagneticButton";

export default function Home() {
  const router = useRouter();

  const staggerContainer: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
      },
    },
  };

  const fadeUp: Variants = {
    hidden: { opacity: 0, y: 50 },
    show: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" as any } },
  };

  const textRevealContainer: Variants = {
    hidden: { opacity: 1 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.2,
      }
    }
  };

  const textRevealItem: Variants = {
    hidden: { y: "120%", opacity: 0 },
    show: { 
      y: "0%", 
      opacity: 1,
      transition: { 
        type: "spring",
        damping: 12,
        stiffness: 100
      }
    }
  };

  const title1 = "Spatial.".split("");
  const title2 = "Newsletter.".split("");

  return (
    <div className="flex flex-col items-center overflow-hidden bg-background">
      
      {/* Minimal Hero Section */}
      <section className="relative w-full min-h-[70svh] pt-24 sm:pt-32 pb-8 sm:pb-12 flex items-center justify-center">
        
        {/* Simple Gradient Background */}
        <div className="absolute inset-0 w-full h-full -z-10 overflow-hidden flex items-center justify-center">
          <div className="w-[800px] h-[800px] rounded-full bg-brand/10 blur-[120px]" />
        </div>

        {/* Foreground Content */}
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center w-full"
        >
          <motion.div variants={fadeUp} className="inline-block mb-10 px-5 py-2 rounded-full border border-brand/20 bg-brand/5 text-brand font-bold tracking-widest uppercase text-xs sm:text-sm shadow-sm">
            Newsletter Active
          </motion.div>
          
          {/* Hyper-Kinetic Typography */}
          <motion.h1 
            variants={textRevealContainer}
            initial="hidden"
            animate="show"
            className="text-4xl sm:text-7xl lg:text-[7.5rem] font-black tracking-tighter mb-8 text-foreground leading-[0.9] select-none"
          >
            <div className="overflow-hidden pt-8 -mt-8 pb-4 pr-4 inline-block cursor-default">
              {title1.map((char, index) => (
                <motion.span 
                  key={index} 
                  variants={textRevealItem} 
                  whileHover={{ y: -20, scale: 1.1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 10 }}
                  className="inline-block transition-colors duration-200 hover:text-brand"
                >
                  {char === " " ? "\u00A0" : char}
                </motion.span>
              ))}
            </div>
            <br className="hidden sm:block" />
            <div className="overflow-hidden pt-8 -mt-8 pb-6 pr-4 inline-block cursor-default">
              {title2.map((char, index) => (
                <motion.span 
                  key={index} 
                  variants={textRevealItem} 
                  whileHover={{ y: -20, scale: 1.1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 10 }}
                  className="inline-block text-brand transition-colors duration-200 hover:text-brand-light"
                >
                  {char === " " ? "\u00A0" : char}
                </motion.span>
              ))}
            </div>
          </motion.h1>
          
          <motion.p variants={fadeUp} className="text-lg sm:text-2xl text-muted max-w-2xl mx-auto mb-14 leading-relaxed font-light">
            A fully autonomous, AI-powered tech journalism pipeline. We scrape, analyze, and deliver a premium magazine straight to you.
          </motion.p>
          
          {/* Magnetic CTA */}
          <motion.div variants={fadeUp} className="flex justify-center w-full">
            <MagneticButton 
              strength={40} 
              onClick={() => router.push('/login')}
              className="px-6 py-4 sm:px-10 sm:py-5 rounded-2xl bg-foreground text-background font-bold tracking-wider shadow-spatial active:scale-95 transition-all duration-300 flex items-center gap-3 group relative overflow-hidden border border-border-subtle"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-brand to-brand-light opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <span className="relative z-10 group-hover:text-white transition-colors duration-300">Get Started</span>
              <ArrowRight size={20} className="relative z-10 group-hover:text-white group-hover:translate-x-2 transition-all duration-300" />
            </MagneticButton>
          </motion.div>

        </motion.div>
      </section>

      {/* Services Spatial Stagger Section */}
      <section className="w-full py-16 sm:py-24 relative z-20">
        {/* Background depth for services */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-surface/50 to-background -z-10" />
        
        <motion.div 
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 perspective-[1200px]"
        >
          <motion.div variants={fadeUp} className="text-center mb-12 sm:mb-16">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tighter mb-6 text-foreground">Core <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light text-glow">Services</span></h2>
            <p className="text-muted text-lg sm:text-xl font-light">Our expanding suite of services.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-6 gap-8 sm:gap-12 auto-rows-fr">
            {/* Daily Tech Digest Card - Large Span */}
            <motion.div variants={fadeUp} className="md:col-span-4 h-full transform-style-3d">
              <SpatialCard depth={15} className="h-full p-6 sm:p-10 md:p-14 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer">
                <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-brand/10 flex items-center justify-center mb-8 transition-colors duration-500 shadow-inner">
                  <Zap className="text-brand" size={36} />
                </div>
                <h3 className="text-3xl sm:text-4xl font-bold mb-4 sm:mb-6 text-foreground tracking-tight">Daily Tech Digest</h3>
                <p className="text-muted text-base sm:text-xl mb-8 sm:mb-10 flex-grow leading-relaxed font-light">
                  Our flagship product. A stunning light-mode PDF magazine delivered to Telegram every morning, curated by our Multi-Model AI Cascade.
                </p>
                <Link href="/login" aria-label="Get Started with Daily Tech Digest" className="text-brand font-bold tracking-widest uppercase flex items-center gap-3 group-hover:gap-5 transition-all duration-300 w-fit text-sm">
                  Get Started <ArrowRight size={18} />
                </Link>
              </SpatialCard>
            </motion.div>

            {/* Placeholder Service 1 - Small Span */}
            <motion.div variants={fadeUp} className="md:col-span-2 h-full transform-style-3d">
              <SpatialCard depth={25} className="h-full p-6 sm:p-10 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer bg-surface/50">
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
              <SpatialCard depth={20} className="h-full p-6 sm:p-10 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer bg-surface/50">
                <div className="w-16 h-16 rounded-2xl bg-surface-hover flex items-center justify-center mb-8 group-hover:bg-brand/10 transition-colors duration-500">
                  <Cpu className="text-muted group-hover:text-brand transition-colors duration-500" size={32} />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-foreground tracking-tight">Model Cascade</h3>
                <p className="text-muted text-base flex-grow mb-8 font-light">
                  Smart routing of prompts across specialized neural networks for optimal output.
                </p>
                <span className="text-muted text-xs font-bold uppercase tracking-widest bg-background px-4 py-2 rounded-full w-fit border border-border-subtle">Restricted</span>
              </SpatialCard>
            </motion.div>

            {/* New Service - Medium Span */}
            <motion.div variants={fadeUp} className="md:col-span-3 h-full transform-style-3d">
              <SpatialCard depth={20} className="h-full p-6 sm:p-10 rounded-[2.5rem] border-border-subtle flex flex-col group cursor-pointer bg-surface/50">
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
