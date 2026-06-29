"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Newspaper, Settings, LogOut, TerminalSquare, Menu, X, ShieldAlert } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ThemeToggle from "@/components/ThemeToggle";
import { logout } from "@/app/auth/actions";
import { SubmitButton } from "@/components/SubmitButton";

export default function Sidebar({ isAdmin = false }: { isAdmin?: boolean }) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  
  const navItems = [
    { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { name: "Digests", href: "/dashboard/digests", icon: Newspaper },
    ...(isAdmin ? [{ name: "Command Center", href: "/dashboard/admin", icon: ShieldAlert }] : []),
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
  ];

  return (
    <>
      {/* Mobile Toggle Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className="md:hidden fixed top-5 left-4 z-50 p-2 bg-surface border border-border-subtle rounded-lg text-brand hover:opacity-80 transition-colors shadow-sm"
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
        className={`fixed md:static inset-y-0 left-0 w-64 border-r border-border-subtle bg-background flex flex-col z-50 shadow-sm transition-transform duration-300 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="h-20 flex items-center justify-between px-6 border-b border-border-subtle bg-surface/50">
          <Link href="/" className="flex items-center gap-2 group">
            <TerminalSquare className="text-brand h-6 w-6 group-hover:opacity-80 transition-colors" />
            <span className="font-bold tracking-widest text-foreground group-hover:text-brand transition-colors text-sm">
              AHEAD OF <span className="text-brand group-hover:text-foreground transition-colors">EVERYONE</span>
            </span>
          </Link>
          {/* Mobile Close Button */}
          <button onClick={() => setIsOpen(false)} className="md:hidden text-muted hover:text-brand font-bold">
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <div className="flex-1 py-8 px-4 flex flex-col gap-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link 
                key={item.name} 
                href={item.href}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 font-bold ${
                  isActive 
                    ? "bg-brand/10 border-l-4 border-brand text-brand" 
                    : "text-muted hover:text-brand hover:bg-surface"
                }`}
              >
                <item.icon className="h-5 w-5" />
                <span className="font-bold text-sm tracking-wide">{item.name}</span>
              </Link>
            );
          })}
        </div>
        
        <div className="p-4 border-t border-border-subtle bg-surface/50 space-y-4">
          <div className="flex items-center justify-between px-4">
            <span className="text-sm font-bold text-muted">Theme</span>
            <ThemeToggle />
          </div>
          <form action={logout} className="w-full">
            <SubmitButton 
              className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-muted hover:text-red-600 hover:bg-red-500/10 transition-all duration-300 text-left cursor-pointer font-bold"
              loadingText="Signing Out"
            >
              <LogOut className="h-5 w-5" />
              <span className="font-bold text-sm tracking-wide">Sign Out</span>
            </SubmitButton>
          </form>
        </div>
      </aside>
    </>
  );
}
