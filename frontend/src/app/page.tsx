import { ArrowUpRight, ChatText, IdentificationCard, MagnifyingGlass } from "@phosphor-icons/react/dist/ssr";
import Image from "next/image";
import Link from "next/link";

const mosaic = [
  {
    title: "PM-KISAN",
    detail: "Rs. 6,000 a year for landholding farmer families.",
    href: "/schemes",
    image: "/images/sahay-agriculture.png",
    label: "Agriculture",
  },
  {
    title: "Ayushman Bharat",
    detail: "Up to Rs. 5 lakh hospital cover per eligible family.",
    href: "/schemes",
    image: "/images/sahay-health.png",
    label: "Health",
  },
  {
    title: "PMAY-G",
    detail: "Support to build a pucca house in rural areas.",
    href: "/schemes",
    image: "/images/sahay-housing.png",
    label: "Housing",
  },
  {
    title: "Scholarships",
    detail: "Central student aid through the National Scholarship Portal.",
    href: "/schemes",
    image: "/images/sahay-education.png",
    label: "Education",
  },
];

const languages = [
  "English",
  "Hindi",
  "Telugu",
  "Tamil",
  "Bengali",
  "Marathi",
  "Gujarati",
  "Kannada",
  "Malayalam",
  "Punjabi",
  "Odia",
];

export default function HomePage() {
  return (
    <div>
      <section className="shell grid min-h-[calc(100dvh-6.5rem)] items-center gap-10 pt-10 pb-16 lg:grid-cols-[1.05fr_0.95fr] lg:pt-14">
        <div>
          <p className="kicker">Public scheme guide</p>
          <h1 className="display mt-5">Find the scheme that actually fits you.</h1>
          <p className="lede mt-5">
            Ask in plain language. Get official benefits, documents, and the apply link.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/chat" className="btn btn-primary">
              Ask Sahay
              <span className="btn-icon">
                <ArrowUpRight size={16} />
              </span>
            </Link>
            <Link href="/schemes" className="btn btn-ghost">
              Browse catalog
            </Link>
          </div>
        </div>
        <div className="bezel h-[min(520px,62dvh)]">
          <div className="bezel-inner relative h-full">
            <Image
              src="/images/sahay-hero-desk.png"
              alt="A citizen speaking with a help-desk officer in a small-town office"
              fill
              priority
              className="photo"
              sizes="(min-width: 1024px) 48vw, 100vw"
            />
          </div>
        </div>
      </section>

      <section className="shell grid gap-8 pb-24 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="bezel">
          <div className="bezel-inner relative min-h-[320px]">
            <Image
              src="/images/sahay-agriculture.png"
              alt="A farmer standing in a paddy field at dusk"
              fill
              className="photo"
              sizes="(min-width: 1024px) 40vw, 100vw"
            />
          </div>
        </div>
        <div className="flex flex-col justify-center gap-8">
          <h2 className="max-w-xl text-3xl font-semibold tracking-tight md:text-4xl">
            Three short steps. Then the official portal.
          </h2>
          <ol className="space-y-6">
            <li className="flex gap-4">
              <MagnifyingGlass size={22} className="mt-1 shrink-0" />
              <div>
                <p className="font-semibold">Describe work, place, or a scheme name</p>
                <p className="mt-1 text-[var(--muted)]">
                  Farmer, student, street vendor, or PM-KISAN. Type or speak.
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <IdentificationCard size={22} className="mt-1 shrink-0" />
              <div>
                <p className="font-semibold">See likely matches with documents</p>
                <p className="mt-1 text-[var(--muted)]">
                  Benefits, who it is for, and what to carry. No invented amounts.
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <ChatText size={22} className="mt-1 shrink-0" />
              <div>
                <p className="font-semibold">Open the ministry apply page</p>
                <p className="mt-1 text-[var(--muted)]">
                  Sahay links out. Applications stay on government sites.
                </p>
              </div>
            </li>
          </ol>
        </div>
      </section>

      <section className="shell pb-24">
        <h2 className="max-w-2xl text-3xl font-semibold tracking-tight md:text-4xl">
          A catalog of flagship central schemes, kept as structured records.
        </h2>
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {mosaic.map((item, index) => (
            <Link
              key={item.title}
              href={item.href}
              className={`group bezel ${index === 0 ? "md:col-span-2" : ""}`}
            >
              <div className={`bezel-inner relative ${index === 0 ? "min-h-[280px]" : "min-h-[240px]"}`}>
                <Image
                  src={item.image}
                  alt=""
                  fill
                  className="photo transition-transform duration-700 group-hover:scale-[1.03]"
                  sizes="(min-width: 768px) 50vw, 100vw"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[rgba(17,22,19,0.72)] to-transparent" />
                <div className="absolute bottom-0 p-6 text-[#f6f3ea]">
                  <p className="scheme-chip bg-white/15 text-[#f6f3ea]">{item.label}</p>
                  <h3 className="mt-3 text-2xl font-semibold">{item.title}</h3>
                  <p className="mt-2 max-w-md text-sm leading-6 text-white/85">{item.detail}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="shell pb-24">
        <p className="text-sm text-[var(--muted)]">Ask in any of these languages</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {languages.map((language) => (
            <span
              key={language}
              className="rounded-full border border-[var(--line)] px-4 py-2 text-sm"
            >
              {language}
            </span>
          ))}
        </div>
      </section>

      <section className="shell pb-28">
        <div className="bezel">
          <div className="bezel-inner px-8 py-12 md:px-14 md:py-16">
            <h2 className="max-w-2xl text-3xl font-semibold tracking-tight md:text-4xl">
              Start with one sentence about your family or work.
            </h2>
            <p className="lede mt-4">
              Sahay retrieves from official scheme records, then answers. Confirm the last mile on the ministry site.
            </p>
            <Link href="/chat" className="btn btn-primary mt-8">
              Open chat
              <span className="btn-icon">
                <ArrowUpRight size={16} />
              </span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
