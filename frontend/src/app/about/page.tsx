import Link from 'next/link';

export const metadata = {
    title: 'About — SAHAY.AI',
    description: 'Learn about Sahay AI and our mission to help citizens access government schemes',
};

const features = [
    'Multilingual support for 10+ Indian languages including Hindi, Telugu, Tamil, Bengali',
    'AI-powered eligibility checking based on your profile',
    'Real-time scheme information from official government sources',
    'Step-by-step application guidance and document requirements',
    'Voice input support for accessible interaction',
];

const techStack = ['Next.js', 'FastAPI', 'Google Gemini', 'Supabase'];

export default function AboutPage() {
    return (
        <div className="max-w-4xl mx-auto px-6 py-16">
            {/* Header */}
            <div className="mb-12">
                <h1 className="text-3xl font-semibold text-zinc-100 mb-4">About Sahay AI</h1>
                <p className="text-zinc-400 text-lg leading-relaxed max-w-2xl">
                    An AI-powered platform designed to help Indian citizens discover and access government welfare schemes — in any language.
                </p>
            </div>

            <div className="space-y-8">
                {/* Mission */}
                <section className="glass-card-accent p-8">
                    <h2 className="text-xl font-medium text-zinc-100 mb-4">Our Mission</h2>
                    <p className="text-zinc-400 leading-relaxed">
                        To bridge the information gap between government welfare programs and the citizens who need them most.
                        We use AI to simplify the complex landscape of 500+ government schemes across central and state levels.
                    </p>
                </section>

                {/* Features */}
                <section className="glass-card-accent p-8">
                    <h2 className="text-xl font-medium text-zinc-100 mb-4">Key Features</h2>
                    <ul className="space-y-3">
                        {features.map((feature, i) => (
                            <li key={i} className="flex items-start gap-3 text-zinc-400">
                                <span className="text-emerald-400 mt-1">•</span>
                                <span>{feature}</span>
                            </li>
                        ))}
                    </ul>
                </section>

                {/* Technology */}
                <section className="glass-card-accent p-8">
                    <h2 className="text-xl font-medium text-zinc-100 mb-4">Technology</h2>
                    <p className="text-zinc-400 leading-relaxed mb-6">
                        Built with modern technologies for speed, reliability, and accessibility.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {techStack.map((tech) => (
                            <div key={tech} className="px-4 py-3 bg-zinc-900/50 border border-zinc-800 rounded-lg text-center">
                                <span className="text-zinc-200 text-sm">{tech}</span>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Stats */}
                <section className="glass-card p-8">
                    <div className="grid grid-cols-3 gap-8 text-center">
                        <div>
                            <p className="text-3xl font-bold text-emerald-400">500+</p>
                            <p className="text-zinc-500 text-sm mt-1">Schemes</p>
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-cyan-400">10+</p>
                            <p className="text-zinc-500 text-sm mt-1">Languages</p>
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-emerald-400">1M+</p>
                            <p className="text-zinc-500 text-sm mt-1">Citizens</p>
                        </div>
                    </div>
                </section>
            </div>

            {/* CTA */}
            <div className="mt-12 text-center">
                <Link href="/chat" className="btn-primary gap-2">
                    Start Chatting
                    <span>→</span>
                </Link>
            </div>
        </div>
    );
}
