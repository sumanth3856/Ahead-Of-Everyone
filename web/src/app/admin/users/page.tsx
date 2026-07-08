"use client";

import { Users, Loader2, Send, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { getAdminTelemetry, deleteUserAction } from "../actions";
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

  const [confirmAction, setConfirmAction] = useState<{
    title: string;
    description: string;
    onConfirm: () => void;
    confirmText: string;
    confirmColor: string;
  } | null>(null);

  const handleDeleteUser = (userId: string) => {
    setConfirmAction({
      title: "Revoke Access",
      description: "Are you sure you want to permanently delete this agent? This action cannot be undone and will cascade to all related records.",
      confirmText: "Delete Agent",
      confirmColor: "bg-red-500",
      onConfirm: async () => {
        setConfirmAction(null);
        try {
          await deleteUserAction(userId);
          setUsers(users.filter(u => u.id !== userId));
        } catch (err) {
          console.error("Failed to delete user:", err);
          alert("Failed to delete user.");
        }
      }
    });
  };

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-20 relative">
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-foreground uppercase flex items-center gap-3">
            <Users className="text-brand w-8 h-8" />
            Personnel Database
          </h1>
          <p className="text-muted text-sm mt-2 font-medium">Manage your active AI agents and users.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface border border-border-subtle shadow-sm shrink-0">
          <span className="text-xs font-bold text-muted uppercase tracking-widest">Total Agents:</span>
          {loading ? <Loader2 className="h-4 w-4 animate-spin text-brand" /> : <span className="text-brand font-black">{users.length}</span>}
        </div>
      </div>

      <SpatialCard depth={4} className="glass rounded-3xl border border-border-subtle overflow-hidden shadow-sm">
        <div className="overflow-x-auto min-h-[500px]">
          <table className="w-full text-sm text-left relative">
            <thead className="text-[11px] text-muted uppercase bg-gradient-to-r from-surface/80 to-surface/40 border-b border-border-subtle sticky top-0 z-20 backdrop-blur-md">
              <tr>
                <th className="px-8 py-5 font-extrabold tracking-widest">Agent Details</th>
                <th className="px-8 py-5 font-extrabold tracking-widest">Join Date (IST)</th>
                <th className="px-8 py-5 font-extrabold tracking-widest text-center">Telegram Status</th>
                <th className="px-8 py-5 font-extrabold tracking-widest text-right">Actions</th>
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
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-muted italic">
                    <div className="flex flex-col items-center justify-center gap-3">
                      <Users className="w-10 h-10 opacity-30 text-brand" />
                      No personnel data available.
                    </div>
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="group hover:bg-brand/5 even:bg-surface/30 transition-all duration-300 relative">
                    <td className="px-8 py-6 relative">
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand scale-y-0 group-hover:scale-y-100 transition-transform origin-center" />
                      <div className="flex items-center gap-5">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand/20 to-brand/5 border border-brand/20 flex items-center justify-center text-brand font-black text-lg shadow-sm shrink-0 group-hover:scale-110 group-hover:shadow-md group-hover:border-brand/40 transition-all duration-300">
                          {(user.full_name || user.email || "?").charAt(0).toUpperCase()}
                        </div>
                        <div className="flex flex-col">
                          <span className="font-extrabold text-foreground capitalize group-hover:text-brand transition-colors text-base">
                            {user.full_name || "Unknown Agent"}
                          </span>
                          <span className="text-xs text-muted font-medium mt-1 truncate max-w-[250px]" title={user.email}>
                            {user.email || "No email available"}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-[11px] font-bold tracking-widest uppercase text-muted">
                      {toISTTime(user.created_at)}
                    </td>
                    <td className="px-8 py-6 text-center">
                      {user.telegram_chat_id ? (
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-500 text-[10px] font-bold uppercase tracking-widest shadow-sm">
                          <Send size={12} className="animate-pulse" /> Linked
                        </div>
                      ) : (
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface border border-border-subtle text-muted text-[10px] font-bold uppercase tracking-widest">
                          Unlinked
                        </div>
                      )}
                    </td>
                    <td className="px-8 py-6 text-right">
                      <button 
                        onClick={() => handleDeleteUser(user.id)}
                        className="p-2.5 text-muted/50 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all inline-flex items-center justify-center shadow-sm hover:shadow-md"
                        title="Revoke Access"
                      >
                        <Trash2 size={16} className="group-hover:scale-110 transition-transform" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </SpatialCard>

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
    </div>
  );
}
