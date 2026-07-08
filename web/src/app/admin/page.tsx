"use client";

import { ShieldCheck, Activity, ShieldAlert, Cpu, Users, Newspaper, Download } from "lucide-react";
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

  const loadingUsers = loading;
  const loadingDigests = loading;

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
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-light opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-brand"></span>
            </span>
            Live Sync Active
          </div>
        </div>
      </header>

      {/* Top Metrics Row */}
      <section aria-label="Key Metrics" className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* System Status Card */}
        <SpatialCard depth={6} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group">
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
        <SpatialCard depth={6} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group">
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
            {loadingUsers ? (
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
        <SpatialCard depth={6} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group">
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
            {loadingDigests ? (
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

      {/* Live Feed Row */}
      <section aria-label="Live Telemetry Feeds" className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Registrations Feed */}
        <SpatialCard depth={3} className="glass rounded-3xl border border-border-subtle overflow-hidden flex flex-col h-[450px] shadow-sm">
          <header className="p-5 border-b border-border-subtle bg-surface/80 backdrop-blur-md flex justify-between items-center z-10">
            <h3 className="font-bold tracking-wider uppercase text-sm text-foreground flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-brand" />
              Recent Registrations
            </h3>
            <span className="text-xs font-bold text-muted bg-muted/10 px-2 py-1 rounded-md">{users.length} Total</span>
          </header>
          
          <div className="overflow-y-auto flex-1 p-3 flex flex-col gap-2 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
            {loadingUsers ? (
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="p-4 rounded-2xl bg-background/40 border border-transparent flex justify-between items-center animate-pulse">
                  <div className="space-y-2">
                    <div className="h-4 w-32 bg-muted/20 rounded" />
                    <div className="h-3 w-48 bg-muted/20 rounded" />
                  </div>
                  <div className="h-3 w-16 bg-muted/20 rounded" />
                </div>
              ))
            ) : users.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-muted gap-2">
                <Users className="w-8 h-8 opacity-20" />
                <p className="text-sm font-medium italic">No personnel found.</p>
              </div>
            ) : (
              <ul className="flex flex-col gap-2">
                {users.slice(0, 10).map((user) => (
                  <li key={user.id} className="group p-4 rounded-2xl bg-background/50 border border-border-subtle hover:border-brand/30 hover:bg-brand/5 hover:shadow-sm transition-all duration-300 flex justify-between items-center cursor-default">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-brand/10 text-brand flex items-center justify-center shrink-0 font-bold text-sm ring-1 ring-brand/20 group-hover:scale-110 transition-transform duration-300">
                        {user.full_name?.charAt(0).toUpperCase() || "A"}
                      </div>
                      <div className="group-hover:translate-x-1 transition-transform duration-300">
                        <p className="font-bold text-sm text-foreground">{user.full_name || "Unknown Agent"}</p>
                        <p className="text-xs text-muted font-medium mt-0.5">{user.email}</p>
                      </div>
                    </div>
                    <div className="text-xs text-brand/80 font-bold uppercase tracking-wider group-hover:text-brand transition-colors">
                      {toISTTime(user.created_at)}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </SpatialCard>

        {/* Transmissions Feed */}
        <SpatialCard depth={3} className="glass rounded-3xl border border-border-subtle overflow-hidden flex flex-col h-[450px] shadow-sm">
          <header className="p-5 border-b border-border-subtle bg-surface/80 backdrop-blur-md flex justify-between items-center z-10">
            <h3 className="font-bold tracking-wider uppercase text-sm text-foreground flex items-center gap-2">
              <Newspaper className="w-4 h-4 text-brand" />
              Recent Transmissions
            </h3>
            <span className="text-xs font-bold text-muted bg-muted/10 px-2 py-1 rounded-md">{digests.length} Total</span>
          </header>
          
          <div className="overflow-y-auto flex-1 p-3 flex flex-col gap-2 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
            {loadingDigests ? (
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="p-4 rounded-2xl bg-background/40 border border-transparent flex justify-between items-center animate-pulse">
                  <div className="space-y-2">
                    <div className="h-4 w-40 bg-muted/20 rounded" />
                    <div className="h-3 w-24 bg-muted/20 rounded" />
                  </div>
                  <div className="h-3 w-16 bg-muted/20 rounded" />
                </div>
              ))
            ) : digests.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-muted gap-2">
                <Newspaper className="w-8 h-8 opacity-20" />
                <p className="text-sm font-medium italic">No broadcasts available.</p>
              </div>
            ) : (
              <ul className="flex flex-col gap-2">
                {digests.slice(0, 10).map((digest) => (
                  <li key={digest.id} className="group p-4 rounded-2xl bg-background/50 border border-border-subtle hover:border-brand/30 hover:bg-brand/5 hover:shadow-sm transition-all duration-300 flex justify-between items-center cursor-default">
                    <div className="flex items-center gap-3">
                       <div className="w-10 h-10 rounded-xl bg-brand/10 text-brand flex items-center justify-center shrink-0 ring-1 ring-brand/20 group-hover:rotate-6 transition-transform duration-300">
                        <Newspaper className="w-5 h-5" />
                      </div>
                      <div className="group-hover:translate-x-1 transition-transform duration-300">
                        <p className="font-bold text-sm text-foreground capitalize truncate max-w-[150px] sm:max-w-[200px]">
                          {(digest.topic || "Unknown").replace(/-/g, ' ').replace(/^v4:/, '')}
                        </p>
                        <p className="text-xs text-muted font-medium mt-0.5">{digest.generated_date_ist}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1 shrink-0">
                      <div className="text-[10px] text-brand/80 font-bold uppercase tracking-wider group-hover:text-brand transition-colors">
                        {toISTTime(digest.created_at)}
                      </div>
                      {digest.supabase_path ? (
                        <Link 
                          href={`${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/daily-digests/${digest.supabase_path}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-brand hover:bg-brand-light text-white rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all duration-300 shadow-sm hover:-translate-y-0.5"
                        >
                          <Download size={12} /> <span className="hidden sm:inline">Download</span>
                        </Link>
                      ) : digest.file_id ? (
                        <Link 
                          href={`/api/download?file_id=${digest.file_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-brand hover:bg-brand-light text-white rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all duration-300 shadow-sm hover:-translate-y-0.5"
                        >
                          <Download size={12} /> <span className="hidden sm:inline">Download</span>
                        </Link>
                      ) : (
                        <span className="text-[10px] text-muted italic inline-flex items-center gap-1 px-2.5 py-1.5 bg-surface border border-border-subtle rounded-lg"><Activity size={10} className="animate-pulse" /> Processing</span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </SpatialCard>
      </section>
    </main>
  );
}
