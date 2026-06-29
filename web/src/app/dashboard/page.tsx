import { ShieldCheck, Activity, Send, Clock, Download, FileText, AlertCircle } from "lucide-react";
import { createClient } from "@/utils/supabase/server";
import Link from "next/link";
import { redirect } from "next/navigation";
import LinkTelegramClient from "@/components/dashboard/LinkTelegramClient";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { RadarChartWidget } from "@/components/ui/RadarChartWidget";
import { StreakCalendarWidget } from "@/components/ui/StreakCalendarWidget";

export default async function DashboardHome() {
  const supabase = await createClient();
  
  // 1. Fetch Auth State
  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) {
    redirect("/login");
  }

  let fullName = user.user_metadata?.full_name?.trim();
  if (!fullName || fullName === "-") {
    fullName = "Agent";
  }
  const firstName = fullName.split(' ')[0] || "Agent";

  // Fetch user profile to check telegram linkage
  const { data: profile } = await supabase
    .from("profiles")
    .select("telegram_chat_id")
    .eq("id", user.id)
    .single();

  const isTelegramLinked = !!profile?.telegram_chat_id;

  // 2. Fetch live digests for THIS USER (and global broadcasts)
  // Use admin client to bypass RLS in Server Component context safely
  const { createClient: createSupabaseClient } = await import('@supabase/supabase-js');
  const supabaseAdmin = createSupabaseClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const { data: digests, error: dbError } = await supabaseAdmin
    .from("digests_cache")
    .select("topic, generated_date_ist, supabase_path")
    .or(`user_id.eq.${user.id},user_id.is.null`)
    .order("generated_date_ist", { ascending: false })
    .limit(10);
    
  const recentDigests = digests || [];
  const totalDigests = recentDigests.length;

  const publicStorageUrl = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/daily-digests/`;

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-widest text-foreground uppercase">
            Welcome, <span className="text-brand">{firstName}</span>
          </h1>
          <p className="text-muted text-sm mt-1">Intelligence pipeline active. All systems nominal.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-green-500/30 bg-green-500/10 text-green-600 text-xs tracking-widest uppercase font-bold shrink-0">
          <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse"></div>
          Secure Connection
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Connection Status Card */}
        <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle lg:col-span-1 shadow-sm relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-5 translate-x-4 -translate-y-4 pointer-events-none">
            <Send className="h-24 w-24 text-brand" />
          </div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-lg bg-brand/5 border border-brand/10">
                <ShieldCheck className="h-6 w-6 text-brand" />
              </div>
              <h2 className="font-bold tracking-wide uppercase text-sm text-foreground">Account Status</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-muted text-sm font-medium">Status</span>
                <span className="text-green-600 text-sm font-bold flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500"></span> Active
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted text-sm font-medium">Telegram</span>
                <span className={isTelegramLinked ? "text-green-500 text-sm font-bold" : "text-yellow-500 text-sm font-bold"}>
                  {isTelegramLinked ? "Linked" : "Unlinked"}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted text-sm font-medium">Access</span>
                <span className="text-foreground text-sm font-semibold">{isTelegramLinked ? "Premium" : "Standard"}</span>
              </div>
              <div className="pt-4 mt-4 border-t border-border-subtle flex justify-end">
                <Link href="/dashboard/settings" className="text-xs font-bold text-brand uppercase tracking-wider hover:text-brand-light transition-colors">
                  Manage Profile &rarr;
                </Link>
              </div>
            </div>
          </div>
        </SpatialCard>

        {/* Link Telegram Client if unlinked, otherwise show Stats */}
        {!isTelegramLinked ? (
          <LinkTelegramClient />
        ) : (
          <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle flex flex-col justify-center shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <FileText className="h-5 w-5 text-brand" />
              <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Digests Available</h3>
            </div>
            <p className="text-4xl font-extrabold text-foreground">{totalDigests}</p>
            <p className="text-xs text-brand font-semibold mt-2">Latest intelligence reports</p>
          </SpatialCard>
        )}

        <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle flex flex-col justify-center shadow-sm lg:col-span-1">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="h-5 w-5 text-brand" />
              <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Latest Update</h3>
            </div>
            <p className="text-xl sm:text-2xl font-extrabold text-foreground truncate">
              {recentDigests.length > 0 ? recentDigests[0].generated_date_ist : "N/A"}
            </p>
            <p className="text-xs text-muted font-semibold mt-2">Time in IST</p>
          </SpatialCard>
        </div>

        {/* Visual Metrics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <RadarChartWidget />
          <StreakCalendarWidget />
        </div>


      {/* Recent Digests Table */}
      <SpatialCard depth={2} className="glass rounded-[2rem] border border-border-subtle overflow-hidden shadow-sm">
        <div className="p-6 border-b border-border-subtle flex justify-between items-center bg-surface">
          <h2 className="font-bold tracking-wide uppercase text-sm text-foreground">Recent Transmissions</h2>
          <span className="text-xs text-muted font-bold uppercase tracking-widest">Live Feed</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted uppercase bg-surface/50 border-b border-border-subtle">
              <tr>
                <th className="px-6 py-4 font-bold tracking-wider">Topic</th>
                <th className="px-6 py-4 font-bold tracking-wider">Date Generated (IST)</th>
                <th className="px-6 py-4 font-bold tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5">
              {recentDigests.length === 0 && !dbError && (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-muted italic">
                    No intelligence digests available yet.
                  </td>
                </tr>
              )}
              {recentDigests.map((row, i) => (
                <tr key={i} className="hover:bg-surface transition-colors group stagger-row">
                  <td className="px-6 py-4 font-bold text-foreground group-hover:text-brand transition-colors capitalize">
                    {row.topic === "latest" ? "Daily Tech Briefing" : row.topic}
                  </td>
                  <td className="px-6 py-4 text-muted font-medium whitespace-nowrap">{row.generated_date_ist}</td>
                  <td className="px-6 py-4 text-right">
                    {row.supabase_path ? (
                      <Link 
                        href={`${publicStorageUrl}${row.supabase_path}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-brand/10 hover:bg-brand text-brand hover:text-white rounded-lg text-xs font-bold uppercase tracking-widest transition-all duration-300"
                      >
                        <Download size={14} /> Download
                      </Link>
                    ) : (
                      <span className="text-xs text-muted italic">Processing...</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SpatialCard>
    </div>
  );
}
