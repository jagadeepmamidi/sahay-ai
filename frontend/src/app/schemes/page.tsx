"use client";

import { useState, useEffect } from "react";
import { getSchemes, getCategories, getSchemeDetails } from "@/lib/api";
import { Scheme, SchemeListItem } from "@/types";

function formatCategoryLabel(category: string) {
  const primaryCategory = category.split(",")[0]?.replace(/\s+/g, " ").trim();
  return primaryCategory || "General";
}

function dedupeCategories(values: string[]) {
  return Array.from(new Set(values.map(formatCategoryLabel)));
}

function cleanInlineLinks(text: string) {
  return text
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/gi, "$1: $2")
    .replace(/\s+/g, " ")
    .trim();
}

function formatApplicationSteps(text: string) {
  const cleaned = cleanInlineLinks(text);
  if (!cleaned) {
    return [];
  }

  const numberedMatches = cleaned.match(/\d+\.\s.*?(?=\s+\d+\.\s|$)/g);
  if (numberedMatches && numberedMatches.length > 0) {
    return numberedMatches.map((step) => step.replace(/^\d+\.\s*/, "").trim());
  }

  return cleaned
    .split(/(?<=[.!?])\s+(?=[A-Z])/)
    .map((step) => step.trim())
    .filter(Boolean);
}

