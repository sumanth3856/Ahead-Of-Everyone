import Sidebar from "@/components/dashboard/Sidebar";
import Header from "@/components/dashboard/Header";
import RealtimeSync from "@/components/dashboard/RealtimeSync";
import { createClient } from "@/utils/supabase/server";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  let isAdmin = false;
  if (user) {
    const { data: profile, error } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single();
    
    // TEMPORARY FIX: Use ADMIN_EMAIL env var until 'role' column is added
    isAdmin = user.email === process.env.ADMIN_EMAIL;
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden selection:bg-brand/30">
      <RealtimeSync />
      <Sidebar isAdmin={isAdmin} />
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <Header />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
