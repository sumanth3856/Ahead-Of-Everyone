"use client";

import Link from "next/link";
import { ArrowRight, Mail, Lock, User, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { signup } from "@/app/auth/actions";

function SignupFormContent() {
  const searchParams = useSearchParams();
  const message = searchParams.get("message");
  
  const fadeUp = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: ("easeOut" as any) } },
  };

  return (
    <div className="min-h-screen flex items-center justify-center pt-20 px-4 sm:px-6 lg:px-8 bg-background relative overflow-hidden">
      {/* Decorative background element */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-brand/5 rounded-full blur-[100px] -z-10 pointer-events-none" />

      <motion.div 
        initial="hidden"
        animate="show"
        variants={fadeUp}
        className="w-full max-w-md glass p-6 sm:p-10 rounded-2xl border border-border-subtle shadow-lg relative"
      >
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold tracking-tight text-foreground mb-2">Create Protocol</h2>
          <p className="text-muted text-sm">Register to initialize your intelligence dashboard.</p>
        </div>

        {message && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 mb-6 rounded-xl border flex items-start gap-3 text-sm ${
              message.toLowerCase().includes('check your email') 
                ? 'bg-green-500/10 border-green-500/20 text-green-400'
                : 'bg-red-500/10 border-red-500/20 text-red-400'
            }`}
          >
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p>{message}</p>
          </motion.div>
        )}

        <form className="space-y-5" action={signup}>
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-foreground mb-2">
              Full Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-muted" />
              </div>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                required
                className="block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl bg-surface text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition-all duration-300"
                placeholder="Agent Smith"
              />
            </div>
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-muted" />
              </div>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl bg-surface text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition-all duration-300"
                placeholder="agent@aheadofeveryone.com"
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-muted" />
              </div>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl bg-surface text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition-all duration-300"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-brand hover:opacity-90 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand transition-all duration-300 mt-6"
          >
            Create Protocol <ArrowRight size={18} />
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-muted">
          Already have an access protocol?{" "}
          <Link href="/login" className="font-semibold text-brand hover:text-brand/80 transition-colors">
            Authenticate
          </Link>
        </p>
      </motion.div>
    </div>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-background"><div className="animate-pulse w-8 h-8 rounded-full bg-brand"></div></div>}>
      <SignupFormContent />
    </Suspense>
  );
}
