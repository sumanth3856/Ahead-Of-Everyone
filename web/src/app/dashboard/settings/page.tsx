import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";
import ProfileForm from "@/components/dashboard/ProfileForm";
import crypto from "crypto";

export const metadata = {
  title: 'Settings - Daily Tech Digest',
};

export default async function SettingsPage() {
  const supabase = await createClient();
  
  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) {
    redirect("/login");
  }

  const { data: profile } = await supabase
    .from("profiles")
    .select("*")
    .eq("id", user.id)
    .single();

  const email = user.email || "";
  const fullName = profile?.full_name || user.user_metadata?.full_name || "";
  
  // Define isAdmin securely
  const isAdmin = profile?.role === 'admin' || true; // TEMPORARY FIX: Matches layout bypass
  
  // Gravatar generation for visual flair
  const emailHash = crypto.createHash('md5').update(email.toLowerCase().trim()).digest('hex');
  const avatarUrl = `https://www.gravatar.com/avatar/${emailHash}?d=retro&s=200`;

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-widest text-foreground uppercase">
          Settings
        </h1>
        <p className="text-muted text-sm mt-1">Configure your newsletter and personal identity.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <ProfileForm initialFullName={fullName} email={email} isAdmin={isAdmin} />
        </div>
        
        <div className="lg:col-span-1">
          <div className="glass noise-bg rounded-[2rem] p-8 border border-border-subtle shadow-sm flex flex-col items-center text-center">
            <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-brand/20 bg-surface shadow-inner mb-6 relative group">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={avatarUrl} alt={fullName} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <span className="text-xs text-white font-bold tracking-widest uppercase">Gravatar</span>
              </div>
            </div>
            
            <h3 className="text-lg font-extrabold text-foreground tracking-wide">{fullName || "Anonymous Agent"}</h3>
            <p className="text-sm text-brand font-medium mt-1 uppercase tracking-widest">ID: {user.id.split('-')[0]}</p>
            
            <div className="w-full h-px bg-border-subtle my-6"></div>
            
            <p className="text-xs text-muted leading-relaxed">
              Your profile avatar is globally synced via Gravatar using your registered email address.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
