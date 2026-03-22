'use client';

import Link from 'next/link';

const stats = [
  { value: '500+', label: 'Schemes indexed' },
  { value: '10+', label: 'Indian languages' },
  { value: '1M+', label: 'Citizens supported' },
];

const features = [
  {
    title: 'AI-guided scheme discovery',
    description:
      'Share your location, occupation, income range, and needs. SAHAY narrows large government catalogs into the programs worth your time.',
    icon: 'discovery',
  },
  {
    title: 'Multilingual conversation',
    description:
      'Users can ask questions in Hindi, Tamil, Telugu, Bengali, or English without switching tools or translating government terms manually.',
    icon: 'language',
  },
  {
    title: 'Eligibility pre-check',
    description:
      'Simple guided questions help users understand whether they likely qualify before they gather documents or visit an office.',
    icon: 'eligibility',
  },
];

const schemes = [
  {
    name: 'PM-KISAN',
    category: 'Agriculture',
    description: 'Income support of Rs. 6,000 per year for eligible farmer families.',
  },
  {
    name: 'Ayushman Bharat',
    category: 'Health',
    description: 'Health coverage of Rs. 5 lakh per family per year for eligible households.',
  },
  {
    name: 'PM Awas Yojana',
    category: 'Housing',
    description: 'Housing support with subsidized financing for qualifying urban and rural applicants.',
  },
];

const journeySteps = [
  'Describe your family, work, and location in plain language.',
  'Review recommended schemes with plain-language summaries.',
  'Check likely eligibility and prepare for next application steps.',
];

function FeatureIcon({ icon }: { icon: string }) {
  if (icon === 'discovery') {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5">
        <path
          d="M11 4a7 7 0 1 0 4.89 12.01L20 20.12"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="1.8"
        />
      </svg>
    );
  }

  if (icon === 'language') {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5">
        <path
          d="M4 6h10M9 6c0 5-2 8-5 10m4-5c1.5 2.3 3.6 4.2 6 5M15 6l5 12m-1.5-3.5h-6.8"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="1.8"
        />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5">
      <path
        d="M5 12.5 9.2 17 19 7.5"
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

export default function HomePage() {
  return (
    <div className="relative overflow-hidden">
      <section className="px-6 pt-14 pb-16 md:pt-20 md:pb-20">
        <div className="hero-shell mx-auto max-w-6xl">
          <div className="hero-grid">
            <div className="space-y-8">
              <span className="kicker">Government scheme discovery, without portal fatigue</span>
              <div className="max-w-3xl space-y-5">
                <p className="text-sm font-semibold uppercase tracking-[0.3em] text-emerald-700/80">
                  SAHAY.AI
                </p>
                <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl lg:leading-[1.05]">
                  Find the right government scheme faster, with AI that speaks your language.
                </h1>
                <p className="max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
                  SAHAY helps citizens navigate large welfare catalogs, understand likely eligibility,
                  and move toward the next application step with less confusion and less guesswork.
                </p>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <Link href="/chat" className="btn-primary gap-2">
                  Start chat
                </Link>
                <Link href="/schemes" className="btn-outline">
                  Browse schemes
                </Link>
              </div>

              <div className="flex flex-wrap gap-3 text-sm text-slate-600">
                <span className="chip">Plain-language recommendations</span>
                <span className="chip">Regional language support</span>
                <span className="chip">Eligibility guidance</span>
              </div>
            </div>

            <aside className="surface-accent p-6 md:p-8">
              <div className="space-y-6">
                <div className="space-y-2">
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-700/80">
                    How SAHAY helps
                  </p>
                  <h2 className="text-2xl font-semibold tracking-tight text-slate-950">
                    One guided path from question to next step
                  </h2>
                  <p className="text-sm leading-7 text-slate-600">
                    The product should feel calm and directional, not like another dense government portal.
                  </p>
                </div>

                <div className="space-y-4">
                  {journeySteps.map((step, index) => (
                    <div key={step} className="flex gap-4 rounded-2xl border border-slate-200 bg-white p-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-sm font-semibold text-emerald-700">
                        0{index + 1}
                      </div>
                      <p className="text-sm leading-7 text-slate-700">{step}</p>
                    </div>
                  ))}
                </div>

                <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
                  {stats.map((stat) => (
                    <div key={stat.label} className="stat-card">
                      <p className="text-2xl font-semibold tracking-tight text-slate-950">{stat.value}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-500">{stat.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </div>
      </section>

      <section className="px-6 pb-20 md:pb-24">
        <div className="mx-auto max-w-6xl">
          <div className="section-heading">
            <span className="kicker">What you can do here</span>
            <h2 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              A cleaner path through complex public programs
            </h2>
            <p className="max-w-2xl text-base leading-8 text-slate-600">
              The homepage should immediately explain the product, show credibility, and make the next action obvious.
            </p>
          </div>

          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {features.map((feature) => (
              <article key={feature.title} className="glass-card p-7">
                <div className="icon-badge">
                  <FeatureIcon icon={feature.icon} />
                </div>
                <h3 className="mt-5 text-xl font-semibold tracking-tight text-slate-950">{feature.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{feature.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-slate-200 px-6 py-20 md:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="section-heading">
            <span className="kicker">Representative programs</span>
            <h2 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Show real schemes, not just abstract promises
            </h2>
            <p className="max-w-2xl text-base leading-8 text-slate-600">
              A few recognizable examples help visitors quickly understand the kind of support they can explore.
            </p>
          </div>

          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {schemes.map((scheme) => (
              <Link href="/schemes" key={scheme.name} className="glass-card-accent p-7">
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-700/80">
                  {scheme.category}
                </p>
                <h3 className="mt-4 text-2xl font-semibold tracking-tight text-slate-950">{scheme.name}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{scheme.description}</p>
                <p className="mt-6 text-sm font-medium text-emerald-700">View scheme details</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-20 md:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="surface-panel mx-auto max-w-4xl p-8 text-center md:p-12">
            <span className="kicker justify-center">Ready to explore benefits</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Start with a short conversation and narrow the search quickly.
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-base leading-8 text-slate-600">
              The next action should be obvious: ask a question, describe your situation, and move directly into recommendations.
            </p>
            <div className="mt-8 flex justify-center">
              <Link href="/chat" className="btn-primary">
                Launch chat
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
