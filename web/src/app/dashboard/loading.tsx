import { ShieldCheck, Activity, Send, Clock, FileText } from "lucide-react";

export default function DashboardLoading() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 animate-pulse">
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <div className="h-8 w-64 bg-surface-hover rounded-lg mb-2"></div>
          <div className="h-4 w-48 bg-surface-hover rounded-lg"></div>
        </div>
        <div className="h-8 w-40 bg-surface-hover rounded-full shrink-0"></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Connection Status Card Skeleton */}
        <div className="glass rounded-xl p-6 border border-border-subtle lg:col-span-1 relative overflow-hidden shadow-sm">
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-lg bg-surface-hover w-12 h-12"></div>
              <div className="h-4 w-32 bg-surface-hover rounded"></div>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="h-4 w-16 bg-surface-hover rounded"></div>
                <div className="h-4 w-24 bg-surface-hover rounded"></div>
              </div>
              <div className="flex justify-between items-center">
                <div className="h-4 w-16 bg-surface-hover rounded"></div>
                <div className="h-4 w-32 bg-surface-hover rounded"></div>
              </div>
              <div className="flex justify-between items-center">
                <div className="h-4 w-16 bg-surface-hover rounded"></div>
                <div className="h-4 w-20 bg-surface-hover rounded"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Skeleton */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="glass rounded-xl p-6 border border-border-subtle flex flex-col justify-center shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-5 h-5 rounded-full bg-surface-hover"></div>
              <div className="h-4 w-32 bg-surface-hover rounded"></div>
            </div>
            <div className="h-10 w-24 bg-surface-hover rounded mb-3"></div>
            <div className="h-3 w-40 bg-surface-hover rounded"></div>
          </div>
          <div className="glass rounded-xl p-6 border border-border-subtle flex flex-col justify-center shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-5 h-5 rounded-full bg-surface-hover"></div>
              <div className="h-4 w-32 bg-surface-hover rounded"></div>
            </div>
            <div className="h-10 w-48 bg-surface-hover rounded mb-3"></div>
            <div className="h-3 w-32 bg-surface-hover rounded"></div>
          </div>
        </div>
      </div>

      {/* Table Skeleton */}
      <div className="glass rounded-xl border border-border-subtle overflow-hidden shadow-sm">
        <div className="p-6 border-b border-border-subtle flex justify-between items-center bg-surface">
          <div className="h-4 w-48 bg-surface-hover rounded"></div>
          <div className="h-4 w-20 bg-surface-hover rounded"></div>
        </div>
        <div className="p-6 space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex justify-between items-center py-2">
              <div className="h-4 w-40 bg-surface-hover rounded"></div>
              <div className="h-4 w-32 bg-surface-hover rounded"></div>
              <div className="h-8 w-24 bg-surface-hover rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
