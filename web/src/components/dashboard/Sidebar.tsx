"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Newspaper, Settings, LogOut, TerminalSquare, Menu, X, ShieldAlert } from "lucide-react";
import { m as motion, AnimatePresence } from "framer-motion";
import ThemeToggle from "@/components/ThemeToggle";
import { logout } from "@/app/auth/actions";
import { SubmitButton } from "@/components/SubmitButton";

export default function Sidebar({ isAdmin = false }: { isAdmin?: boolean }) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  
  const navItems = [
    { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
  ];

  return (
    <>
      {/* Mobile Toggle Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className="md:hidden fixed top-5 right-4 z-50 p-3 bg-surface border border-border-subtle rounded-lg text-brand hover:opacity-80 transition-colors shadow-sm"
      >
        <Menu className="h-6 w-6" />
      </button>

      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          onClick={() => setIsOpen(false)}
          className="md:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
        />
      )}
      
      {/* Sidebar */}
      <aside 
        className={`fixed md:static inset-y-0 right-0 md:left-0 md:right-auto w-64 border-l md:border-l-0 border-border-subtle md:border-r bg-background flex flex-col z-50 shadow-sm transition-transform duration-300 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'
        }`}
      >
        <div className="h-20 flex items-center justify-between px-6 border-b border-border-subtle bg-surface/50 shrink-0">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative w-12 h-12 shrink-0 rounded-lg overflow-hidden group-hover:opacity-80 transition-opacity bg-surface">
              <img src="/logo.jpg" alt="Logo" className="w-full h-full object-contain" />
            </div>
            <span className="flex flex-col justify-center font-bold text-base tracking-wider text-foreground group-hover:text-brand transition-colors leading-tight">
              <span>AHEAD OF</span>
              <span className="text-brand group-hover:text-foreground transition-colors">EVERYONE</span>
            </span>
          </Link>
          {/* Mobile Close Button */}
          <button onClick={() => setIsOpen(false)} className="md:hidden text-muted hover:text-brand font-bold p-3" aria-label="Close menu">
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <div className="flex-1 py-6 px-4 flex flex-col gap-3 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link 
                key={item.name} 
                href={item.href}
                onClick={() => setIsOpen(false)}
                className={`group flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-bold ${
                  isActive 
                    ? "bg-brand text-white shadow-md shadow-brand/25 scale-[1.02] translate-x-1" 
                    : "text-muted hover:text-foreground hover:bg-surface hover:translate-x-1 hover:shadow-sm border border-transparent hover:border-border-subtle"
                }`}
              >
                <item.icon className={`h-5 w-5 transition-transform duration-300 ${isActive ? "scale-110" : "group-hover:scale-110"}`} />
                <span className="tracking-wide text-sm">{item.name}</span>
              </Link>
            );
          })}
        </div>
        
        <div className="p-4 border-t border-border-subtle bg-surface/50 space-y-4 shrink-0">
          <div className="flex items-center justify-between px-4">
            <span className="text-sm font-bold text-foreground">Theme</span>
            <ThemeToggle />
          </div>
          <form action={logout} className="w-full">
            <SubmitButton 
              className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-muted hover:text-red-500 hover:bg-red-500/10 transition-all duration-300 text-left cursor-pointer font-bold group hover:translate-x-1"
              loadingText="Signing Out"
            >
              <LogOut className="h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
              <span className="tracking-wide text-sm">Sign Out</span>
            </SubmitButton>
          </form>
        </div>
      </aside>
    </>
  );
}
