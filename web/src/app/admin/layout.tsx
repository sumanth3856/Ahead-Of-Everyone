import AdminSidebar from "@/components/admin/AdminSidebar";
import Header from "@/components/dashboard/Header";
import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    redirect("/login");
  }

  // TEMPORARY FIX: Use ADMIN_EMAIL env var until 'role' column is active everywhere
  if (user.email !== process.env.ADMIN_EMAIL) {
    redirect("/dashboard");
  }

  return (
    <div className="flex h-[100dvh] bg-background overflow-hidden selection:bg-red-500/30">
      <AdminSidebar />
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <Header />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
