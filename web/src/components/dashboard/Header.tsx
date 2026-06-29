import Link from "next/link";

export default function Header() {
  return (
    <header className="md:hidden h-20 border-b border-border-subtle/90 backdrop-blur-xl flex items-center justify-between pl-4 pr-[72px] z-10 sticky top-0 shadow-sm">
      <div className="flex items-center gap-4 w-full">
        {/* Mobile Logo */}
        <Link href="/" className="flex items-center gap-2 group shrink min-w-0">
          <div className="relative w-9 h-9 sm:w-12 sm:h-12 shrink-0 rounded-lg overflow-hidden group-hover:opacity-80 transition-opacity bg-surface">
            <img src="/logo.jpg" alt="Logo" className="w-full h-full object-contain" />
          </div>
          <span className="font-bold text-base sm:text-xl tracking-wider text-foreground group-hover:text-brand transition-colors truncate">
            AHEAD OF <span className="text-brand group-hover:text-foreground transition-colors">EVERY1</span>
          </span>
        </Link>
      </div>
    </header>
  );
}
