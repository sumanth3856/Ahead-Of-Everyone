"use client";

import { useState } from "react";
import { toast } from "sonner";
import { insertAdminCommand } from "@/app/dashboard/actions";
import { SpatialCard } from "@/components/ui/SpatialCard";

import { ShieldAlert, Send, Terminal, Loader2, KeyRound } from "lucide-react";

export function AdminOperationsClient() {
  const [broadcasting, setBroadcasting] = useState(false);
  const [updatingToken, setUpdatingToken] = useState(false);
  const [token, setToken] = useState("");

  const handleBroadcast = async () => {
    setBroadcasting(true);
    toast.info("Initializing global broadcast sequence...");
    try {
      await insertAdminCommand("broadcast_digests", { timestamp: Date.now() });
      toast.success("Broadcast command sent to central processing!");
    } catch (e: any) {
      toast.error(e.message || "Failed to initiate broadcast.");
    } finally {
      setBroadcasting(false);
    }
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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      {/* Broadcast Override */}
      <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle shadow-sm flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-lg bg-brand/10 border border-brand/20">
              <Send className="h-6 w-6 text-brand" />
            </div>
            <h2 className="font-bold tracking-wide uppercase text-sm text-foreground">Global Broadcast</h2>
          </div>
          <p className="text-sm text-muted mb-6">
            Manually override the schedule and force the Python backend to generate and broadcast the Daily Digest immediately.
          </p>
        </div>
        
        <button 
          onClick={handleBroadcast}
          disabled={broadcasting}
          className="w-full flex justify-center items-center gap-2 py-4 px-4 border border-transparent rounded-xl shadow-spatial text-sm font-bold text-white bg-red-600 hover:bg-red-500 transition-all duration-300"
        >
          {broadcasting ? <Loader2 className="animate-spin" size={18} /> : (
            <>
              <ShieldAlert size={18} /> INITIATE BROADCAST
            </>
          )}
        </button>
      </SpatialCard>

      {/* Crisis Management (Token Update) */}
      <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle shadow-sm flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
              <Terminal className="h-6 w-6 text-orange-500" />
            </div>
            <h2 className="font-bold tracking-wide uppercase text-sm text-foreground">Crisis Management</h2>
          </div>
          <p className="text-sm text-muted mb-6">
            In the event of a Telegram Bot ban, input the new bot token here. The backend will automatically reboot with the new credentials.
          </p>
        </div>
        
        <div className="flex flex-col gap-3">
          <div className="relative">
            <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input 
              type="text" 
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste new bot token (e.g. 1234:ABC...)" 
              className="w-full bg-surface border border-border-subtle rounded-xl py-3 pl-10 pr-4 text-sm text-foreground placeholder:text-muted focus:border-orange-500 focus:ring-1 focus:ring-orange-500/30 transition-all outline-none"
            />
          </div>
          <button 
            onClick={handleUpdateToken}
            disabled={updatingToken}
            className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-orange-500/30 rounded-xl shadow-sm text-sm font-bold text-orange-500 bg-orange-500/10 hover:bg-orange-500/20 transition-all duration-300"
          >
            {updatingToken ? <Loader2 className="animate-spin" size={18} /> : "Update Bot Configuration"}
          </button>
        </div>
      </SpatialCard>
    </div>
  );
}
