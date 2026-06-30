"use client";

import { m as motion, Variants } from "framer-motion";
import { Plus, Minus } from "lucide-react";
import { useState } from "react";

const faqs = [
  {
    question: "What is Ahead Of Everyone?",
    answer: "Ahead Of Everyone is a fully autonomous AI-powered tech newsletter. We aggregate, summarize, and deliver the most important technology news, developments, and code releases directly to your Telegram every single day."
  },
  {
    question: "How much does it cost?",
    answer: "The core Daily Tech Digest is currently completely free. We may introduce premium tiers for customized AI research agents in the future, but the daily digest will always remain accessible."
  },
  {
    question: "How do I receive the digests?",
    answer: "Digests are sent securely via Telegram. Once you initialize your account, you will receive a unique link code to connect our Telegram bot to your personal account."
  },
  {
    question: "What sources do you scrape?",
    answer: "Our autonomous agents monitor Hacker News, major Tech RSS feeds, AI research repositories, and top engineering blogs. We use advanced LLMs to filter out the noise and synthesize only the most critical signals."
  },
  {
    question: "Can I access my previous digests?",
    answer: "Yes! By logging into the Client Portal on our website, you have full access to your personalized Dashboard which archives your last 10 daily digests with deep-links to the raw source material."
  }
];

function FaqItem({ question, answer }: { question: string, answer: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-border-subtle py-6">
      <button 
        onClick={() => setIsOpen(!isOpen)} 
        className="flex w-full items-center justify-between text-left focus:outline-none group"
      >
        <span className="text-lg font-bold text-foreground group-hover:text-brand transition-colors">{question}</span>
        <div className="w-8 h-8 rounded-full bg-surface-hover flex items-center justify-center shrink-0 ml-4 group-hover:bg-brand/10 transition-colors text-muted group-hover:text-brand">
          {isOpen ? <Minus size={16} /> : <Plus size={16} />}
        </div>
      </button>
      <motion.div 
        initial={false}
        animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="overflow-hidden"
      >
        <p className="pt-4 text-muted font-medium leading-relaxed">
          {answer}
        </p>
      </motion.div>
    </div>
  );
}

export default function FaqPage() {
  const fadeUp: Variants = {
    hidden: { opacity: 0, y: 30 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <div className="pt-24 pb-12 sm:pt-32 sm:pb-24 min-h-[80vh] relative overflow-hidden bg-background">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl h-[500px] bg-brand/5 rounded-full blur-[120px] -z-10 mix-blend-screen" />

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <motion.div 
          initial="hidden"
          animate="show"
          variants={fadeUp}
          className="text-center mb-16"
        >
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-brand/20 bg-brand/5 text-brand font-bold tracking-widest uppercase text-xs shadow-sm">
            Knowledge Base
          </div>
          <h1 className="text-4xl sm:text-5xl font-black tracking-tighter mb-6 leading-tight text-foreground">
            Frequently Asked <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light">Questions</span>
          </h1>
          <p className="text-lg text-muted font-light leading-relaxed">
            Everything you need to know about the product and how it works.
          </p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="glass rounded-3xl p-6 sm:p-10 border border-border-subtle"
        >
          <div className="divide-y divide-border-subtle">
            {faqs.map((faq, index) => (
              <FaqItem key={index} question={faq.question} answer={faq.answer} />
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
