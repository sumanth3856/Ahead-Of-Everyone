"use client";

import { Users, Loader2, Send } from "lucide-react";
import { useEffect, useState } from "react";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { getAdminTelemetry } from "../actions";
import { toISTTime } from "@/lib/ist";

export default function AdminUsersGrid() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchTelemetry = async () => {
      try {
        const data = await getAdminTelemetry();
        if (mounted) {
          setUsers(data.users);
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
          <h1 className="text-2xl font-bold tracking-widest text-foreground uppercase flex items-center gap-3">
            <Users className="text-red-500 w-6 h-6" />
            Personnel Database
          </h1>
          <p className="text-muted text-sm mt-1">Real-time synchronized user registry.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface border border-border-subtle shadow-sm shrink-0">
          <span className="text-xs font-bold text-muted uppercase tracking-widest">Total Agents:</span>
          {loading ? <Loader2 className="h-4 w-4 animate-spin text-red-500" /> : <span className="text-red-500 font-extrabold">{users.length}</span>}
        </div>
      </div>

      <SpatialCard depth={4} className="glass rounded-3xl border border-border-subtle overflow-hidden shadow-sm">
        <div className="overflow-x-auto min-h-[500px]">
          <table className="w-full text-sm text-left relative">
            <thead className="text-xs text-muted uppercase bg-surface/80 border-b border-border-subtle sticky top-0 z-20 backdrop-blur-md">
              <tr>
                <th className="px-6 py-4 font-bold tracking-wider">Agent Name</th>
                <th className="px-6 py-4 font-bold tracking-wider">Email Address</th>
                <th className="px-6 py-4 font-bold tracking-wider">Join Date (IST)</th>
                <th className="px-6 py-4 font-bold tracking-wider text-center">Telegram Link</th>
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
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-muted italic">
                    No personnel data available.
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="group hover:bg-surface/50 transition-colors">
                    <td className="px-6 py-5 font-bold text-foreground capitalize">
                      {user.full_name || "Agent"}
                    </td>
                    <td className="px-6 py-5 text-muted font-medium">
                      {user.email}
                    </td>
                    <td className="px-6 py-5 text-xs font-bold tracking-wider uppercase text-muted">
                      {toISTTime(user.created_at)}
                    </td>
                    <td className="px-6 py-5 text-center">
                      {user.telegram_chat_id ? (
                        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-500 text-xs font-bold uppercase tracking-wider">
                          <Send size={12} /> Linked
                        </div>
                      ) : (
                        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-surface border border-border-subtle text-muted text-xs font-bold uppercase tracking-wider">
                          Unlinked
                        </div>
                      )}
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
