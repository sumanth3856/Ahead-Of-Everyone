"use client";

import { useState } from "react";
import { Send, CheckCircle2, Loader2, Copy } from "lucide-react";
import { generateTelegramLinkCode } from "@/app/dashboard/actions";
import { SpatialCard } from "@/components/ui/SpatialCard";

export default function LinkTelegramClient() {
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const newCode = await generateTelegramLinkCode();
      setCode(newCode);
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
            disabled={loading}
            className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-brand hover:opacity-90 transition-all duration-300"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : "Generate Link Code"}
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
          </div>
        )}
      </div>
    </SpatialCard>
  );
}
