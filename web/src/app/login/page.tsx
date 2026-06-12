import Link from "next/link";
import { Send, AlertCircle, ShieldCheck } from "lucide-react";
import { loginWithTelegram } from "@/app/auth/actions";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ message: string }>;
}) {
  const params = await searchParams;
  const message = params?.message;
  
  return (
    <div className="min-h-[calc(100vh-5rem)] flex items-center justify-center p-4 pt-20">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-wider mb-2">INTELLIGENCE <span className="text-brand text-glow">ACCESS</span></h1>
          <p className="text-muted text-sm">Authenticate via secure Telegram uplink</p>
        </div>

        <div className="glass rounded-2xl p-8 relative overflow-hidden group">
          <div className="absolute -inset-0.5 bg-brand/20 blur-xl rounded-2xl opacity-0 group-hover:opacity-100 transition duration-500 pointer-events-none"></div>
          
          {message && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg flex items-center gap-2 mb-6 text-sm relative z-10">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{message}</span>
            </div>
          )}

          <div className="relative z-10 flex flex-col items-center gap-8 py-4">
            <div className="h-20 w-20 rounded-full bg-brand/10 border border-brand/50 flex items-center justify-center relative">
              <div className="absolute inset-0 rounded-full bg-brand/20 animate-ping opacity-20"></div>
              <ShieldCheck className="h-10 w-10 text-brand-light text-glow" />
            </div>
            
            <div className="text-center">
              <h2 className="text-lg font-semibold text-foreground tracking-wide mb-1">Secure Uplink Required</h2>
              <p className="text-sm text-muted">To access your dashboard, please authenticate using your Telegram account.</p>
            </div>

            <form action={loginWithTelegram} className="w-full mt-4">
              <button 
                type="submit" 
                className="w-full bg-[#2AABEE]/10 border border-[#2AABEE]/50 text-[#2AABEE] font-semibold tracking-widest text-sm uppercase py-4 rounded-lg hover:bg-[#2AABEE] hover:text-white hover:shadow-[0_0_25px_rgba(42,171,238,0.5)] transition-all duration-300 flex items-center justify-center gap-3 group/btn cursor-pointer"
              >
                <Send className="h-5 w-5 group-hover/btn:-translate-y-1 group-hover/btn:translate-x-1 transition-transform" />
                <span>Log in with Telegram</span>
              </button>
            </form>
          </div>
        </div>

        <div className="text-center mt-8 space-y-2">
          <p className="text-xs text-muted max-w-xs mx-auto leading-relaxed">
            By authenticating, you establish a secure connection to the Ahead Of Everyone intelligence pipeline.
          </p>
          <Link href="/" className="text-brand hover:text-brand-light transition-colors text-xs font-medium uppercase tracking-widest block mt-6">
            Return to Base
          </Link>
        </div>
      </div>
    </div>
  );
}
