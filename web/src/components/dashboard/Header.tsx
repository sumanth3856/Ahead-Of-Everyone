import { Bell, Search, User } from "lucide-react";

export default function Header() {
  return (
    <header className="h-20 border-b border-brand/20 glass flex items-center justify-between pl-16 pr-4 md:px-6 lg:px-8 z-10 sticky top-0">
      <div className="flex items-center glass rounded-full px-4 py-2 w-full max-w-[12rem] md:w-64 border border-brand/10 focus-within:border-brand/50 focus-within:ring-1 focus-within:ring-brand/30 transition-all">
        <Search className="h-4 w-4 text-muted mr-2" />
        <input 
          type="text" 
          placeholder="Search intel..." 
          className="bg-transparent border-none outline-none text-sm text-foreground w-full placeholder:text-muted/50"
        />
      </div>
      
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-muted hover:text-brand-light transition-colors rounded-full hover:bg-brand/5">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-brand bg-glow"></span>
        </button>
        
        <div className="h-8 w-px bg-brand/20 mx-2"></div>
        
        <button className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-semibold text-foreground">Agent 007</p>
            <p className="text-xs text-brand tracking-widest uppercase">Clearance: Level 4</p>
          </div>
          <div className="h-10 w-10 rounded-full bg-brand/20 border border-brand/50 flex items-center justify-center text-brand-light">
            <User className="h-5 w-5" />
          </div>
        </button>
      </div>
    </header>
  );
}
