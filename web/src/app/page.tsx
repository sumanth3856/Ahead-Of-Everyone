import Image from "next/image";
import Link from "next/link";
import { ArrowRight, Zap, Database, Cpu } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden pt-20">
        {/* Background glow effects */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-brand/20 rounded-full blur-[120px] -z-10" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-brand/30 bg-brand/10 text-brand-light text-xs font-semibold tracking-widest uppercase shadow-[0_0_15px_rgba(113,27,209,0.3)]">
            Intelligence Pipeline Active
          </div>
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-extrabold tracking-tight mb-8">
            <span className="text-foreground">Five minutes.</span>
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light text-glow leading-tight block pb-4">
              ahead of everyone.
            </span>
          </h1>
          <p className="mt-4 text-xl text-muted max-w-2xl mx-auto mb-10 leading-relaxed">
            A fully autonomous, AI-powered tech journalism pipeline. We scrape, analyze, and deliver a premium cyberpunk magazine straight to you.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link href="/services" className="px-8 py-4 rounded-lg bg-brand text-white font-semibold tracking-wider hover:bg-brand-light bg-glow transition-all duration-300 flex items-center justify-center gap-2 group">
              Explore Services <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/about" className="px-8 py-4 rounded-lg glass text-foreground font-semibold tracking-wider hover:bg-white/10 transition-all duration-300">
              How it works
            </Link>
          </div>
        </div>
      </section>

      {/* Services Preview Section */}
      <section className="w-full py-32 bg-surface/30 border-t border-brand/10 relative">
        <div className="absolute left-0 top-0 w-1/3 h-full bg-gradient-to-r from-brand/5 to-transparent -z-10" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold tracking-wider mb-4">Core <span className="text-brand">Protocols</span></h2>
            <p className="text-muted text-lg">Our expanding suite of intelligence services.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Daily Tech Digest Card */}
            <div className="glass p-10 rounded-2xl border border-brand/40 hover:border-brand shadow-[0_0_30px_rgba(113,27,209,0.1)] hover:shadow-[0_0_40px_rgba(113,27,209,0.2)] transition-all duration-500 group hover:-translate-y-2 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-brand/10 rounded-bl-full -z-10 group-hover:bg-brand/20 transition-colors" />
              <div className="w-16 h-16 rounded-xl bg-brand/20 flex items-center justify-center mb-8 group-hover:bg-brand/40 transition-colors">
                <Zap className="text-brand-light" size={32} />
              </div>
              <h3 className="text-2xl font-bold mb-4 text-foreground tracking-wide">Daily Tech Digest</h3>
              <p className="text-muted mb-8 line-clamp-3 leading-relaxed">
                Our flagship product. A stunning dark-mode PDF magazine delivered to Telegram every morning, curated by our Multi-Model AI Cascade.
              </p>
              <Link href="/services" className="text-brand-light font-medium tracking-wide flex items-center gap-2 group-hover:gap-4 transition-all">
                Access Protocol <ArrowRight size={18} />
              </Link>
            </div>

            {/* Placeholder Service 1 */}
            <div className="glass p-10 rounded-2xl border border-white/5 hover:border-brand/30 transition-all duration-500 group hover:-translate-y-2 relative overflow-hidden">
              <div className="w-16 h-16 rounded-xl bg-white/5 flex items-center justify-center mb-8 group-hover:bg-brand/20 transition-colors">
                <Database className="text-muted group-hover:text-brand-light transition-colors" size={32} />
              </div>
              <h3 className="text-2xl font-bold mb-4 text-foreground opacity-80 tracking-wide">B2B Data API</h3>
              <p className="text-muted mb-8 opacity-80 leading-relaxed">
                Direct access to our aggregated tech data and synthesized insights. Build your own dashboards and customized intelligence alerts.
              </p>
              <span className="text-xs uppercase tracking-widest text-brand-light border border-brand/20 bg-brand/5 px-4 py-1.5 rounded-full font-semibold">Coming Soon</span>
            </div>

            {/* Placeholder Service 2 */}
            <div className="glass p-10 rounded-2xl border border-white/5 hover:border-brand/30 transition-all duration-500 group hover:-translate-y-2 relative overflow-hidden">
              <div className="w-16 h-16 rounded-xl bg-white/5 flex items-center justify-center mb-8 group-hover:bg-brand/20 transition-colors">
                <Cpu className="text-muted group-hover:text-brand-light transition-colors" size={32} />
              </div>
              <h3 className="text-2xl font-bold mb-4 text-foreground opacity-80 tracking-wide">AI Consultation</h3>
              <p className="text-muted mb-8 opacity-80 leading-relaxed">
                Leverage our architecture for your own autonomous pipelines. Serverless, zero-maintenance, and designed for infinite scale.
              </p>
              <span className="text-xs uppercase tracking-widest text-brand-light border border-brand/20 bg-brand/5 px-4 py-1.5 rounded-full font-semibold">Coming Soon</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
