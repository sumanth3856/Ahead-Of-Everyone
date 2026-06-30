import os

def replace_in_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            modified = True
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated', filepath)

replacements = {
    '"Intelligence.".split("")': '"Newsletter.".split("")',
    'Intelligence Pipeline Active': 'Newsletter Active',
    'Our expanding suite of intelligence services.': 'Our expanding suite of services.',
    'Intelligent routing of prompts': 'Smart routing of prompts',
    'Access Protocols': 'Get Started',
    'Core <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light text-glow">Protocols</span>': 'Core <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-light text-glow">Services</span>',
    'Access Protocol for Daily Tech Digest': 'Get Started with Daily Tech Digest',
    'Access Protocol <ArrowRight size={18} />': 'Get Started <ArrowRight size={18} />',
    'A fully autonomous, AI-powered tech journalism pipeline and intelligence agency.': 'A fully autonomous, AI-powered tech newsletter.',
    'Intelligence <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand via-brand-light to-brand text-glow">Protocols</span>': 'Our <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand via-brand-light to-brand text-glow">Services</span>',
    'Raw firehose access. Plug our scraped intelligence directly into your own dashboards.': 'Raw firehose access. Plug our scraped data directly into your own dashboards.',
    'The core protocol.': 'Our core service.',
    'Intel Dispatched': 'Newsletters Sent',
    'Intelligence Archive': 'Newsletter Archive',
    'No Intel Found': 'No Newsletters Found',
    "Your intelligence pipeline hasn't generated any digests yet.": "Your newsletter hasn't generated any issues yet.",
    'Read Intel': 'Read',
    'Intelligence pipeline active. All systems nominal.': 'Newsletter active. All systems nominal.',
    'Latest intelligence reports': 'Latest newsletters',
    'No intelligence digests available yet.': 'No newsletters available yet.',
    'Configure your intelligence pipeline and personal identity.': 'Configure your newsletter and personal identity.',
    'A critical failure occurred in the intelligence pipeline.': 'A critical failure occurred.',
    'The requested intel could not be located in our systems. The pipeline might have been rerouted or the link is classified.': 'The requested page could not be located.',
    'Initializing intelligence pipeline...': 'Initializing newsletter...',
    'The architecture is designed to run indefinitely without human intervention. Automated cron schedules, fallback LLM routing, and resilient database queries ensure the intelligence keeps flowing.': 'The architecture is designed to run indefinitely without human intervention. Automated cron schedules, fallback LLM routing, and resilient database queries ensure the newsletter keeps flowing.',
    'Your data is your own. The intelligence pipeline runs directly to your secure Telegram client.': 'Your data is your own. The service runs directly to your secure Telegram client.'
}

files = [
    'src/app/(marketing)/page.tsx',
    'src/app/(marketing)/about/page.tsx',
    'src/app/(marketing)/services/page.tsx',
    'src/app/dashboard/admin/page.tsx',
    'src/app/dashboard/digests/page.tsx',
    'src/app/dashboard/page.tsx',
    'src/app/dashboard/settings/page.tsx',
    'src/app/error.tsx',
    'src/app/not-found.tsx',
    'src/components/Footer.tsx',
    'src/components/ui/LiveTerminal.tsx'
]

for f in files:
    filepath = os.path.join('d:\\Projects\\Agentic Projects\\Daily Tech Digest\\web', f.replace('/', '\\'))
    if os.path.exists(filepath):
        replace_in_file(filepath, replacements)
    else:
        print('File not found:', filepath)
