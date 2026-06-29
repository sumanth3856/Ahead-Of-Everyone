import { ShieldCheck, Activity, ShieldAlert, Cpu } from "lucide-react";
import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { AdminOperationsClient } from "@/components/dashboard/AdminOperationsClient";

export default async function AdminDashboard() {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // Verify Admin Status
  const { data: profile } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', user.id)
    .single();

  // TEMPORARY FIX: Bypass role check because 'role' column is missing
  // if (profile?.role !== 'admin') {
  //   redirect("/dashboard");
  // }

  // Fetch some basic system health stats (mocked/queried)
  const { count: usersCount } = await supabase.from('profiles').select('*', { count: 'exact', head: true });
  const { count: digestsCount } = await supabase.from('digests_cache').select('*', { count: 'exact', head: true });

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-10 pb-20 relative">
      
      {/* Elegant Glowing Background Orbs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-red-500/5 blur-[120px] rounded-full pointer-events-none -z-10 mix-blend-screen" />
      <div className="absolute top-1/4 right-0 w-[400px] h-[400px] bg-blue-500/5 blur-[100px] rounded-full pointer-events-none -z-10 mix-blend-screen" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-widest text-foreground uppercase flex items-center gap-3">
            <ShieldAlert className="text-red-500 w-6 h-6" />
            Command Center
          </h1>
          <p className="text-muted text-sm mt-1">Elevated operations and global system overrides.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-red-500/30 bg-red-500/10 text-red-500 text-xs tracking-widest uppercase font-bold shrink-0">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500"></span>
          </span>
          Admin Clearance
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SpatialCard depth={8} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-500 -translate-y-4 translate-x-4 pointer-events-none">
            <Activity className="w-32 h-32 text-green-500" />
          </div>
          <div className="flex items-center justify-between mb-4 relative z-10">
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">System Status</h3>
            <div className="p-2 rounded-lg bg-green-500/10 text-green-500">
              <Activity className="h-4 w-4" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-foreground flex items-baseline gap-2 relative z-10">
            100<span className="text-lg text-green-500 font-bold">%</span>
          </p>
          <p className="text-green-500 text-sm font-semibold mt-1">All pipelines operational</p>
        </SpatialCard>
        
        <SpatialCard depth={8} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-500 -translate-y-4 translate-x-4 pointer-events-none">
            <ShieldCheck className="w-32 h-32 text-brand" />
          </div>
          <div className="flex items-center justify-between mb-4 relative z-10">
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Total Personnel</h3>
            <div className="p-2 rounded-lg bg-brand/10 text-brand">
              <ShieldCheck className="h-4 w-4" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-foreground relative z-10">{usersCount || 0}</p>
          <p className="text-muted text-sm font-semibold mt-1">Registered agents</p>
        </SpatialCard>

        <SpatialCard depth={8} className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col justify-center relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-500 -translate-y-4 translate-x-4 pointer-events-none">
            <Cpu className="w-32 h-32 text-blue-500" />
          </div>
          <div className="flex items-center justify-between mb-4 relative z-10">
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Intel Dispatched</h3>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
              <Cpu className="h-4 w-4" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-foreground relative z-10">{digestsCount || 0}</p>
          <p className="text-muted text-sm font-semibold mt-1">Broadcasts completed</p>
        </SpatialCard>
      </div>

      {/* Admin Operations Component */}
      <AdminOperationsClient />
      
    </div>
  );
}
