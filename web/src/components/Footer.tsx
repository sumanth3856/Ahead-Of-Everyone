import Link from "next/link";
import Image from "next/image";
import { Terminal, Globe, Send } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-surface/50 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <Link href="/" className="flex items-center gap-3 group mb-4">
              <div className="relative w-10 h-10 overflow-hidden rounded-lg group-hover:shadow-md transition-all duration-500 bg-surface-hover">
                <Image src="/logo.png" alt="AoE Logo" fill className="object-cover" />
              </div>
              <span className="font-bold text-xl tracking-wider text-foreground group-hover:text-brand transition-colors">
                AHEAD OF <span className="text-brand group-hover:text-foreground transition-colors">EVERYONE</span>
              </span>
            </Link>
            <p className="text-muted text-sm max-w-xs font-medium">
              A fully autonomous, AI-powered tech journalism pipeline and intelligence agency. Five minutes. Then you are ahead of everyone.
            </p>
          </div>
          
          <div>
            <h3 className="font-bold text-foreground tracking-widest uppercase text-sm mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link href="/" className="text-muted hover:text-brand font-medium transition-colors text-sm">Home</Link></li>
              <li><Link href="/services" className="text-muted hover:text-brand font-medium transition-colors text-sm">Services</Link></li>
              <li><Link href="/about" className="text-muted hover:text-brand font-medium transition-colors text-sm">About</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-foreground tracking-widest uppercase text-sm mb-4">Connect</h3>
            <div className="flex space-x-4">
              <a href="#" className="w-10 h-10 rounded-full border border-border-subtle flex items-center justify-center text-muted hover:text-brand hover:border-brand shadow-sm transition-all">
                <Terminal size={18} />
              </a>
              <a href="#" className="w-10 h-10 rounded-full border border-border-subtle flex items-center justify-center text-muted hover:text-brand hover:border-brand shadow-sm transition-all">
                <Globe size={18} />
              </a>
              <a href="#" className="w-10 h-10 rounded-full border border-border-subtle flex items-center justify-center text-muted hover:text-brand hover:border-brand shadow-sm transition-all">
                <Send size={18} />
              </a>
            </div>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-border-subtle flex flex-col md:flex-row justify-between items-center">
          <p className="text-muted font-medium text-xs">
            © {new Date().getFullYear()} Ahead Of Everyone. Engineered by Sumanth.
          </p>
          <div className="mt-4 md:mt-0 flex space-x-4">
            <Link href="#" className="text-muted font-medium hover:text-brand text-xs">Privacy</Link>
            <Link href="#" className="text-muted font-medium hover:text-brand text-xs">Terms</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
