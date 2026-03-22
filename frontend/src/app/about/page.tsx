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
    'Voice input and output for accessible interaction',
    'WhatsApp integration — discover schemes right from your phone',
];

const techStack = ['Next.js', 'FastAPI', 'Groq (Llama 3.3)', 'Sarvam AI', 'ChromaDB'];

export default function AboutPage() {
    return (
        <div className="max-w-4xl mx-auto px-6 py-16">
            {/* Header */}
            <div className="mb-12">
                <h1 className="text-3xl font-semibold text-slate-950 mb-4">About Sahay AI</h1>
                <p className="text-slate-500 text-lg leading-relaxed max-w-2xl">
                    An AI-powered platform designed to help Indian citizens discover and access government welfare schemes — in any language.
                </p>
            </div>

            <div className="space-y-8">
                {/* Mission */}
                <section className="glass-card p-8">
                    <h2 className="text-xl font-medium text-slate-800 mb-4">Our Mission</h2>
                    <p className="text-slate-500 leading-relaxed">
                        To bridge the information gap between government welfare programs and the citizens who need them most.
                        We use AI to simplify the complex landscape of 500+ government schemes across central and state levels.
                    </p>
                </section>

                {/* Features */}
                <section className="glass-card p-8">
                    <h2 className="text-xl font-medium text-slate-800 mb-4">Key Features</h2>
                    <ul className="space-y-3">
                        {features.map((feature, i) => (
                            <li key={i} className="flex items-start gap-3 text-slate-500">
                                <span className="text-emerald-600 mt-1">•</span>
                                <span>{feature}</span>
                            </li>
                        ))}
                    </ul>
                </section>

                {/* Technology */}
                <section className="glass-card p-8">
                    <h2 className="text-xl font-medium text-slate-800 mb-4">Technology</h2>
                    <p className="text-slate-500 leading-relaxed mb-6">
                        Built with modern technologies for speed, reliability, and accessibility.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                        {techStack.map((tech) => (
                            <div key={tech} className="px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-center">
                                <span className="text-slate-700 text-sm font-medium">{tech}</span>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Stats */}
                <section className="glass-card p-8">
                    <div className="grid grid-cols-3 gap-8 text-center">
                        <div>
                            <p className="text-3xl font-bold text-emerald-600">500+</p>
                            <p className="text-slate-400 text-sm mt-1">Schemes</p>
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-emerald-700">10+</p>
                            <p className="text-slate-400 text-sm mt-1">Languages</p>
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-emerald-600">1M+</p>
                            <p className="text-slate-400 text-sm mt-1">Citizens</p>
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
