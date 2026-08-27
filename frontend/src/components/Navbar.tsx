"use client";

import { ArrowUpRight, List, X } from "@phosphor-icons/react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { ThemeToggle } from "./ThemeToggle";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/schemes", label: "Schemes" },
  { href: "/eligibility", label: "Eligibility" },
  { href: "/about", label: "About" },
];

export function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      <header className="island-nav">
        <Link href="/" className="wordmark">
          Sahay<span>.in</span>
        </Link>
        <nav className="nav-links" aria-label="Primary">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              aria-current={pathname === link.href ? "page" : undefined}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Link href="/chat" className="btn btn-primary hidden sm:inline-flex">
            Ask Sahay
            <span className="btn-icon">
              <ArrowUpRight size={16} />
            </span>
          </Link>
          <button
            type="button"
            className="icon-btn lg:hidden"
            onClick={() => setOpen((value) => !value)}
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
          >
            {open ? <X size={18} /> : <List size={18} />}
          </button>
        </div>
      </header>
      {open && (
        <div className="shell mt-3 rounded-[1.5rem] border border-[var(--line)] bg-[var(--surface)] p-4 lg:hidden">
          <div className="flex flex-col gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="rounded-2xl px-4 py-3 text-[var(--ink)]"
                aria-current={pathname === link.href ? "page" : undefined}
              >
                {link.label}
              </Link>
            ))}
            <Link href="/chat" onClick={() => setOpen(false)} className="btn btn-primary mt-2">
              Ask Sahay
              <span className="btn-icon">
                <ArrowUpRight size={16} />
              </span>
            </Link>
          </div>
        </div>
      )}
    </>
  );
}
