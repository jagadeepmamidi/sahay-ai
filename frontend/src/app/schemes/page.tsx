"use client";

import { useEffect, useState } from "react";
import { X } from "@phosphor-icons/react";
import { getCategories, getSchemeDetails, getSchemes } from "@/lib/api";
import { Scheme, SchemeListItem } from "@/types";

function formatCategoryLabel(category: string) {
  return category.split(",")[0]?.replace(/\s+/g, " ").trim() || "General";
}

export default function SchemesPage() {
  const [schemes, setSchemes] = useState<SchemeListItem[]>([]);
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [selectedScheme, setSelectedScheme] = useState<Scheme | null>(null);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");

  useEffect(() => {
    getCategories()
      .then((data) => {
        const payload = data as { categories: string[] };
        setCategories(["All", ...payload.categories]);
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const data = (await getSchemes(
          page,
          12,
          activeCategory === "All" ? undefined : activeCategory,
          undefined,
          search || undefined,
        )) as { schemes: SchemeListItem[]; total_pages: number; total: number };
        setSchemes(data.schemes);
        setTotalPages(data.total_pages);
        setTotal(data.total);
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [page, activeCategory, search]);

  const openSchemeDetails = async (schemeId: string) => {
    setIsDetailsLoading(true);
    setDetailsError("");
    try {
      setSelectedScheme((await getSchemeDetails(schemeId)) as Scheme);
    } catch {
      setDetailsError("Could not load this scheme. Try again.");
    } finally {
      setIsDetailsLoading(false);
    }
  };

  return (
    <div className="shell py-10 md:py-14">
      <h1 className="max-w-2xl text-4xl font-semibold tracking-tight">Scheme catalog</h1>
      <p className="lede mt-3">
        {total ? `${total} curated central schemes.` : "Flagship central schemes with official apply links."}
      </p>

      <div className="mt-8">
        <input
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPage(1);
          }}
          placeholder="Search by name, benefit, or keyword"
          aria-label="Search schemes"
        />
      </div>

      <div className="mt-5 flex gap-2 overflow-x-auto pb-2">
        {categories.map((category) => (
          <button
            key={category}
            type="button"
            onClick={() => {
              setActiveCategory(category);
              setPage(1);
            }}
            className={`whitespace-nowrap rounded-full px-4 py-2 text-sm ${
              activeCategory === category
                ? "bg-[var(--forest)] text-[#f6f3ea]"
                : "border border-[var(--line)]"
            }`}
          >
            {formatCategoryLabel(category)}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="h-40 animate-pulse rounded-[1.5rem] bg-[var(--surface-2)]" />
          ))}
        </div>
      ) : schemes.length > 0 ? (
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {schemes.map((scheme) => (
            <button
              key={scheme.id}
              type="button"
              onClick={() => openSchemeDetails(scheme.id)}
              className="bezel text-left"
            >
              <div className="bezel-inner p-6">
                <p className="scheme-chip">{formatCategoryLabel(scheme.category)}</p>
                <h2 className="mt-4 text-xl font-semibold leading-snug">{scheme.name}</h2>
                <p className="mt-3 text-sm leading-6 text-[var(--muted)]">
                  {scheme.eligibility_summary || "Open for full details"}
                </p>
                {scheme.benefit_summary && (
                  <p className="mt-4 text-sm font-medium">{scheme.benefit_summary}</p>
                )}
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="bezel mt-10">
          <div className="bezel-inner p-10 text-center">
            <p className="font-semibold">No schemes matched that search</p>
            <p className="mt-2 text-sm text-[var(--muted)]">Try a scheme name or clear the category filter.</p>
          </div>
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-10 flex items-center justify-center gap-6 text-sm">
          <button type="button" disabled={page === 1} onClick={() => setPage((value) => value - 1)}>
            Previous
          </button>
          <span className="text-[var(--faint)]">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page === totalPages}
            onClick={() => setPage((value) => value + 1)}
          >
            Next
          </button>
        </div>
      )}

      {(isDetailsLoading || selectedScheme || detailsError) && (
        <div className="fixed inset-0 z-40 flex items-end justify-center bg-[rgba(17,22,19,0.45)] p-0 md:items-center md:p-6">
          <div className="max-h-[88dvh] w-full max-w-2xl overflow-y-auto rounded-t-[1.8rem] bg-[var(--surface)] p-6 md:rounded-[1.8rem]">
            <div className="flex items-start justify-between gap-4">
              <h2 className="text-xl font-semibold">Scheme details</h2>
              <button
                type="button"
                className="icon-btn"
                aria-label="Close details"
                onClick={() => {
                  setSelectedScheme(null);
                  setDetailsError("");
                  setIsDetailsLoading(false);
                }}
              >
                <X size={16} />
              </button>
            </div>
            {isDetailsLoading && <p className="mt-6 text-sm text-[var(--muted)]">Loading details...</p>}
            {detailsError && <p className="mt-6 text-sm text-red-700">{detailsError}</p>}
            {selectedScheme && !isDetailsLoading && (
              <div className="mt-5 space-y-5">
                <p className="scheme-chip">{formatCategoryLabel(selectedScheme.category)}</p>
                <h3 className="text-2xl font-semibold">{selectedScheme.name}</h3>
                <p className="text-sm leading-7 text-[var(--muted)]">{selectedScheme.description}</p>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded-2xl bg-[var(--paper)] p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--faint)]">
                      Benefit
                    </p>
                    <p className="mt-2 text-sm">
                      {selectedScheme.benefit_amount || selectedScheme.benefits || "See official page"}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-[var(--paper)] p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--faint)]">
                      Eligibility
                    </p>
                    <p className="mt-2 text-sm">{selectedScheme.eligibility_summary}</p>
                  </div>
                </div>
                <div className="rounded-2xl bg-[var(--paper)] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--faint)]">
                    How to apply
                  </p>
                  <p className="mt-2 text-sm leading-7">{selectedScheme.application_process}</p>
                </div>
                {selectedScheme.apply_url && (
                  <a
                    href={selectedScheme.apply_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-primary"
                  >
                    Open official page
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
