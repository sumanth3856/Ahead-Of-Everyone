"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

export default function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Services", path: "/services" },
    { name: "About", path: "/about" },
  ];

  return (
    <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-2xl border-b border-brand/20 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative w-12 h-12 overflow-hidden rounded-lg group-hover:bg-glow transition-all duration-500">
              <Image src="/logo.png" alt="AoE Logo" fill className="object-cover" />
            </div>
            <span className="font-bold text-xl tracking-wider text-foreground group-hover:text-brand transition-colors">
              AHEAD OF <span className="text-brand text-glow group-hover:text-foreground transition-colors">EVERYONE</span>
            </span>
          </Link>

          <div className="hidden md:flex space-x-8">
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
          
          <div className="hidden md:flex items-center">
            <button className="px-6 py-2 rounded-full bg-brand/10 border border-brand/50 text-brand-light font-semibold tracking-widest text-xs uppercase hover:bg-brand hover:text-white hover:bg-glow transition-all duration-300">
              Client Portal
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
