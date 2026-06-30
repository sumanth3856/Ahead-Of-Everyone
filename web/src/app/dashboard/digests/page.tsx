import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";
import { FileText, Download, Calendar, ExternalLink } from "lucide-react";
import { SpatialCard } from "@/components/ui/SpatialCard";
import Link from "next/link";

export const metadata = {
  title: 'Digests Archive | Daily Tech Digest',
};

export default async function DigestsPage() {
  const supabase = await createClient();
  
  // 1. Fetch Auth State
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    redirect("/login");
  }

  // 2. Fetch all live digests for THIS USER (and global broadcasts)
  // Use admin client to bypass RLS in Server Component context safely
  const { createClient: createSupabaseClient } = await import('@supabase/supabase-js');
  const supabaseAdmin = createSupabaseClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const { data: digests, error: dbError } = await supabaseAdmin
    .from("digests_cache")
    .select("topic, generated_date_ist, supabase_path, file_id, created_at")
    .order("generated_date_ist", { ascending: false });
    
  const allDigests = digests || [];

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8 pb-20">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-2 gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-widest text-foreground uppercase flex items-center gap-3">
            <FileText className="text-brand w-6 h-6" />
            Newsletter Archive
          </h1>
          <p className="text-muted text-sm mt-1">Access your entire history of generated tech digests.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-brand/30 bg-brand/10 text-brand text-xs tracking-widest uppercase font-bold shrink-0">
          {allDigests.length} Records Found
        </div>
      </div>

      {/* Grid Layout for Digests */}
      {allDigests.length === 0 ? (
        <SpatialCard depth={5} className="glass rounded-[2rem] p-12 border border-border-subtle shadow-sm flex flex-col items-center justify-center text-center mt-8">
          <FileText className="h-16 w-16 text-muted mb-4 opacity-50" />
          <h2 className="text-xl font-bold text-foreground mb-2">No Newsletters Found</h2>
          <p className="text-muted max-w-md">Your newsletter hasn't generated any issues yet. Ensure your Telegram is linked and wait for the scheduled broadcast.</p>
        </SpatialCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {allDigests.map((digest, index) => {
            // Use public storage URL or fallback to Telegram API proxy
            let fileUrl = "#";
            if (digest.supabase_path) {
              fileUrl = digest.supabase_path.startsWith('http') 
                ? digest.supabase_path 
                : `${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/daily-digests/${digest.supabase_path}`;
            } else if (digest.file_id) {
              fileUrl = `/api/download?file_id=${digest.file_id}`;
            }
            
            return (
              <SpatialCard 
                key={index} 
                depth={8} 
                className="glass rounded-3xl p-6 border border-border-subtle shadow-sm flex flex-col group hover:border-brand/30 transition-colors"
              >
                <div className="flex items-start justify-between mb-6">
                  <div className="p-3 rounded-xl bg-surface border border-border-subtle shadow-inner group-hover:bg-brand/10 group-hover:border-brand/20 transition-colors">
                    <FileText className="h-6 w-6 text-brand" />
                  </div>
                  <div className="flex items-center gap-2 text-xs font-bold text-muted uppercase tracking-widest bg-surface px-3 py-1.5 rounded-full border border-border-subtle">
                    <Calendar className="h-3 w-3" />
                    {digest.generated_date_ist}
                    {digest.created_at && (
                      <span className="opacity-70 ml-1">
                        {new Date(digest.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Formatted Title */}
                <h3 className="text-2xl font-bold text-foreground leading-tight mb-2 flex-grow capitalize">
                  {(() => {
                    const cleanTopic = (digest.topic || "").replace(/^v4:/, "").replace(/_/g, " ");
                    if (cleanTopic.toLowerCase() === "latest") {
                      return `Daily Tech Digest`;
                    }
                    return cleanTopic;
                  })()}
                </h3>
                
                <div className="pt-4 mt-2 border-t border-border-subtle flex gap-3">
                  <Link 
                    href={fileUrl} 
                    target="_blank"
                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-foreground text-background font-bold text-sm tracking-wide hover:opacity-90 transition-all shadow-sm"
                  >
                    Read Intel <ExternalLink className="w-4 h-4" />
                  </Link>
                  <Link 
                    href={fileUrl} 
                    download
                    target="_blank"
                    className="w-12 h-12 shrink-0 flex items-center justify-center rounded-xl bg-surface border border-border-subtle hover:bg-brand hover:border-brand hover:text-white transition-all text-muted hover:text-white"
                  >
                    <Download className="w-5 h-5" />
                  </Link>
                </div>
              </SpatialCard>
            );
          })}
        </div>
      )}

    </div>
  );
}
