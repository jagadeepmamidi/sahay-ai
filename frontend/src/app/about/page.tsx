import Link from "next/link";

export const metadata = {
  title: "About Sahay",
  description: "Why Sahay exists and how the scheme catalog is built.",
};

export default function AboutPage() {
  return (
    <div className="shell py-12 md:py-16">
      <h1 className="max-w-2xl text-4xl font-semibold tracking-tight">Built to cut through scheme noise</h1>
      <p className="lede mt-4">
        Most people do not fail eligibility. They never find the right portal. Sahay is a retrieval layer over official records, not a replacement for government websites.
      </p>

      <div className="mt-12 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="bezel">
          <div className="bezel-inner p-8">
            <h2 className="text-2xl font-semibold">How answers are produced</h2>
            <p className="mt-4 text-[var(--muted)] leading-7">
              Each scheme is stored as a structured record: benefits, eligibility rules, documents, and the official URL. Search is lexical (BM25 plus aliases). The language model may only speak from those records.
            </p>
            <p className="mt-4 text-[var(--muted)] leading-7">
              Uploaded PDFs can extend the catalog later. They are not required for chat to work, and they do not load a large embedding model on every question.
            </p>
          </div>
        </section>
        <section className="rounded-[2rem] bg-[var(--forest)] p-8 text-[#f6f3ea]">
          <h2 className="text-2xl font-semibold">What we will not do</h2>
          <ul className="mt-5 space-y-3 text-sm leading-7 text-white/85">
            <li>Invent benefit amounts or deadlines</li>
            <li>Submit applications on your behalf</li>
            <li>Replace Aadhaar, bank, or ministry verification</li>
          </ul>
        </section>
      </div>

      <Link href="/chat" className="btn btn-primary mt-10">
        Ask Sahay
      </Link>
    </div>
  );
}
