"use client";

import { ShieldCheck, Activity, ShieldAlert, Cpu, Users, Newspaper, Download, Loader2, Play, RefreshCw, FileText, Zap } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { toISTTime } from "@/lib/ist";
import { getAdminTelemetry } from "./actions";
import ThemeToggle from "@/components/ThemeToggle";

export default function AdminDashboardOverview() {
  const [users, setUsers] = useState<any[]>([]);
  const [digests, setDigests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [broadcasting, setBroadcasting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{
    title: string;
    description: string;
    onConfirm: () => void;
    confirmText: string;
    confirmColor: string;
  } | null>(null);

  useEffect(() => {
    let mounted = true;
    
    const fetchTelemetry = async () => {
      try {
        const data = await getAdminTelemetry();
        if (mounted) {
          setUsers(data.users);
          setDigests(data.digests);
          setLoading(false);
        }
      } catch (err) {
        console.error("Failed to fetch telemetry:", err);
      }
    };

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 3000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const activityFeed = [
    ...users.map((u: any) => ({ _type: 'user', ...u })),
    ...digests.map((d: any) => ({ _type: 'digest', ...d }))
  ].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const requestBroadcast = () => {
    setConfirmAction({
      title: "Confirm Broadcast",
      description: "Are you sure you want to trigger an on-demand AI scraping cycle? This will query external sources and consume API quota.",
      confirmText: "Trigger Broadcast",
      confirmColor: "bg-brand",
      onConfirm: async () => {
        setConfirmAction(null);
        try {
          setBroadcasting(true);
          const { triggerBroadcastCommand } = await import("./actions");
          await triggerBroadcastCommand();
          alert("Broadcast command queued successfully.");
        } catch (err: any) {
          alert(err.message || "Failed to trigger broadcast.");
        } finally {
          setBroadcasting(false);
        }
      }
    });
  };

  const requestSync = () => {
    setConfirmAction({
      title: "Force System Sync",
      description: "This will invalidate all Next.js caches and force a fresh data pull from Supabase across the entire dashboard. Proceed?",
      confirmText: "Sync Now",
      confirmColor: "bg-blue-500",
      onConfirm: async () => {
        setConfirmAction(null);
        try {
          setSyncing(true);
          const { forceSystemSync } = await import("./actions");
          await forceSystemSync();
          alert("System sync triggered.");
        } catch (err: any) {
          alert(err.message || "Failed to sync system.");
        } finally {
          setSyncing(false);
        }
      }
    });
  };

  const requestExport = () => {
    if (!activityFeed.length) {
      alert("No data to export");
      return;
    }
    setConfirmAction({
      title: "Export Telemetry",
      description: `You are about to export ${activityFeed.length} event records as a CSV file. Do you want to continue?`,
      confirmText: "Download CSV",
      confirmColor: "bg-purple-500",
      onConfirm: () => {
        setConfirmAction(null);
        const headers = ["Event Type", "Date (IST)", "User Name", "Email", "Digest Topic", "Status"];
        const rows = activityFeed.map((item: any) => {
          const isUser = item._type === 'user';
          return [
            isUser ? "Registration" : "Broadcast",
            toISTTime(item.created_at),
            isUser ? `"${item.full_name || ''}"` : "",
            isUser ? `"${item.email || ''}"` : "",
            !isUser ? `"${(item.topic || '').replace(/"/g, '""')}"` : "",
            !isUser ? (item.supabase_path || item.file_id ? "Completed" : "Generating") : "Active"
          ].join(",");
        });
        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows].join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `system-telemetry-${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    });
  };

  return (
    <main className="max-w-6xl mx-auto flex flex-col gap-10 pb-20 relative">
      {/* Elegant Glowing Background Orbs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-brand/5 blur-[120px] rounded-full pointer-events-none -z-10 mix-blend-screen" />
      <div className="absolute top-1/4 right-0 w-[400px] h-[400px] bg-brand-light/5 blur-[100px] rounded-full pointer-events-none -z-10 mix-blend-screen" />

      {/* Header */}
      <header className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-fluid-3 font-extrabold tracking-tight uppercase flex items-center gap-3">
            <ShieldAlert className="text-brand w-8 h-8 shrink-0" />
            <span className="text-foreground drop-shadow-sm">
              Command Center
            </span>
          </h1>
          <p className="text-muted text-sm mt-2 font-medium">Global System Overview & Real-Time Telemetry.</p>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <div className="flex items-center gap-3 px-4 py-2 rounded-full border border-brand/30 bg-brand/10 text-brand text-xs tracking-widest uppercase font-bold shrink-0 shadow-sm transition-all hover:bg-brand/20">
            {loading ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-light opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand"></span>
              </span>
            )}
            Live Sync {loading ? "..." : "Active"}
          </div>
        </div>
      </header>

      {/* Top Metrics Row */}
      <section aria-label="Key Metrics" className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* System Status Card */}
        <SpatialCard depth={6} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group hover:-translate-y-1 hover:shadow-lg hover:border-brand/40 transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-[0.02] group-hover:opacity-[0.06] transition-opacity duration-700 -translate-y-4 translate-x-4 pointer-events-none">
            <Activity className="w-32 h-32 text-brand" />
          </div>
          <div className="flex items-center justify-between mb-4 relative z-10">
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">System Status</h3>
            <div className="p-2.5 rounded-xl bg-brand/10 text-brand shadow-sm ring-1 ring-brand/20">
              <Activity className="h-5 w-5" />
            </div>
          </div>
          <div className="h-10 flex items-center relative z-10">
            <p className="text-4xl font-black text-foreground flex items-baseline gap-1 drop-shadow-sm">
              100<span className="text-xl text-brand font-bold">%</span>
            </p>
          </div>
          <p className="text-brand text-sm font-semibold mt-2">All pipelines operational</p>
        </SpatialCard>
        
        {/* Total Personnel Card */}
        <SpatialCard depth={6} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group hover:-translate-y-1 hover:shadow-lg hover:border-brand/40 transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-[0.02] group-hover:opacity-[0.06] transition-opacity duration-700 -translate-y-4 translate-x-4 pointer-events-none">
            <Users className="w-32 h-32 text-brand" />
          </div>
          <div className="flex items-center justify-between mb-4 relative z-10">
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Total Personnel</h3>
            <div className="p-2.5 rounded-xl bg-brand/10 text-brand shadow-sm ring-1 ring-brand/20">
              <Users className="h-5 w-5" />
            </div>
          </div>
          <div className="h-10 flex items-center relative z-10">
            {loading ? (
              <div className="h-8 w-16 bg-muted/20 animate-pulse rounded-md" role="status" aria-label="Loading users count" />
            ) : (
              <p className="text-4xl font-black text-foreground drop-shadow-sm">
                {users.length}
              </p>
            )}
          </div>
          <p className="text-muted text-sm font-semibold mt-2">Registered agents</p>
        </SpatialCard>

        {/* Newsletters Sent Card */}
        <SpatialCard depth={6} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group hover:-translate-y-1 hover:shadow-lg hover:border-brand/40 transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-[0.02] group-hover:opacity-[0.06] transition-opacity duration-700 -translate-y-4 translate-x-4 pointer-events-none">
            <Cpu className="w-32 h-32 text-brand" />
          </div>
          <div className="flex items-center justify-between mb-4 relative z-10">
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Newsletters Sent</h3>
            <div className="p-2.5 rounded-xl bg-brand/10 text-brand shadow-sm ring-1 ring-brand/20">
              <Cpu className="h-5 w-5" />
            </div>
          </div>
          <div className="h-10 flex items-center relative z-10">
            {loading ? (
              <div className="h-8 w-16 bg-muted/20 animate-pulse rounded-md" role="status" aria-label="Loading digests count" />
            ) : (
              <p className="text-4xl font-black text-foreground drop-shadow-sm">
                {digests.length}
              </p>
            )}
          </div>
          <p className="text-muted text-sm font-semibold mt-2">Broadcasts completed</p>
        </SpatialCard>
      </section>

      {/* Middle Row: Quick Actions */}
      <section aria-label="Quick Actions" className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <button onClick={requestBroadcast} disabled={broadcasting} className="group relative overflow-hidden rounded-3xl bg-surface/80 border border-border-subtle p-5 hover:bg-brand/10 hover:border-brand/30 transition-all duration-300 text-left shadow-sm hover:shadow-lg hover:-translate-y-1 disabled:opacity-50 disabled:pointer-events-none">
          <div className="absolute right-0 top-0 p-4 opacity-[0.03] group-hover:opacity-[0.1] transition-opacity duration-500 pointer-events-none transform group-hover:scale-110">
            <Play className="w-24 h-24 text-brand" />
          </div>
          <div className="w-10 h-10 rounded-xl bg-brand/10 text-brand flex items-center justify-center mb-3 ring-1 ring-brand/20 group-hover:scale-110 group-hover:rotate-6 transition-transform duration-300">
            {broadcasting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5 fill-brand/20" />}
          </div>
          <h3 className="text-foreground font-extrabold text-sm tracking-wide mb-1 uppercase">Broadcast Custom Digest</h3>
          <p className="text-xs text-muted font-medium">Trigger an on-demand AI scraping cycle.</p>
        </button>

        <button onClick={requestSync} disabled={syncing} className="group relative overflow-hidden rounded-3xl bg-surface/80 border border-border-subtle p-5 hover:bg-blue-500/10 hover:border-blue-500/30 transition-all duration-300 text-left shadow-sm hover:shadow-lg hover:-translate-y-1 disabled:opacity-50 disabled:pointer-events-none">
          <div className="absolute right-0 top-0 p-4 opacity-[0.03] group-hover:opacity-[0.1] transition-opacity duration-500 pointer-events-none transform group-hover:scale-110">
            <RefreshCw className="w-24 h-24 text-blue-500" />
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center mb-3 ring-1 ring-blue-500/20 group-hover:scale-110 group-hover:rotate-180 transition-transform duration-700">
            {syncing ? <Loader2 className="w-5 h-5 animate-spin" /> : <RefreshCw className="w-5 h-5" />}
          </div>
          <h3 className="text-foreground font-extrabold text-sm tracking-wide mb-1 uppercase">Force System Sync</h3>
          <p className="text-xs text-muted font-medium">Invalidate cache and refresh databases.</p>
        </button>

        <button onClick={requestExport} className="group relative overflow-hidden rounded-3xl bg-surface/80 border border-border-subtle p-5 hover:bg-purple-500/10 hover:border-purple-500/30 transition-all duration-300 text-left shadow-sm hover:shadow-lg hover:-translate-y-1">
          <div className="absolute right-0 top-0 p-4 opacity-[0.03] group-hover:opacity-[0.1] transition-opacity duration-500 pointer-events-none transform group-hover:scale-110">
            <FileText className="w-24 h-24 text-purple-500" />
          </div>
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-500 flex items-center justify-center mb-3 ring-1 ring-purple-500/20 group-hover:scale-110 transition-transform duration-300">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="text-foreground font-extrabold text-sm tracking-wide mb-1 uppercase">Export Telemetry</h3>
          <p className="text-xs text-muted font-medium">Download CSV reports of system activity.</p>
        </button>
      </section>

      {/* Global Activity Stream */}
      <section aria-label="Global Activity Stream">
        <SpatialCard depth={3} className="glass rounded-3xl border border-border-subtle overflow-hidden flex flex-col min-h-[600px] shadow-sm">
          <header className="p-5 border-b border-border-subtle bg-surface/80 backdrop-blur-md flex justify-between items-center z-10 sticky top-0">
            <h3 className="font-bold tracking-wider uppercase text-sm text-foreground flex items-center gap-2">
              <Zap className="w-4 h-4 text-brand" />
              Global Activity Stream
            </h3>
            <span className="text-xs font-bold text-muted bg-muted/10 px-3 py-1 rounded-full border border-border-subtle">{activityFeed.length} Events Logged</span>
          </header>
          
          <div className="overflow-x-auto flex-1">
            {loading ? (
              <div className="p-5 flex flex-col gap-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="p-4 rounded-2xl bg-background/40 border border-transparent flex justify-between items-center animate-pulse">
                    <div className="flex gap-4 items-center w-full">
                      <div className="w-10 h-10 bg-muted/20 rounded-full shrink-0" />
                      <div className="space-y-2 flex-1">
                        <div className="h-4 w-40 bg-muted/20 rounded" />
                        <div className="h-3 w-24 bg-muted/20 rounded" />
                      </div>
                      <div className="h-3 w-16 bg-muted/20 rounded shrink-0" />
                    </div>
                  </div>
                ))}
              </div>
            ) : activityFeed.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-muted gap-3 bg-background/30 rounded-2xl border border-dashed border-border-subtle p-6 m-2">
                <Zap className="w-10 h-10 opacity-30 animate-pulse text-brand" />
                <p className="text-sm font-medium tracking-wide">No system activity logged.</p>
              </div>
            ) : (
              <table className="w-full text-sm text-left relative border-collapse">
                <thead className="text-xs text-muted uppercase bg-surface/80 border-b border-border-subtle sticky top-0 z-20 backdrop-blur-md">
                  <tr>
                    <th className="px-6 py-4 font-bold tracking-wider">Event Type</th>
                    <th className="px-6 py-4 font-bold tracking-wider">Entity Details</th>
                    <th className="px-6 py-4 font-bold tracking-wider">Timestamp (IST)</th>
                    <th className="px-6 py-4 font-bold tracking-wider text-right">Action / Link</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle/50">
                  {activityFeed.slice(0, 50).map((item: any) => {
                    const isUser = item._type === 'user';
                    const Icon = isUser ? Users : Newspaper;
                    const colorClass = isUser ? 'text-blue-500 bg-blue-500/10 border-blue-500/20' : 'text-brand bg-brand/10 border-brand/20';
                    
                    return (
                      <tr key={`${item._type}-${item.id}`} className="group hover:bg-surface/50 transition-colors">
                        <td className="px-6 py-5">
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center border ${colorClass} shrink-0`}>
                              <Icon className="w-4 h-4" />
                            </div>
                            <span className="font-bold text-foreground tracking-wide uppercase text-xs">
                              {isUser ? "Registration" : "Broadcast"}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-5">
                          <div className="flex flex-col">
                            <span className="font-bold text-foreground capitalize">
                              {isUser ? (item.full_name || "Unknown Agent") : (item.topic || "Unknown").replace(/-/g, ' ').replace(/^v4:/, '')}
                            </span>
                            <span className="text-xs text-muted font-medium mt-0.5">
                              {isUser ? item.email : item.generated_date_ist}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-5 text-xs font-bold tracking-wider uppercase text-muted">
                          {toISTTime(item.created_at)}
                        </td>
                        <td className="px-6 py-5 text-right">
                          {isUser ? (
                            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface border border-border-subtle text-muted text-[10px] font-bold uppercase tracking-wider shadow-sm">
                              User Joined
                            </div>
                          ) : (
                            item.supabase_path ? (
                              <Link 
                                href={`${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/daily-digests/${item.supabase_path}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand hover:bg-brand-light text-white rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all duration-300 shadow-sm hover:-translate-y-0.5 active:scale-95"
                              >
                                <Download size={12} /> <span className="hidden sm:inline">PDF</span>
                              </Link>
                            ) : item.file_id ? (
                              <Link 
                                href={`/api/download?file_id=${item.file_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand hover:bg-brand-light text-white rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all duration-300 shadow-sm hover:-translate-y-0.5 active:scale-95"
                              >
                                <Download size={12} /> <span className="hidden sm:inline">PDF</span>
                              </Link>
                            ) : (
                              <span className="text-[10px] text-muted italic inline-flex items-center gap-1 px-3 py-1.5 bg-background border border-border-subtle rounded-lg shadow-inner"><Activity size={10} className="animate-pulse text-brand" /> Generating</span>
                            )
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </SpatialCard>
      </section>

      {/* Confirmation Modal Overlay */}
      {confirmAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-surface border border-border-subtle rounded-3xl p-8 max-w-md w-full shadow-2xl relative overflow-hidden animate-in zoom-in-95 duration-200">
            <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-current to-transparent opacity-50 ${confirmAction.confirmColor.replace('bg-', 'text-')}`} />
            <h2 className="text-xl font-black text-foreground mb-3">{confirmAction.title}</h2>
            <p className="text-muted text-sm mb-8 leading-relaxed">
              {confirmAction.description}
            </p>
            <div className="flex gap-3 justify-end">
              <button 
                onClick={() => setConfirmAction(null)}
                className="px-5 py-2.5 rounded-full text-sm font-bold text-foreground bg-surface border border-border-subtle hover:bg-muted/10 transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={confirmAction.onConfirm}
                className={`px-5 py-2.5 rounded-full text-sm font-bold text-white shadow-md hover:shadow-lg transition-all ${confirmAction.confirmColor} hover:brightness-110`}
              >
                {confirmAction.confirmText}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
