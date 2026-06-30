"use client";

import { Newspaper, Loader2, Database } from "lucide-react";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { useRealtimeDigests } from "@/hooks/useRealtime";
import { toISTTime } from "@/lib/ist";

export default function AdminDigestsGrid() {
  const { digests, loading } = useRealtimeDigests();

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-20 relative">
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-widest text-foreground uppercase flex items-center gap-3">
            <Newspaper className="text-red-500 w-6 h-6" />
            Digest Archive
          </h1>
          <p className="text-muted text-sm mt-1">Real-time synchronized transmission records.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface border border-border-subtle shadow-sm shrink-0">
          <span className="text-xs font-bold text-muted uppercase tracking-widest">Total Generated:</span>
          {loading ? <Loader2 className="h-4 w-4 animate-spin text-red-500" /> : <span className="text-red-500 font-extrabold">{digests.length}</span>}
        </div>
      </div>

      <SpatialCard depth={4} className="glass rounded-3xl border border-border-subtle overflow-hidden shadow-sm">
        <div className="overflow-x-auto min-h-[500px]">
          <table className="w-full text-sm text-left relative">
            <thead className="text-xs text-muted uppercase bg-surface/80 border-b border-border-subtle sticky top-0 z-20 backdrop-blur-md">
              <tr>
                <th className="px-6 py-4 font-bold tracking-wider">Digest Topic</th>
                <th className="px-6 py-4 font-bold tracking-wider">Storage Path</th>
                <th className="px-6 py-4 font-bold tracking-wider">Issue Date</th>
                <th className="px-6 py-4 font-bold tracking-wider text-right">DB Timestamp (IST)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle/50">
              {loading ? (
                <tr>
                  <td colSpan={4} className="h-[400px]">
                    <div className="flex justify-center items-center h-full">
                      <Loader2 className="h-8 w-8 animate-spin text-red-500" />
                    </div>
                  </td>
                </tr>
              ) : digests.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-muted italic">
                    No digests have been generated yet.
                  </td>
                </tr>
              ) : (
                digests.map((digest) => (
                  <tr key={digest.id} className="group hover:bg-surface/50 transition-colors">
                    <td className="px-6 py-5 font-bold text-foreground capitalize">
                      {digest.topic.replace(/-/g, ' ')}
                    </td>
                    <td className="px-6 py-5">
                      <div className="inline-flex items-center gap-2 text-muted text-xs font-mono bg-background/50 px-2 py-1 rounded border border-border-subtle">
                        <Database size={12} className="text-brand" />
                        {digest.supabase_path}
                      </div>
                    </td>
                    <td className="px-6 py-5 text-muted font-medium">
                      {digest.generated_date_ist}
                    </td>
                    <td className="px-6 py-5 text-right text-xs font-bold tracking-wider uppercase text-brand">
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
