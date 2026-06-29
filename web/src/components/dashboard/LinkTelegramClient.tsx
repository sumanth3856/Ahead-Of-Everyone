"use client";

import { useState, useEffect } from "react";
import { Send, CheckCircle2, Loader2, Copy } from "lucide-react";
import { generateTelegramLinkCode } from "@/app/dashboard/actions";
import { SpatialCard } from "@/components/ui/SpatialCard";

export default function LinkTelegramClient() {
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  // Load persistent cooldown on mount
  useEffect(() => {
    const expires = localStorage.getItem("link_cooldown_expires");
    const savedCode = localStorage.getItem("link_code_generated");
    if (expires) {
      const remaining = Math.ceil((parseInt(expires) - Date.now()) / 1000);
      if (remaining > 0) {
        setCooldown(remaining);
        if (savedCode) setCode(savedCode);
      } else {
        localStorage.removeItem("link_cooldown_expires");
        localStorage.removeItem("link_code_generated");
      }
    }
  }, []);

  // Tick the cooldown
  useEffect(() => {
    if (cooldown <= 0) return;

    const timer = setInterval(() => {
      setCooldown(prev => {
        if (prev <= 1) {
          localStorage.removeItem("link_cooldown_expires");
          localStorage.removeItem("link_code_generated");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const newCode = await generateTelegramLinkCode();
      setCode(newCode);
      setCooldown(30);
      localStorage.setItem("link_cooldown_expires", (Date.now() + 30000).toString());
      localStorage.setItem("link_code_generated", newCode);
    } catch (e) {
      console.error(e);
      alert("Failed to generate code.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (code) {
      navigator.clipboard.writeText(`/link ${code}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle lg:col-span-1 shadow-sm bg-brand/5">
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 rounded-lg bg-brand/10 border border-brand/20">
            <Send className="h-6 w-6 text-brand" />
          </div>
          <h2 className="font-bold tracking-wide uppercase text-sm text-foreground">Link Telegram</h2>
        </div>
        
        <p className="text-sm text-muted mb-6">
          Connect your Telegram account to generate and receive personalized PDF digests directly to this dashboard.
        </p>

        {!code ? (
          <button
            onClick={handleGenerate}
            disabled={loading || cooldown > 0}
            className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-brand hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : (cooldown > 0 ? `Wait ${cooldown}s` : "Generate Link Code")}
          </button>
        ) : (
          <div className="space-y-4">
            <p className="text-xs font-semibold text-foreground uppercase tracking-wider text-center">
              Send this to the Bot:
            </p>
            <div 
              onClick={handleCopy}
              className="w-full flex justify-between items-center bg-surface border border-brand/30 rounded-xl p-4 cursor-pointer hover:border-brand transition-colors"
            >
              <code className="text-lg font-mono font-bold text-brand">/link {code}</code>
              {copied ? <CheckCircle2 className="text-green-500" size={20} /> : <Copy className="text-muted" size={20} />}
            </div>
            <p className="text-xs text-center text-muted">Click to copy command</p>
            <button
              onClick={handleGenerate}
              disabled={loading || cooldown > 0}
              className="w-full mt-4 flex justify-center items-center gap-2 py-2 px-4 border border-brand/20 rounded-xl shadow-sm text-xs font-bold text-brand bg-brand/5 hover:bg-brand/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              {loading ? <Loader2 className="animate-spin" size={14} /> : (cooldown > 0 ? `Wait ${cooldown}s` : "Generate New Code")}
            </button>
          </div>
        )}
      </div>
    </SpatialCard>
  );
}
