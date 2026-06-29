"use client";

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { insertAdminCommand } from "@/app/dashboard/actions";
import { SpatialCard } from "@/components/ui/SpatialCard";

import { Send, Terminal, Loader2, KeyRound, Zap, AlertTriangle, CheckCircle2, Radio } from "lucide-react";

type BroadcastPhase = "idle" | "armed" | "broadcasting" | "success" | "error";

export function AdminOperationsClient() {
  const [phase, setPhase] = useState<BroadcastPhase>("idle");
  const [armCountdown, setArmCountdown] = useState(0);
  const [cooldown, setCooldown] = useState(0);

  const [updatingToken, setUpdatingToken] = useState(false);
  const [token, setToken] = useState("");

  // Auto-disarm after countdown expires
  useEffect(() => {
    if (phase !== "armed" || armCountdown <= 0) return;
    const timer = setInterval(() => {
      setArmCountdown(prev => {
        if (prev <= 1) {
          setPhase("idle");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [phase, armCountdown]);

  // Cooldown after success
  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => {
      setCooldown(prev => {
        if (prev <= 1) return 0;
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  const handleBroadcastClick = useCallback(async () => {
    if (phase === "idle") {
      setPhase("armed");
      setArmCountdown(10);
      return;
    }
    if (phase === "armed") {
      setPhase("broadcasting");
      try {
        await insertAdminCommand("broadcast_digests", { timestamp: Date.now() });
        setPhase("success");
        setCooldown(30);
        toast.success("Broadcast command dispatched successfully!");
      } catch (e: any) {
        setPhase("error");
        toast.error(e.message || "Failed to initiate broadcast.");
        setTimeout(() => setPhase("idle"), 3000);
      }
    }
  }, [phase]);

  const handleCancel = () => {
    setPhase("idle");
    setArmCountdown(0);
  };

  const handleUpdateToken = async () => {
    if (!token.trim()) {
      toast.error("Please enter a valid bot token.");
      return;
    }
    setUpdatingToken(true);
    toast.info("Updating Telegram Bot configuration...");
    try {
      await insertAdminCommand("update_telegram_token", { new_token: token.trim() });
      toast.success("Bot token update command sent!");
      setToken("");
    } catch (e: any) {
      toast.error(e.message || "Failed to update token.");
    } finally {
      setUpdatingToken(false);
    }
  };

  // Render broadcast button based on phase
  const renderBroadcastContent = () => {
    switch (phase) {
      case "idle":
        return (
          <button 
            onClick={handleBroadcastClick}
            disabled={cooldown > 0}
            className="w-full flex justify-center items-center gap-3 py-4 px-6 rounded-2xl text-sm font-bold text-white bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 shadow-lg shadow-red-500/20 hover:shadow-red-500/40 transition-all duration-300 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <Zap size={18} />
            {cooldown > 0 ? `COOLDOWN ${cooldown}s` : "INITIATE BROADCAST"}
          </button>
        );

      case "armed":
        return (
          <div className="space-y-3">
            {/* Warning banner */}
            <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
              <div className="relative shrink-0">
                <div className="absolute inset-0 bg-red-500/30 blur-md rounded-full animate-pulse" />
                <AlertTriangle className="h-5 w-5 text-red-500 relative z-10" />
              </div>
              <div className="flex-1">
                <p className="text-red-500 text-xs font-bold uppercase tracking-wider">Broadcast Armed</p>
                <p className="text-muted text-xs mt-0.5">This will send digests to all linked agents. Auto-cancels in {armCountdown}s.</p>
              </div>
            </div>

            {/* Countdown progress bar */}
            <div className="w-full h-1.5 bg-surface rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full transition-all duration-1000 ease-linear"
                style={{ width: `${(armCountdown / 10) * 100}%` }}
              />
            </div>

            {/* Action buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleCancel}
                className="flex-1 flex justify-center items-center gap-2 py-3.5 px-4 rounded-2xl text-sm font-bold text-muted bg-surface border border-border-subtle hover:bg-surface-hover transition-all duration-200 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleBroadcastClick}
                className="flex-1 flex justify-center items-center gap-2 py-3.5 px-4 rounded-2xl text-sm font-bold text-white bg-red-600 hover:bg-red-500 shadow-lg shadow-red-500/30 transition-all duration-200 active:scale-[0.97] cursor-pointer animate-pulse"
              >
                <Radio size={16} />
                CONFIRM BROADCAST
              </button>
            </div>
          </div>
        );

      case "broadcasting":
        return (
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="relative">
              <div className="absolute inset-0 bg-red-500/20 blur-xl rounded-full animate-pulse" />
              <Loader2 className="h-8 w-8 text-red-500 animate-spin relative z-10" />
            </div>
            <div className="text-center">
              <p className="text-sm font-bold text-foreground">Broadcasting in progress...</p>
              <p className="text-xs text-muted mt-1">Dispatching to central processing pipeline</p>
            </div>
          </div>
        );

      case "success":
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-4 rounded-xl bg-green-500/10 border border-green-500/20">
              <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
              <div>
                <p className="text-green-500 text-xs font-bold uppercase tracking-wider">Broadcast Dispatched</p>
                <p className="text-muted text-xs mt-0.5">The pipeline is processing your request.</p>
              </div>
            </div>
            <button
              disabled={cooldown > 0}
              onClick={() => setPhase("idle")}
              className="w-full flex justify-center items-center gap-3 py-4 px-6 rounded-2xl text-sm font-bold text-muted bg-surface border border-border-subtle transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              {cooldown > 0 ? `Available in ${cooldown}s` : "Ready for new broadcast"}
            </button>
          </div>
        );

      case "error":
        return (
          <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
            <AlertTriangle className="h-5 w-5 text-red-500 shrink-0" />
            <div>
              <p className="text-red-500 text-xs font-bold uppercase tracking-wider">Broadcast Failed</p>
              <p className="text-muted text-xs mt-0.5">Resetting in a moment...</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

      {/* Broadcast Override */}
      <SpatialCard depth={8} className="glass rounded-3xl border border-border-subtle shadow-sm flex flex-col relative overflow-hidden group">
        {/* Top accent — changes color based on phase */}
        <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent to-transparent transition-all duration-500 ${
          phase === "armed" ? "via-orange-500/80" :
          phase === "broadcasting" ? "via-yellow-500/80 animate-pulse" :
          phase === "success" ? "via-green-500/80" :
          "via-red-500/60"
        }`} />
        
        <div className="p-8 flex flex-col flex-grow">
          <div className="flex items-center gap-4 mb-6">
            <div className="relative">
              <div className={`absolute inset-0 blur-lg rounded-full transition-opacity duration-500 ${
                phase === "armed" ? "bg-orange-500/30 opacity-100" :
                phase === "broadcasting" ? "bg-yellow-500/30 opacity-100 animate-pulse" :
                phase === "success" ? "bg-green-500/30 opacity-100" :
                "bg-red-500/20 opacity-0 group-hover:opacity-100"
              }`} />
              <div className={`p-3.5 rounded-2xl border relative z-10 transition-colors duration-300 ${
                phase === "armed" ? "bg-orange-500/10 border-orange-500/20" :
                phase === "success" ? "bg-green-500/10 border-green-500/20" :
                "bg-red-500/10 border-red-500/20"
              }`}>
                {phase === "success" ? (
                  <CheckCircle2 className="h-6 w-6 text-green-500" />
                ) : phase === "broadcasting" ? (
                  <Loader2 className="h-6 w-6 text-yellow-500 animate-spin" />
                ) : (
                  <Send className={`h-6 w-6 ${phase === "armed" ? "text-orange-500" : "text-red-500"}`} />
                )}
              </div>
            </div>
            <div>
              <h2 className="font-bold tracking-wider uppercase text-sm text-foreground">Global Broadcast</h2>
              <p className="text-xs text-muted mt-0.5">Force immediate digest generation</p>
            </div>
          </div>
          
          <p className="text-sm text-muted mb-8 leading-relaxed flex-grow">
            Manually override the scheduled pipeline and force the Python backend to generate and broadcast the Daily Digest to all linked agents immediately.
          </p>

          {renderBroadcastContent()}
        </div>
      </SpatialCard>

      {/* Crisis Management (Token Update) */}
      <SpatialCard depth={8} className="glass rounded-3xl border border-border-subtle shadow-sm flex flex-col relative overflow-hidden group">
        {/* Subtle top accent line */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-orange-500/60 to-transparent" />
        
        <div className="p-8 flex flex-col flex-grow">
          <div className="flex items-center gap-4 mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-orange-500/20 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="p-3.5 rounded-2xl bg-orange-500/10 border border-orange-500/20 relative z-10">
                <Terminal className="h-6 w-6 text-orange-500" />
              </div>
            </div>
            <div>
              <h2 className="font-bold tracking-wider uppercase text-sm text-foreground">Crisis Management</h2>
              <p className="text-xs text-muted mt-0.5">Emergency bot token rotation</p>
            </div>
          </div>
          
          <p className="text-sm text-muted mb-8 leading-relaxed flex-grow">
            In the event of a Telegram Bot ban or token compromise, input the new bot token here. The backend will automatically reboot with the new credentials.
          </p>

          <div className="flex flex-col gap-3">
            <div className="relative group/input">
              <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within/input:text-orange-500 transition-colors" />
              <input 
                type="text" 
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Paste new bot token (e.g. 1234:ABC...)" 
                className="w-full bg-surface border border-border-subtle rounded-2xl py-4 pl-11 pr-4 text-sm text-foreground placeholder:text-muted/60 focus:border-orange-500/50 focus:ring-2 focus:ring-orange-500/20 transition-all outline-none"
              />
            </div>
            <button 
              onClick={handleUpdateToken}
              disabled={updatingToken || !token.trim()}
              className="w-full flex justify-center items-center gap-3 py-4 px-6 rounded-2xl text-sm font-bold text-orange-500 bg-orange-500/10 border border-orange-500/20 hover:bg-orange-500/20 hover:border-orange-500/30 shadow-sm hover:shadow-orange-500/10 transition-all duration-300 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              {updatingToken ? <Loader2 className="animate-spin" size={18} /> : "Update Bot Configuration"}
            </button>
          </div>
        </div>
      </SpatialCard>
    </div>
  );
}
