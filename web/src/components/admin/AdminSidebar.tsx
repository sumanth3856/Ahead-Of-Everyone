"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, Newspaper, Zap, ShieldAlert, LogOut, Menu, X } from "lucide-react";
import { useState } from "react";
import { createClient } from "@/utils/supabase/client";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import ThemeToggle from "@/components/ThemeToggle";

export default function AdminSidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const supabase = createClient();
  const router = useRouter();
  
  const navItems = [
    { name: "System Overview", href: "/admin", icon: LayoutDashboard },
    { name: "Personnel (Users)", href: "/admin/users", icon: Users },
    { name: "Global Digests", href: "/admin/digests", icon: Newspaper },
    { name: "Operations", href: "/admin/operations", icon: Zap },
  ];

  const handleSignOut = async () => {
    try {
      await supabase.auth.signOut();
      toast.success("Signed out successfully");
      router.push("/login");
      router.refresh();
    } catch (error: any) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <button 
        onClick={() => setIsOpen(true)}
        className="md:hidden fixed top-5 right-4 z-50 p-3 bg-surface border border-border-subtle rounded-lg text-brand hover:opacity-80 transition-colors shadow-sm"
      >
        <Menu className="h-6 w-6" />
      </button>

      {isOpen && (
        <div 
          onClick={() => setIsOpen(false)}
          className="md:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
        />
      )}
      
      <aside 
        className={`fixed md:static inset-y-0 right-0 md:left-0 md:right-auto w-64 border-l md:border-l-0 border-border-subtle md:border-r bg-background flex flex-col z-50 shadow-sm transition-transform duration-300 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'
        }`}
      >
        <div className="h-20 flex items-center justify-between px-6 border-b border-border-subtle bg-surface/50 shrink-0">
          <Link href="/admin" className="flex items-center gap-3 group outline-none" onClick={() => setIsOpen(false)}>
            <div className="w-10 h-10 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center shrink-0 group-hover:bg-brand/20 group-hover:border-brand/30 transition-all duration-300 group-active:scale-95 shadow-inner">
              <ShieldAlert className="h-5 w-5 text-brand" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold tracking-widest uppercase text-foreground text-sm group-hover:text-brand transition-colors duration-300">Command</span>
              <span className="text-[10px] text-brand font-bold uppercase tracking-widest">Center</span>
            </div>
          </Link>
          <button onClick={() => setIsOpen(false)} className="md:hidden text-muted hover:text-brand font-bold p-3" aria-label="Close menu">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-6 px-4">
          <nav className="flex flex-col gap-3">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={`group flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-bold relative overflow-hidden ${
                    isActive 
                      ? "bg-brand/10 text-brand border border-brand/20 shadow-sm scale-[1.02] translate-x-1 before:absolute before:left-0 before:top-1/2 before:-translate-y-1/2 before:h-8 before:w-1.5 before:bg-brand before:rounded-r-full" 
                      : "text-muted hover:bg-surface hover:text-foreground hover:translate-x-1 hover:shadow-sm border border-transparent hover:border-border-subtle"
                  }`}
                >
                  <Icon className={`h-5 w-5 transition-transform duration-300 ${isActive ? "scale-110" : "group-hover:scale-110"}`} />
                  <span className="tracking-wide text-sm">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-border-subtle shrink-0 bg-surface/50 space-y-4">
          <div className="flex items-center justify-between px-4 hidden md:flex">
             {/* Note: Admin page has its own Theme toggle in header, but keeping here for consistency if needed, or remove. Let's keep it consistent with Dashboard. */}
          </div>
          <button 
            onClick={handleSignOut}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-muted hover:bg-red-500/10 hover:text-red-500 transition-all duration-300 font-bold group cursor-pointer hover:translate-x-1"
          >
            <LogOut className="h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
            <span className="tracking-wide text-sm">Exit Command</span>
          </button>
        </div>
      </aside>
    </>
  );
}
