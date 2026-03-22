'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/schemes', label: 'Schemes' },
  { href: '/eligibility', label: 'Eligibility' },
  { href: '/about', label: 'About' },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex h-[4.5rem] items-center justify-between gap-4">
          <Link href="/" className="flex shrink-0 items-center gap-2">
            <span className="text-xl font-semibold tracking-tight text-slate-950">
              <span className="text-accent-glow">SAHAY</span>
              <span className="text-slate-400">.AI</span>
            </span>
          </Link>

          <div className="hidden flex-1 items-center justify-center lg:flex">
            <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 p-1">
              {navLinks.map((link) => {
                const isActive = pathname === link.href;

                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    aria-current={isActive ? 'page' : undefined}
                    className={`rounded-full px-4 py-2 text-sm font-medium ${
                      isActive
                        ? 'bg-emerald-50 text-emerald-700'
                        : 'text-slate-600 hover:bg-white hover:text-slate-950'
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="hidden shrink-0 items-center gap-3 lg:flex">
            <Link href="/chat" className="btn-primary">
              Start chat
            </Link>
          </div>

          <button
            type="button"
            onClick={() => setMobileMenuOpen((open) => !open)}
            className="inline-flex rounded-full border border-slate-200 bg-white p-2 text-slate-700 lg:hidden"
            aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-navigation"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M6 6 18 18M18 6 6 18" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M4 7h16M4 12h16M4 17h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div id="mobile-navigation" className="border-t border-slate-200 bg-white lg:hidden">
          <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-4">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`rounded-2xl px-4 py-3 text-sm font-medium ${
                    isActive
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'text-slate-700 hover:bg-slate-50 hover:text-slate-950'
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
            <Link href="/chat" onClick={() => setMobileMenuOpen(false)} className="btn-primary mt-2">
              Start chat
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
