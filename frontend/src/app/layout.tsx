import type { Metadata } from "next";
import { IBM_Plex_Mono, Outfit } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { ThemeScript } from "@/components/ThemeScript";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

const ibmPlex = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-ibm",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Sahay - Find the government scheme that fits",
  description:
    "Sahay helps Indian citizens find central welfare schemes, understand likely eligibility, and reach the official apply page.",
  openGraph: {
    title: "Sahay - Find the government scheme that fits",
    description:
      "Ask in plain language. Get scheme matches with benefits, documents, and official links.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className={`${outfit.variable} ${ibmPlex.variable} ${outfit.className}`}>
        <a href="#main-content" className="skip-link">
          Skip to content
        </a>
        <Navbar />
        <main id="main-content">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
