"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, TerminalSquare } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import { logout } from "@/app/auth/actions";

interface NavbarProps {
  isLoggedIn?: boolean;
}

export default function Navbar({ isLoggedIn = false }: NavbarProps) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Services", path: "/services" },
    { name: "About", path: "/about" },
  ];

  return (
    <>
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled 
          ? "bg-background/80 backdrop-blur-xl border-b border-border-subtle shadow-sm" 
          : "bg-background/0 border-b-transparent"
      }`}>
        <div className="w-full px-4 sm:px-6 lg:px-8 transition-all duration-300">
        <div className="flex justify-between items-center h-20">
          
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <div className="relative w-10 h-10 sm:w-12 sm:h-12 overflow-hidden rounded-lg group-hover:shadow-md transition-all duration-500 bg-surface">
              <Image src="/logo.png" alt="AoE Logo" fill className="object-cover" />
            </div>
            <span className="font-bold text-lg sm:text-xl tracking-wider text-foreground group-hover:text-brand transition-colors whitespace-nowrap">
              AHEAD OF <span className="text-brand group-hover:text-foreground transition-colors hidden sm:inline">EVERYONE</span>
              <span className="text-brand group-hover:text-foreground transition-colors sm:hidden">EVRY1</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex space-x-8 flex-1 justify-center">
            {navLinks.map((link) => {
              const isActive = pathname === link.path;
              return (
                <Link
                  key={link.name}
                  href={link.path}
                  className={`relative font-bold text-sm tracking-widest uppercase transition-colors hover:text-brand ${
                    isActive ? "text-brand" : "text-muted hover:text-foreground"
                  }`}
                >
                  {link.name}
                  {isActive && (
                    <motion.div
                      layoutId="navbar-indicator"
                      className="absolute -bottom-2 left-0 right-0 h-0.5 bg-brand"
                      initial={false}
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                </Link>
              );
            })}
          </div>
          
          {/* Desktop Auth */}
          <div className="hidden md:flex items-center gap-4 shrink-0">
            <ThemeToggle />
            {isLoggedIn ? (
              <>
                <Link href="/dashboard" className="px-6 py-2 rounded-full bg-brand/10 border border-brand/20 text-brand font-bold tracking-widest text-xs uppercase hover:bg-brand hover:text-white transition-all duration-300">
                  Dashboard
                </Link>
                <form action={logout}>
                  <button type="submit" className="text-xs font-bold tracking-widest uppercase text-muted hover:text-red-500 transition-colors cursor-pointer">
                    Sign Out
                  </button>
                </form>
              </>
            ) : (
              <Link href="/login" className="px-6 py-2 rounded-full bg-brand/10 border border-brand/20 text-brand font-bold tracking-widest text-xs uppercase hover:bg-brand hover:text-white transition-all duration-300 whitespace-nowrap shadow-sm">
                Client Portal
              </Link>
            )}
          </div>

          {/* Mobile Menu Toggle & Theme */}
          <div className="md:hidden flex items-center gap-2 shrink-0">
            <ThemeToggle />
            <button 
              onClick={() => setIsOpen(!isOpen)}
              className="text-foreground hover:text-brand transition-colors p-2 ml-1"
              aria-label="Toggle menu"
            >
              <Menu className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>
    </nav>

      {/* Mobile Sidebar Drawer */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="md:hidden fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            />
            
            <motion.aside 
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", bounce: 0, duration: 0.4 }}
              className="md:hidden fixed inset-y-0 right-0 w-72 sm:w-80 border-l border-border-subtle bg-background flex flex-col z-50 shadow-2xl"
            >
              <div className="h-20 flex items-center justify-between px-6 border-b border-border-subtle bg-surface/50">
                <span className="font-bold tracking-widest text-foreground text-sm uppercase">
                  Menu
                </span>
                <button onClick={() => setIsOpen(false)} className="text-muted hover:text-brand p-2">
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="flex-1 py-8 px-6 flex flex-col gap-2 overflow-y-auto">
                {navLinks.map((link) => (
                  <Link
                    key={link.name}
                    href={link.path}
                    onClick={() => setIsOpen(false)}
                    className={`block text-lg font-bold tracking-widest uppercase py-4 transition-colors border-b border-border-subtle/50 ${
                      pathname === link.path ? "text-brand" : "text-foreground hover:text-brand"
                    }`}
                  >
                    {link.name}
                  </Link>
                ))}
              </div>
              
              <div className="p-6 border-t border-border-subtle flex flex-col gap-4 bg-surface/30">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-muted uppercase tracking-widest">Theme</span>
                  <ThemeToggle />
                </div>
                {isLoggedIn ? (
                  <>
                    <Link 
                      href="/dashboard" 
                      onClick={() => setIsOpen(false)}
                      className="text-center py-4 rounded-xl bg-brand text-white font-bold tracking-widest text-sm uppercase shadow-sm hover:opacity-90 transition-all"
                    >
                      Dashboard
                    </Link>
                    <form action={logout} className="flex flex-col">
                      <button type="submit" className="text-sm font-bold tracking-widest uppercase text-muted hover:text-red-500 transition-colors text-center py-2">
                        Sign Out
                      </button>
                    </form>
                  </>
                ) : (
                  <Link 
                    href="/login" 
                    onClick={() => setIsOpen(false)}
                    className="text-center py-4 rounded-xl bg-brand text-white font-bold tracking-widest text-sm uppercase shadow-sm hover:opacity-90 transition-all"
                  >
                    Client Portal
                  </Link>
                )}
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
