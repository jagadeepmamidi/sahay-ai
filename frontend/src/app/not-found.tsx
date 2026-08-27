import Link from "next/link";

export default function NotFound() {
  return (
    <div className="shell py-24 text-center">
      <p className="kicker justify-center">404</p>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight">This page is not in the catalog</h1>
      <p className="mx-auto mt-3 max-w-md text-[var(--muted)]">
        The link may be old. Head home or ask Sahay for a scheme by name.
      </p>
      <div className="mt-8 flex justify-center gap-3">
        <Link href="/" className="btn btn-primary">
          Home
        </Link>
        <Link href="/chat" className="btn btn-ghost">
          Ask Sahay
        </Link>
      </div>
    </div>
  );
}
