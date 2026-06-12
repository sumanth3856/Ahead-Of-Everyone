import Image from "next/image";

export default function AboutPage() {
  return (
    <div className="pt-32 pb-24 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-16">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">
          The <span className="text-brand text-glow">Philosophy</span>
        </h1>
        <p className="text-xl text-muted leading-relaxed">
          In an era of information overload, speed and signal-to-noise ratio are the ultimate competitive advantages. 
        </p>
      </div>

      <div className="glass rounded-3xl p-8 md:p-12 border border-brand/20 shadow-[0_0_40px_rgba(113,27,209,0.05)] relative overflow-hidden mb-16">
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-brand/20 rounded-full blur-[80px] -z-10" />
        
        <h2 className="text-2xl font-bold mb-6 text-foreground">Five minutes. Then you are ahead of everyone.</h2>
        <div className="space-y-6 text-muted leading-relaxed">
          <p>
            The tech industry moves at breakneck speed. Every day, thousands of articles, press releases, and HackerNews threads are generated. Reading them all is impossible. Missing them is a liability.
          </p>
          <p>
            <strong>Ahead Of Everyone</strong> was built as an autonomous solution to this problem. Our core pipeline operates 100% serverlessly. It scrapes the global tech news ecosystem every 24 hours and feeds the raw data into a Multi-Model AI Cascade.
          </p>
          <p>
            The AI acts as an elite editorial team, stripping away the fluff and synthesizing the pure signal into a premium, dark-mode magazine.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="glass rounded-3xl p-8 border border-white/5 relative overflow-hidden">
          <h3 className="text-xl font-bold mb-4 text-foreground">Zero Maintenance</h3>
          <p className="text-muted text-sm leading-relaxed">
            The architecture is designed to run indefinitely without human intervention. Automated cron schedules, fallback LLM routing, and resilient database queries ensure the intelligence keeps flowing.
          </p>
        </div>
        
        <div className="glass rounded-3xl p-8 border border-white/5 relative overflow-hidden">
          <h3 className="text-xl font-bold mb-4 text-foreground">Premium UX</h3>
          <p className="text-muted text-sm leading-relaxed">
            We believe data shouldn't just be accurate; it should be beautiful. From our custom PDF generation engine using Montserrat typography, to this very web interface.
          </p>
        </div>
      </div>
    </div>
  );
}
