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

  if (profile?.role !== 'admin') {
    redirect("/dashboard");
  }

  // Fetch some basic system health stats (mocked/queried)
  const { count: usersCount } = await supabase.from('profiles').select('*', { count: 'exact', head: true });
  const { count: digestsCount } = await supabase.from('digests_cache').select('*', { count: 'exact', head: true });

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-20">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-foreground flex items-center gap-3">
            <ShieldAlert className="text-red-500 w-8 h-8" />
            Command Center
          </h1>
          <p className="text-muted mt-2">Admin level operations and system overrides.</p>
        </div>
        <div className="px-4 py-2 bg-red-500/10 border border-red-500/20 text-red-500 rounded-full text-xs font-bold uppercase tracking-widest flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
          </span>
          Admin Clearance
        </div>
      </div>

      {/* System Health */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <SpatialCard depth={2} className="glass rounded-[2rem] p-6 border border-border-subtle shadow-sm flex flex-col justify-center">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="h-5 w-5 text-brand" />
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">System Status</h3>
          </div>
          <p className="text-3xl font-extrabold text-foreground text-green-400">Operational</p>
        </SpatialCard>
        
        <SpatialCard depth={2} className="glass rounded-[2rem] p-6 border border-border-subtle shadow-sm flex flex-col justify-center">
          <div className="flex items-center gap-3 mb-2">
            <ShieldCheck className="h-5 w-5 text-brand" />
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Total Users</h3>
          </div>
          <p className="text-3xl font-extrabold text-foreground">{usersCount || 0}</p>
        </SpatialCard>

        <SpatialCard depth={2} className="glass rounded-[2rem] p-6 border border-border-subtle shadow-sm flex flex-col justify-center">
          <div className="flex items-center gap-3 mb-2">
            <Cpu className="h-5 w-5 text-brand" />
            <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Total Broadcasts</h3>
          </div>
          <p className="text-3xl font-extrabold text-foreground">{digestsCount || 0}</p>
        </SpatialCard>
      </div>

      <AdminOperationsClient />
    </div>
  );
}
