import Link from "next/link";

export function Footer() {
  return (
    <footer className="footer">
      <div className="shell grid gap-10 md:grid-cols-[1.4fr_0.8fr_0.8fr]">
        <div>
          <p className="wordmark text-xl">
            Sahay<span>.in</span>
          </p>
          <p className="mt-4 max-w-sm text-sm leading-7 text-[var(--muted)]">
            A public-interest guide to central welfare schemes. We point you to official
            portals. We do not submit applications for you.
          </p>
        </div>
        <div>
          <p className="text-sm font-semibold">Product</p>
          <ul className="mt-4 space-y-3 text-sm text-[var(--muted)]">
            <li><Link href="/schemes">Browse schemes</Link></li>
            <li><Link href="/eligibility">Check eligibility</Link></li>
            <li><Link href="/chat">Ask Sahay</Link></li>
            <li><Link href="/about">About</Link></li>
          </ul>
        </div>
        <div>
          <p className="text-sm font-semibold">Official sources</p>
          <ul className="mt-4 space-y-3 text-sm text-[var(--muted)]">
            <li>
              <a href="https://www.myscheme.gov.in/" target="_blank" rel="noreferrer">
                myScheme
              </a>
            </li>
            <li>
              <a href="https://pmkisan.gov.in/" target="_blank" rel="noreferrer">
                PM-KISAN
              </a>
            </li>
            <li>
              <a href="https://www.pmjay.gov.in/" target="_blank" rel="noreferrer">
                Ayushman Bharat
              </a>
            </li>
            <li><Link href="/privacy">Privacy</Link></li>
            <li><Link href="/terms">Terms</Link></li>
          </ul>
        </div>
      </div>
      <div className="shell mt-10 flex flex-col gap-2 border-t border-[var(--line)] pt-5 text-xs text-[var(--faint)] md:flex-row md:justify-between">
        <p>(c) 2026 Sahay. Informational guidance only.</p>
        <p>Confirm amounts and eligibility on the ministry website before you apply.</p>
      </div>
    </footer>
  );
}
