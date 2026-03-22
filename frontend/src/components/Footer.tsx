import Link from 'next/link';

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="grid gap-10 md:grid-cols-[1.3fr_0.7fr_0.8fr]">
          <div className="max-w-md">
            <p className="text-xl font-semibold tracking-tight text-slate-950">
              <span className="text-accent-glow">SAHAY</span>
              <span className="text-slate-400">.AI</span>
            </p>
            <p className="mt-4 text-sm leading-7 text-slate-600">
              AI-assisted guidance to help Indian citizens discover relevant public welfare schemes with less confusion.
            </p>
            <div className="mt-5 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
              <span className="h-2 w-2 rounded-full bg-emerald-300" />
              Guidance available now
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">Navigation</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-700">
              <li><Link href="/">Home</Link></li>
              <li><Link href="/schemes">Schemes</Link></li>
              <li><Link href="/eligibility">Eligibility</Link></li>
              <li><Link href="/about">About</Link></li>
            </ul>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">Resources</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-700">
              <li>
                <a href="https://www.myscheme.gov.in" target="_blank" rel="noopener noreferrer">
                  MyScheme
                </a>
              </li>
              <li>
                <a href="https://pmkisan.gov.in" target="_blank" rel="noopener noreferrer">
                  PM-KISAN
                </a>
              </li>
              <li>
                <a href="https://pmjay.gov.in" target="_blank" rel="noopener noreferrer">
                  Ayushman Bharat
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-3 border-t border-slate-200 pt-6 text-xs text-slate-500 md:flex-row md:items-center md:justify-between">
          <p>(c) 2026 SAHAY.AI. Informational guidance for public welfare discovery.</p>
          <p>Use official portals to confirm final scheme details and application requirements.</p>
        </div>
      </div>
    </footer>
  );
}
