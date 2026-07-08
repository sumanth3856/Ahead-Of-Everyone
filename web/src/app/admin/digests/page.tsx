"use client";

import { Newspaper, Loader2, Database } from "lucide-react";
import { useEffect, useState } from "react";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { getAdminTelemetry } from "../actions";
import { toISTTime } from "@/lib/ist";

export default function AdminDigestsGrid() {
  const [digests, setDigests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchTelemetry = async () => {
      try {
        const data = await getAdminTelemetry();
        if (mounted) {
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

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-20 relative">
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-foreground uppercase flex items-center gap-3">
            <Newspaper className="text-brand w-8 h-8" />
            Digest Archive
          </h1>
          <p className="text-muted text-sm mt-2 font-medium">Real-time synchronized transmission records.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface border border-border-subtle shadow-sm shrink-0">
          <span className="text-xs font-bold text-muted uppercase tracking-widest">Total Generated:</span>
          {loading ? <Loader2 className="h-4 w-4 animate-spin text-brand" /> : <span className="text-brand font-black">{digests.length}</span>}
        </div>
      </div>

      <SpatialCard depth={4} className="glass rounded-3xl border border-border-subtle overflow-hidden shadow-sm">
        <div className="overflow-x-auto min-h-[500px]">
          <table className="w-full text-sm text-left relative">
            <thead className="text-[11px] text-muted uppercase bg-gradient-to-r from-surface/80 to-surface/40 border-b border-border-subtle sticky top-0 z-20 backdrop-blur-md">
              <tr>
                <th className="px-8 py-5 font-extrabold tracking-widest">Digest Topic</th>
                <th className="px-8 py-5 font-extrabold tracking-widest">Storage Path</th>
                <th className="px-8 py-5 font-extrabold tracking-widest">Issue Date</th>
                <th className="px-8 py-5 font-extrabold tracking-widest text-right">DB Timestamp (IST)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle/30">
              {loading ? (
                <tr>
                  <td colSpan={4} className="h-[400px]">
                    <div className="flex justify-center items-center h-full">
                      <Loader2 className="h-8 w-8 animate-spin text-brand" />
                    </div>
                  </td>
                </tr>
              ) : digests.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-8 py-12 text-center text-muted italic">
                    <div className="flex flex-col items-center justify-center gap-3">
                      <Newspaper className="w-10 h-10 opacity-30 text-brand" />
                      No digests have been generated yet.
                    </div>
                  </td>
                </tr>
              ) : (
                digests.map((digest) => (
                  <tr key={digest.id} className="group hover:bg-brand/5 even:bg-surface/30 transition-all duration-300 relative">
                    <td className="px-8 py-6 relative">
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand scale-y-0 group-hover:scale-y-100 transition-transform origin-center" />
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand/20 to-brand/5 border border-brand/20 flex items-center justify-center text-brand font-black shadow-sm shrink-0 group-hover:scale-110 group-hover:shadow-md group-hover:border-brand/40 transition-all duration-300">
                          <Newspaper className="w-5 h-5" />
                        </div>
                        <span className="font-extrabold text-foreground capitalize group-hover:text-brand transition-colors text-base">
                          {(digest.topic || "Unknown").replace(/-/g, ' ').replace(/^v4:/, '')}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <div className="inline-flex items-center gap-2 text-muted text-xs font-mono bg-background/80 px-3 py-1.5 rounded-lg border border-border-subtle shadow-inner group-hover:border-brand/30 transition-colors">
                        <Database size={12} className="text-brand opacity-70" />
                        {digest.supabase_path || 'Generating...'}
                      </div>
                    </td>
                    <td className="px-8 py-6 text-[13px] font-semibold text-muted">
                      {digest.generated_date_ist}
                    </td>
                    <td className="px-8 py-6 text-right text-[11px] font-bold tracking-widest uppercase text-brand">
                      {toISTTime(digest.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </SpatialCard>
    </div>
  );
}
