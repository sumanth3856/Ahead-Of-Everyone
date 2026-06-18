"use client";

import Link from "next/link";
import { ArrowRight, Mail, Lock, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";
import { toast } from "sonner";
import { login } from "@/app/auth/actions";
import { SubmitButton } from "@/components/SubmitButton";
import { SpatialCard } from "@/components/ui/SpatialCard";

function LoginFormContent() {
  const searchParams = useSearchParams();
  const message = searchParams.get("message");
  
  const fadeUp = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: ("easeOut" as any) } },
  };

  useEffect(() => {
    if (message) {
      if (message.toLowerCase().includes("check your email")) {
        toast.success(message);
      } else {
        toast.error(message);
      }
    }
  }, [message]);

  return (
    <div className="min-h-screen flex items-center justify-center pt-20 px-4 sm:px-6 lg:px-8 bg-background relative overflow-hidden">
      {/* Immersive 3D Background */}
      <div className="absolute top-0 right-0 -z-10 w-[800px] h-[800px] pointer-events-none perspective-[1000px]">
        <motion.div 
          animate={{ rotateX: 360, rotateY: -180, rotateZ: 180 }}
          transition={{ duration: 80, repeat: Infinity, ease: "linear" }}
          className="w-full h-full rounded-full border border-brand/5"
          style={{ transformStyle: "preserve-3d", transform: "translateZ(-200px) translateX(200px) translateY(-200px)" }}
        />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand/10 blur-[100px] rounded-full" />
      </div>

      <motion.div 
        initial="hidden"
        animate="show"
        variants={fadeUp}
        className="w-full max-w-md relative perspective-[1200px]"
      >
        <div className="transform-style-3d">
          <SpatialCard depth={10} className="w-full p-8 sm:p-10 rounded-[2.5rem] border border-border-subtle shadow-spatial relative z-10">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold tracking-tight text-foreground mb-2">Welcome Back</h2>
          <p className="text-muted text-sm">Enter your credentials to access the intelligence portal.</p>
        </div>


        <form className="space-y-6" action={login}>
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
                autoComplete="current-password"
                required
                className="block w-full pl-10 pr-3 py-3 border border-border-subtle rounded-xl bg-surface text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition-all duration-300"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="rounded border-border-subtle text-brand focus:ring-brand" />
              <span className="text-muted">Remember me</span>
            </label>
            <Link href="#" className="font-semibold text-brand hover:text-brand/80 transition-colors">
              Forgot password?
            </Link>
          </div>

          <SubmitButton
            className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-brand hover:opacity-90 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand transition-all duration-300"
            loadingText="Authenticating"
          >
            Authenticate <ArrowRight size={18} />
          </SubmitButton>
        </form>

        <p className="mt-8 text-center text-sm text-muted">
          Don't have an access protocol?{" "}
          <Link href="/signup" className="font-semibold text-brand hover:text-brand/80 transition-colors">
            Initialize here
          </Link>
        </p>
          </SpatialCard>
        </div>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-background"><div className="animate-pulse w-8 h-8 rounded-full bg-brand"></div></div>}>
      <LoginFormContent />
    </Suspense>
  );
}
