"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Services", path: "/services" },
    { name: "About", path: "/about" },
  ];

  // Mocking auth state for UI purposes. Wire to Supabase auth later.
  const isLoggedIn = false;

  return (
    <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-2xl border-b border-brand/20 transition-all duration-300">
      {/* Changed max-w-7xl to w-full to snap elements to edges */}
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <div className="relative w-10 h-10 sm:w-12 sm:h-12 overflow-hidden rounded-lg group-hover:bg-glow transition-all duration-500">
              <Image src="/logo.png" alt="AoE Logo" fill className="object-cover" />
            </div>
            <span className="font-bold text-lg sm:text-xl tracking-wider text-foreground group-hover:text-brand transition-colors whitespace-nowrap">
              AHEAD OF <span className="text-brand text-glow group-hover:text-foreground transition-colors hidden sm:inline">EVERYONE</span>
              <span className="text-brand text-glow group-hover:text-foreground transition-colors sm:hidden">EVRY1</span>
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
                  className={`relative font-medium text-sm tracking-widest uppercase transition-colors hover:text-brand-light ${
                    isActive ? "text-brand-light" : "text-muted"
                  }`}
                >
                  {link.name}
                  {isActive && (
                    <motion.div
                      layoutId="navbar-indicator"
                      className="absolute -bottom-2 left-0 right-0 h-0.5 bg-brand bg-glow"
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
            {isLoggedIn ? (
              <>
                <Link href="/dashboard" className="px-6 py-2 rounded-full bg-brand/10 border border-brand/50 text-brand-light font-semibold tracking-widest text-xs uppercase hover:bg-brand hover:text-white hover:bg-glow transition-all duration-300">
                  Dashboard
                </Link>
                <button className="text-xs font-semibold tracking-widest uppercase text-muted hover:text-red-400 transition-colors cursor-pointer">
                  Sign Out
                </button>
              </>
            ) : (
              <Link href="/login" className="px-6 py-2 rounded-full bg-brand/10 border border-brand/50 text-brand-light font-semibold tracking-widest text-xs uppercase hover:bg-brand hover:text-white hover:bg-glow transition-all duration-300 whitespace-nowrap">
                Client Portal
              </Link>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden flex items-center shrink-0">
            <button 
              onClick={() => setIsOpen(!isOpen)}
              className="text-muted hover:text-brand-light transition-colors p-2"
              aria-label="Toggle menu"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden absolute top-20 left-0 w-full bg-surface border-b border-brand/20 glass"
          >
            <div className="px-4 pt-4 pb-6 space-y-4 flex flex-col">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  href={link.path}
                  onClick={() => setIsOpen(false)}
                  className={`block text-sm tracking-widest uppercase py-2 transition-colors ${
                    pathname === link.path ? "text-brand-light font-bold" : "text-muted"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              <div className="pt-4 border-t border-brand/10 flex flex-col gap-4">
                {isLoggedIn ? (
                  <>
                    <Link 
                      href="/dashboard" 
                      onClick={() => setIsOpen(false)}
                      className="text-center py-3 rounded-lg bg-brand/10 border border-brand/50 text-brand-light font-semibold tracking-widest text-sm uppercase hover:bg-brand hover:text-white transition-all"
                    >
                      Dashboard
                    </Link>
                    <button className="text-sm font-semibold tracking-widest uppercase text-muted hover:text-red-400 transition-colors text-left py-2">
                      Sign Out
                    </button>
                  </>
                ) : (
                  <Link 
                    href="/login" 
                    onClick={() => setIsOpen(false)}
                    className="text-center py-3 rounded-lg bg-brand/10 border border-brand/50 text-brand-light font-semibold tracking-widest text-sm uppercase hover:bg-brand hover:text-white transition-all"
                  >
                    Client Portal
                  </Link>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
