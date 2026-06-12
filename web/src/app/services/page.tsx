import { Zap, Database, Cpu, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function ServicesPage() {
  return (
    <div className="pt-32 pb-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-20">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">
          Intelligence <span className="text-brand text-glow">Protocols</span>
        </h1>
        <p className="text-xl text-muted max-w-2xl mx-auto">
          Choose the level of access you need to stay ahead of the curve.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Tier 1: Daily Digest */}
        <div className="glass rounded-3xl p-8 border border-brand/40 shadow-[0_0_30px_rgba(113,27,209,0.15)] relative overflow-hidden flex flex-col">
          <div className="absolute top-0 right-0 w-full h-1 bg-gradient-to-r from-brand to-brand-light" />
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-brand/20 flex items-center justify-center">
              <Zap className="text-brand-light" size={24} />
            </div>
            <h2 className="text-2xl font-bold">The Digest</h2>
          </div>
          <p className="text-muted mb-8 flex-grow">
            The core protocol. A daily, highly-curated tech magazine sent directly to your Telegram.
          </p>
          <div className="mb-8">
            <span className="text-4xl font-extrabold">$0</span>
            <span className="text-muted ml-2">/forever</span>
          </div>
          <ul className="space-y-4 mb-10">
            {['Daily PDF delivery', 'Multi-Model AI curation', 'Dark-mode typography', 'Telegram integration'].map((feature, i) => (
              <li key={i} className="flex items-center gap-3 text-sm text-foreground/90">
                <CheckCircle2 className="text-brand-light" size={18} /> {feature}
              </li>
            ))}
          </ul>
          <Link href="https://t.me/AheadOfEveryoneBot" className="w-full py-4 rounded-xl bg-brand text-white text-center font-bold tracking-widest uppercase hover:bg-brand-light bg-glow transition-all">
            Initialize
          </Link>
        </div>

        {/* Tier 2: B2B API */}
        <div className="glass rounded-3xl p-8 border border-white/5 relative overflow-hidden flex flex-col opacity-60">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
              <Database className="text-muted" size={24} />
            </div>
            <h2 className="text-2xl font-bold">Data API</h2>
          </div>
          <p className="text-muted mb-8 flex-grow">
            Raw firehose access. Plug our scraped intelligence directly into your own dashboards.
          </p>
          <div className="mb-8">
            <span className="text-4xl font-extrabold">TBA</span>
          </div>
          <ul className="space-y-4 mb-10">
            {['REST & GraphQL endpoints', 'Real-time webhooks', 'Historical archive access', 'High rate limits'].map((feature, i) => (
              <li key={i} className="flex items-center gap-3 text-sm text-muted">
                <CheckCircle2 className="text-muted/50" size={18} /> {feature}
              </li>
            ))}
          </ul>
          <button disabled className="w-full py-4 rounded-xl bg-white/5 text-muted text-center font-bold tracking-widest uppercase cursor-not-allowed">
            Coming Soon
          </button>
        </div>

        {/* Tier 3: Consulting */}
        <div className="glass rounded-3xl p-8 border border-white/5 relative overflow-hidden flex flex-col opacity-60">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
              <Cpu className="text-muted" size={24} />
            </div>
            <h2 className="text-2xl font-bold">Architecture</h2>
          </div>
          <p className="text-muted mb-8 flex-grow">
            Bespoke engineering. We build a fully autonomous, serverless AI pipeline for your specific niche.
          </p>
          <div className="mb-8">
            <span className="text-4xl font-extrabold">Custom</span>
          </div>
          <ul className="space-y-4 mb-10">
            {['Custom data sources', 'Dedicated LLM routing', 'White-labeled delivery', 'Zero-maintenance setup'].map((feature, i) => (
              <li key={i} className="flex items-center gap-3 text-sm text-muted">
                <CheckCircle2 className="text-muted/50" size={18} /> {feature}
              </li>
            ))}
          </ul>
          <button disabled className="w-full py-4 rounded-xl bg-white/5 text-muted text-center font-bold tracking-widest uppercase cursor-not-allowed">
            Waitlist Full
          </button>
        </div>
      </div>
    </div>
  );
}
