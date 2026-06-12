import { ShieldCheck, Activity, Send, Clock } from "lucide-react";

export default function DashboardHome() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8">
      <div className="flex items-end justify-between mb-2">
        <div>
          <h1 className="text-2xl font-bold tracking-widest text-foreground">COMMAND <span className="text-brand text-glow">CENTER</span></h1>
          <p className="text-muted text-sm mt-1">Intelligence pipeline active. All systems nominal.</p>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full border border-green-500/30 bg-green-500/10 text-green-400 text-xs tracking-widest uppercase">
          <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse"></div>
          Secure Connection
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Telegram Connection Status Card */}
        <div className="glass rounded-xl p-6 border border-brand/20 lg:col-span-1 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Send className="h-24 w-24 text-brand" />
          </div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-lg bg-brand/10 border border-brand/30">
                <ShieldCheck className="h-6 w-6 text-brand-light" />
              </div>
              <h2 className="font-semibold tracking-wide uppercase text-sm">Telegram Link</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-muted text-sm">Status</span>
                <span className="text-green-400 text-sm font-medium flex items-center gap-1.5 text-glow">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400"></span> Connected
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted text-sm">Bot Name</span>
                <span className="text-foreground text-sm">@DailyTechDigestBot</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted text-sm">Last Sync</span>
                <span className="text-foreground text-sm">2 mins ago</span>
              </div>
            </div>
            
            <div className="mt-8 pt-4 border-t border-brand/10">
              <button className="w-full py-2 bg-surface hover:bg-surface-hover border border-brand/20 rounded-lg text-xs uppercase tracking-widest text-muted hover:text-foreground transition-all cursor-pointer">
                Reconfigure Link
              </button>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="glass rounded-xl p-6 border border-brand/20 flex flex-col justify-center">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="h-5 w-5 text-brand" />
              <h3 className="text-muted text-sm uppercase tracking-wider">Articles Processed</h3>
            </div>
            <p className="text-4xl font-bold text-foreground">1,204</p>
            <p className="text-xs text-brand mt-2">+12% from last cycle</p>
          </div>
          <div className="glass rounded-xl p-6 border border-brand/20 flex flex-col justify-center">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="h-5 w-5 text-brand" />
              <h3 className="text-muted text-sm uppercase tracking-wider">Next Delivery In</h3>
            </div>
            <p className="text-4xl font-bold text-foreground">04:12:00</p>
            <p className="text-xs text-muted mt-2">Scheduled for 08:00 UTC</p>
          </div>
        </div>
      </div>

      {/* Recent Digests Table */}
      <div className="glass rounded-xl border border-brand/20 overflow-hidden">
        <div className="p-6 border-b border-brand/20 flex justify-between items-center bg-surface/50">
          <h2 className="font-semibold tracking-wide uppercase text-sm">Recent Transmissions</h2>
          <button className="text-xs text-brand hover:text-brand-light uppercase tracking-widest transition-colors cursor-pointer">View All</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted uppercase bg-brand/5 border-b border-brand/10">
              <tr>
                <th className="px-6 py-4 font-medium tracking-wider">Digest ID</th>
                <th className="px-6 py-4 font-medium tracking-wider">Date Sent</th>
                <th className="px-6 py-4 font-medium tracking-wider">Articles</th>
                <th className="px-6 py-4 font-medium tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand/10">
              {[
                { id: "DGST-902", date: "Today, 08:00", articles: 5, status: "Delivered" },
                { id: "DGST-901", date: "Yesterday, 08:00", articles: 8, status: "Delivered" },
                { id: "DGST-900", date: "Jun 10, 08:00", articles: 6, status: "Delivered" },
                { id: "DGST-899", date: "Jun 09, 08:00", articles: 4, status: "Failed" },
              ].map((row, i) => (
                <tr key={i} className="hover:bg-brand/5 transition-colors group">
                  <td className="px-6 py-4 font-medium text-foreground group-hover:text-brand-light transition-colors">{row.id}</td>
                  <td className="px-6 py-4 text-muted">{row.date}</td>
                  <td className="px-6 py-4 text-muted">{row.articles} payload items</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs tracking-wider uppercase border ${
                      row.status === "Delivered" 
                        ? "bg-green-500/10 text-green-400 border-green-500/30" 
                        : "bg-red-500/10 text-red-400 border-red-500/30"
                    }`}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
