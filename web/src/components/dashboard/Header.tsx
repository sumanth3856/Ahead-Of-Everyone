import { Bell, Search, User, TerminalSquare } from "lucide-react";
import Link from "next/link";

export default function Header() {
  return (
    <header className="h-20 border-b border-border-subtle/90 backdrop-blur-xl flex items-center justify-between pl-14 pr-4 md:px-6 lg:px-8 z-10 sticky top-0 shadow-sm">
      <div className="flex items-center gap-4 w-full md:w-auto">
        {/* Mobile Logo */}
        <Link href="/" className="md:hidden flex items-center gap-2 group mr-2">
          <TerminalSquare className="text-brand h-6 w-6 group-hover:opacity-80 transition-colors" />
          <span className="font-bold tracking-widest text-foreground group-hover:text-brand transition-colors text-xs sm:text-sm">
            AHEAD OF <span className="text-brand group-hover:text-foreground transition-colors">EVERYONE</span>
          </span>
        </Link>

        <div className="flex-1 md:flex-none flex items-center bg-surface rounded-full px-3 sm:px-4 py-2 max-w-[8rem] sm:max-w-[12rem] md:max-w-xs border border-border-subtle focus-within:border-brand focus-within:ring-1 focus-within:ring-brand/30 transition-all">
          <Search className="h-4 w-4 text-muted sm:mr-2" />
          <input 
            type="text" 
            placeholder="Search intel..." 
            className="bg-transparent border-none outline-none text-sm text-foreground w-full placeholder:text-muted focus:ring-0 hidden sm:block"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-2 sm:gap-4">
        <button className="relative p-2 text-muted hover:text-brand transition-colors rounded-full hover:bg-surface">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-brand"></span>
        </button>
        
        <div className="h-8 w-px bg-surface-hover mx-2"></div>
        
        <button className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-bold text-foreground">Agent 007</p>
            <p className="text-xs text-brand font-bold tracking-widest uppercase">Clearance: Level 4</p>
          </div>
          <div className="h-10 w-10 rounded-full bg-surface border border-border-subtle flex items-center justify-center text-brand">
            <User className="h-5 w-5" />
          </div>
        </button>
      </div>
    </header>
  );
}
