"use client";

import { Mail, Send, MapPin, Globe } from "lucide-react";
import { m as motion, Variants } from "framer-motion";

export default function ContactPage() {
  const fadeUp: Variants = {
    hidden: { opacity: 0, y: 30 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <div className="pt-24 pb-12 sm:pt-32 sm:pb-24 min-h-[80vh] relative overflow-hidden bg-background flex flex-col justify-center">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand/10 rounded-full blur-[100px] -z-10 mix-blend-screen" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-brand-light/10 rounded-full blur-[100px] -z-10 mix-blend-screen" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <motion.div 
          initial="hidden"
          animate="show"
          variants={fadeUp}
          className="text-center mb-16"
        >
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-brand/20 bg-brand/5 text-brand font-bold tracking-widest uppercase text-xs shadow-sm">
            Reach Out
          </div>
          <h1 className="text-4xl sm:text-5xl font-black tracking-tighter mb-6 leading-tight text-foreground">
            Get in <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light">Touch</span>
          </h1>
          <p className="text-lg text-muted max-w-2xl mx-auto font-light leading-relaxed">
            Have questions about Ahead Of Everyone? We're here to help you navigate the noise.
          </p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-8"
        >
          {/* Support Email */}
          <div className="glass rounded-3xl p-8 border border-border-subtle flex flex-col items-center text-center group hover:border-brand/50 transition-colors">
            <div className="w-16 h-16 rounded-2xl bg-brand/10 text-brand flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Mail size={32} />
            </div>
            <h3 className="text-xl font-bold mb-3 text-foreground">Email Support</h3>
            <p className="text-muted text-sm mb-6">Drop us a line anytime. We usually respond within 24 hours.</p>
            <a href="mailto:support@aheadofeveryone.com" className="text-brand font-bold hover:underline">support@aheadofeveryone.com</a>
          </div>

          {/* Telegram Support */}
          <div className="glass rounded-3xl p-8 border border-border-subtle flex flex-col items-center text-center group hover:border-brand/50 transition-colors">
            <div className="w-16 h-16 rounded-2xl bg-blue-500/10 text-blue-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Send size={32} />
            </div>
            <h3 className="text-xl font-bold mb-3 text-foreground">Telegram Direct</h3>
            <p className="text-muted text-sm mb-6">Message our dedicated support bot for immediate assistance.</p>
            <a href="https://t.me/AheadOfEveryoneBot" target="_blank" rel="noopener noreferrer" className="text-blue-500 font-bold hover:underline">@AheadOfEveryoneBot</a>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
