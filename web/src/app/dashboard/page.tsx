import { ShieldCheck, Activity, Send, Clock, Download, FileText, AlertCircle } from "lucide-react";
import { createClient } from "@/utils/supabase/server";
import Link from "next/link";
import { redirect } from "next/navigation";
import LinkTelegramClient from "@/components/dashboard/LinkTelegramClient";
import { SpatialCard } from "@/components/ui/SpatialCard";
import { LiveClock } from "@/components/ui/LiveClock";
import { toISTTime } from "@/lib/ist";

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
    .select("topic, generated_date_ist, supabase_path, file_id, created_at, user_id")
    .or(`user_id.eq.${user.id},user_id.is.null`)
    .order("created_at", { ascending: false });
    
  if (dbError) {
    console.error("Error fetching digests:", dbError);
  }
  
  const { count: totalDigests } = await supabaseAdmin
    .from("digests_cache")
    .select("*", { count: "exact", head: true })
    .or(`user_id.eq.${user.id},user_id.is.null`);
    
  const allDigests = digests || [];

  const publicStorageUrl = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/daily-digests/`;

  return (
    <main className="max-w-6xl mx-auto flex flex-col gap-8 pb-12 animate-in fade-in duration-500">
      <header className="relative overflow-hidden rounded-3xl bg-surface/50 border border-border-subtle p-4 sm:p-6 md:p-8 shadow-sm">
        <div className="absolute inset-0 bg-gradient-to-r from-brand/10 via-transparent to-transparent opacity-50" />
        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="flex flex-col gap-1.5">
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
              Welcome, <span className="bg-gradient-to-r from-brand to-brand-light bg-clip-text text-transparent">{firstName}</span>
            </h1>
            <p className="text-muted font-medium mb-1 flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand"></span>
              </span>
              Newsletter active. All systems nominal.
            </p>
            <div className="bg-background/50 inline-flex px-3 py-1.5 rounded-full border border-border-subtle backdrop-blur-sm w-fit mt-2">
              <LiveClock />
            </div>
          </div>
          <div className="flex flex-col items-end shrink-0">
            <div className="flex items-center gap-2 px-4 py-2 rounded-2xl border border-green-500/30 bg-green-500/10 text-green-600 text-xs tracking-widest uppercase font-bold shadow-[0_0_15px_rgba(34,197,94,0.15)]">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
              Secure Connection
            </div>
          </div>
        </div>
      </header>

      <section aria-label="Overview Metrics" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
              <h2 className="font-bold tracking-wider uppercase text-sm text-foreground">Account Status</h2>
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
            <p className="text-3xl font-extrabold text-foreground">{totalDigests}</p>
            <p className="text-xs text-brand font-semibold mt-2">Latest newsletters</p>
          </SpatialCard>
        )}

        <SpatialCard depth={5} className="glass rounded-[2rem] p-6 border border-border-subtle flex flex-col justify-center shadow-sm lg:col-span-1">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="h-5 w-5 text-brand" />
              <h3 className="text-muted text-sm uppercase tracking-wider font-bold">Latest Update</h3>
            </div>
            {allDigests.length > 0 ? (
              <>
                <p className="text-xl sm:text-2xl font-extrabold text-foreground truncate">
                  {allDigests[0].generated_date_ist}
                </p>
                <p className="text-xs text-brand font-semibold mt-2">
                  {toISTTime(allDigests[0].created_at)} IST
                </p>
              </>
            ) : (
              <p className="text-xl font-extrabold text-foreground">N/A</p>
            )}
          </SpatialCard>
      </section>

      {/* All Digests Table */}
      <section aria-label="Transmissions Archive">
        <SpatialCard depth={2} className="glass rounded-[2rem] border border-border-subtle overflow-hidden shadow-sm">
        <div className="p-6 border-b border-border-subtle flex justify-between items-center bg-surface">
          <h2 className="font-bold tracking-wider uppercase text-sm text-foreground">Transmissions Archive</h2>
          <span className="text-xs text-muted font-bold uppercase tracking-widest">Total: {allDigests.length}</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <caption className="sr-only">Transmissions Archive Table</caption>
            <thead className="text-xs text-muted uppercase bg-surface/50 border-b border-border-subtle">
              <tr>
                <th scope="col" className="px-3 sm:px-6 py-4 font-bold tracking-wider">Topic</th>
                <th scope="col" className="px-3 sm:px-6 py-4 font-bold tracking-wider">Date Generated (IST)</th>
                <th scope="col" className="px-3 sm:px-6 py-4 font-bold tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5">
              {allDigests.length === 0 && !dbError && (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-muted italic">
                    No newsletters available yet.
                  </td>
                </tr>
              )}
              {allDigests.map((row, i) => (
                <tr key={i} className="group relative z-10 bg-background/30 hover:bg-brand/5 border-l-4 border-l-transparent hover:border-l-brand transition-all duration-300">
                  <td scope="row" className="px-3 sm:px-6 py-5 font-bold text-foreground group-hover:text-brand transition-colors capitalize flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-surface border border-border-subtle flex items-center justify-center shrink-0 group-hover:border-brand/30 transition-colors">
                      <FileText className="w-5 h-5 text-muted group-hover:text-brand transition-colors" />
                    </div>
                    {(() => {
                      const cleanTopic = (row.topic || "").replace(/^v4:/, "").replace(/_/g, " ");
                      if (cleanTopic.toLowerCase() === "latest") {
                        return `Daily Tech Digest`;
                      }
                      return cleanTopic;
                    })()}
                  </td>
                  <td className="px-3 sm:px-6 py-4 text-muted font-medium whitespace-normal sm:whitespace-nowrap">
                    {row.generated_date_ist}
                    {row.created_at && (
                      <span className="ml-2 text-xs opacity-70">
                        {toISTTime(row.created_at)} IST
                      </span>
                    )}
                  </td>
                  <td className="px-3 sm:px-6 py-4 text-right">
                    {row.supabase_path ? (
                      <Link 
                        href={`${publicStorageUrl}${row.supabase_path}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-3 py-2.5 sm:px-5 bg-brand hover:bg-brand-light text-white rounded-xl text-xs font-bold uppercase tracking-widest transition-all duration-300 shadow-md shadow-brand/20 hover:shadow-lg hover:-translate-y-0.5"
                      >
                        <Download size={14} /> <span className="hidden sm:inline">Download</span>
                      </Link>
                    ) : row.file_id ? (
                      <Link 
                        href={`/api/download?file_id=${row.file_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-3 py-2.5 sm:px-5 bg-brand hover:bg-brand-light text-white rounded-xl text-xs font-bold uppercase tracking-widest transition-all duration-300 shadow-md shadow-brand/20 hover:shadow-lg hover:-translate-y-0.5"
                      >
                        <Download size={14} /> <span className="hidden sm:inline">Download</span>
                      </Link>
                    ) : (
                      <span className="text-xs text-muted italic inline-flex items-center gap-2 px-3 py-2.5 bg-surface border border-border-subtle rounded-xl"><Activity size={14} className="animate-pulse" /> Processing</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </SpatialCard>
      </section>
    </main>
  );
}