export default function SchemesPage() {
  const [schemes, setSchemes] = useState<SchemeListItem[]>([]);
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedScheme, setSelectedScheme] = useState<Scheme | null>(null);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");

  const applicationSteps = selectedScheme
    ? formatApplicationSteps(selectedScheme.application_process || "")
    : [];

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = (await getCategories()) as { categories: string[] };
        setCategories(["All", ...dedupeCategories(data.categories)]);
      } catch (err) {
        console.error("Failed to fetch categories:", err);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchSchemes = async () => {
      setIsLoading(true);
      try {
        const data = (await getSchemes(
          page,
          10,
          activeCategory === "All" ? undefined : activeCategory,
          undefined,
          search || undefined,
        )) as { schemes: SchemeListItem[]; total_pages: number };
        setSchemes(data.schemes);
        setTotalPages(data.total_pages);
      } catch (err) {
        console.error("Failed to fetch schemes:", err);
      } finally {
        setIsLoading(false);
      }
    };

    const timer = setTimeout(() => {
      fetchSchemes();
    }, 300);

    return () => clearTimeout(timer);
  }, [page, activeCategory, search]);

  const openSchemeDetails = async (schemeId: string) => {
    setIsDetailsLoading(true);
    setDetailsError("");
    try {
      const details = (await getSchemeDetails(schemeId)) as Scheme;
      setSelectedScheme(details);
    } catch (err) {
      console.error("Failed to fetch scheme details:", err);
      setDetailsError("Failed to load scheme details. Please try again.");
    } finally {
      setIsDetailsLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-slate-950 mb-2">
          Government Schemes
        </h1>
        <p className="text-slate-500 text-sm">
          Browse official schemes across categories
        </p>
      </div>

      {/* Search */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search schemes..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 text-sm transition-colors"
        />
      </div>

      {/* Categories */}
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400 mb-3">
          Browse by Topic
        </p>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => {
                setActiveCategory(cat);
                setPage(1);
              }}
              className={`whitespace-nowrap rounded-full px-4 py-2.5 text-sm transition-colors ${
                activeCategory === cat
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 border border-slate-200 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              {formatCategoryLabel(cat)}
            </button>
          ))}
        </div>
      </div>

      {/* Schemes Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="h-4 w-20 bg-slate-200 rounded mb-3" />
              <div className="h-5 w-3/4 bg-slate-200 rounded mb-3" />
              <div className="h-4 w-full bg-slate-200 rounded" />
            </div>
          ))}
        </div>
      ) : schemes.length > 0 ? (
        <>
          <div className="grid md:grid-cols-2 gap-4">
            {schemes.map((scheme) => (
              <button
                key={scheme.id}
                type="button"
                onClick={() => openSchemeDetails(scheme.id)}
                className="glass-card p-6 group hover:border-emerald-200 transition-colors text-left h-full"
              >
                <div className="mb-4">
                  <span className="inline-flex max-w-full rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-emerald-700">
                    {formatCategoryLabel(scheme.category)}
                  </span>
                </div>
                <h3 className="text-slate-800 font-medium text-lg group-hover:text-emerald-700 transition-colors leading-snug break-words mb-3">
                  {scheme.name}
                </h3>
                <p className="text-slate-500 text-sm line-clamp-3 leading-relaxed">
                  {scheme.eligibility_summary || "Click for details"}
                </p>
                {scheme.benefit_summary && (
                  <p className="text-emerald-600 text-sm mt-4">
                    Benefit: {scheme.benefit_summary}
                  </p>
                )}
              </button>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-6 mt-12">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="text-slate-500 hover:text-emerald-600 disabled:opacity-30 disabled:hover:text-slate-500 transition-colors text-sm"
              >
                ← Previous
              </button>
              <span className="text-slate-400 text-sm">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="text-slate-500 hover:text-emerald-600 disabled:opacity-30 disabled:hover:text-slate-500 transition-colors text-sm"
              >
                Next →
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-20 glass-card">
          <p className="text-slate-600 text-lg mb-2">No results found</p>
          <p className="text-slate-400 text-sm">
            Try adjusting your search or category filters.
          </p>
        </div>
      )}

      {(isDetailsLoading || selectedScheme || detailsError) && (
        <div className="fixed inset-0 z-50 bg-slate-950/30 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-2xl bg-white border border-slate-200 rounded-2xl shadow-xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-xl font-semibold text-slate-900">
                Scheme details
              </h2>
              <button
                type="button"
                onClick={() => {
                  setSelectedScheme(null);
                  setDetailsError("");
                  setIsDetailsLoading(false);
                }}
                className="text-slate-500 hover:text-slate-700"
              >
                Close
              </button>
            </div>

            {isDetailsLoading && (
              <p className="text-slate-500 text-sm">Loading details...</p>
            )}

            {!isDetailsLoading && detailsError && (
              <p className="text-red-600 text-sm">{detailsError}</p>
            )}

            {!isDetailsLoading && selectedScheme && (
              <div className="space-y-4">
                <div className="space-y-3">
                  <span className="inline-flex max-w-full rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-emerald-700">
                    {formatCategoryLabel(selectedScheme.category)}
                  </span>
                  <h3 className="text-xl font-semibold text-slate-900 leading-snug break-words">
                    {selectedScheme.name}
                  </h3>
                </div>
                <p className="text-slate-700 text-sm leading-relaxed">
                  {selectedScheme.description || "No description available."}
                </p>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400 mb-2">
                      Benefit
                    </p>
                    <p className="text-sm text-emerald-700 leading-relaxed">
                      {selectedScheme.benefit_amount ||
                        selectedScheme.benefits ||
                        "Not specified"}
                    </p>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400 mb-2">
                      Eligibility
                    </p>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      {selectedScheme.eligibility_summary ||
                        "Refer official guidelines"}
                    </p>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 md:col-span-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400 mb-2">
                      How to Apply
                    </p>
                    {applicationSteps.length > 0 ? (
                      <ol className="space-y-2 text-sm text-slate-600 leading-relaxed">
                        {applicationSteps.map((step, index) => (
                          <li
                            key={`${selectedScheme.id}-step-${index}`}
                            className="flex gap-3"
                          >
                            <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white text-[11px] font-semibold text-slate-500 border border-slate-200">
                              {index + 1}
                            </span>
                            <span className="break-words">{step}</span>
                          </li>
                        ))}
                      </ol>
                    ) : (
                      <p className="text-sm text-slate-600 leading-relaxed">
                        Refer official portal
                      </p>
                    )}
                  </div>
                </div>
                {selectedScheme.apply_url && (
                  <a
                    href={selectedScheme.apply_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100 transition-colors"
                  >
                    Open official link
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
