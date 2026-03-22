'use client';

import { useState, useEffect } from 'react';
import { getSchemes, getCategories } from '@/lib/api';
import { SchemeListItem } from '@/types';

export default function SchemesPage() {
    const [schemes, setSchemes] = useState<SchemeListItem[]>([]);
    const [categories, setCategories] = useState<string[]>(['All']);
    const [activeCategory, setActiveCategory] = useState('All');
    const [search, setSearch] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const data = await getCategories() as { categories: string[] };
                setCategories(['All', ...data.categories]);
            } catch (err) {
                console.error('Failed to fetch categories:', err);
            }
        };
        fetchCategories();
    }, []);

    useEffect(() => {
        const fetchSchemes = async () => {
            setIsLoading(true);
            try {
                const data = await getSchemes(
                    page,
                    10,
                    activeCategory === 'All' ? undefined : activeCategory,
                    undefined,
                    search || undefined
                ) as { schemes: SchemeListItem[], total_pages: number };
                setSchemes(data.schemes);
                setTotalPages(data.total_pages);
            } catch (err) {
                console.error('Failed to fetch schemes:', err);
            } finally {
                setIsLoading(false);
            }
        };

        const timer = setTimeout(() => {
            fetchSchemes();
        }, 300);

        return () => clearTimeout(timer);
    }, [page, activeCategory, search]);

    return (
        <div className="max-w-5xl mx-auto px-6 py-12">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-semibold text-slate-950 mb-2">Government Schemes</h1>
                <p className="text-slate-500 text-sm">Browse official schemes across categories</p>
            </div>

            {/* Search */}
            <div className="relative mb-6">
                <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                    type="text"
                    placeholder="Search schemes..."
                    value={search}
                    onChange={(e) => {
                        setSearch(e.target.value);
                        setPage(1);
                    }}
                    className="w-full pl-12 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 text-sm transition-colors"
                />
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-2 mb-8">
                {categories.map((cat) => (
                    <button
                        key={cat}
                        onClick={() => {
                            setActiveCategory(cat);
                            setPage(1);
                        }}
                        className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                            activeCategory === cat
                                ? 'bg-emerald-600 text-white'
                                : 'bg-slate-100 text-slate-600 border border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                        }`}
                    >
                        {cat}
                    </button>
                ))}
            </div>

            {/* Schemes Grid */}
            {isLoading ? (
                <div className="grid md:grid-cols-2 gap-4">
                    {[1, 2, 3, 4].map(i => (
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
                            <div key={scheme.id} className="glass-card p-6 group hover:border-emerald-200 transition-colors">
                                <div className="flex justify-between items-start mb-3">
                                    <h3 className="text-slate-800 font-medium text-lg group-hover:text-emerald-700 transition-colors">
                                        {scheme.name}
                                    </h3>
                                    <span className="text-xs uppercase font-medium text-emerald-700 px-2 py-1 bg-emerald-50 border border-emerald-200 rounded">
                                        {scheme.category}
                                    </span>
                                </div>
                                <p className="text-slate-500 text-sm line-clamp-2 leading-relaxed">
                                    {scheme.eligibility_summary || "Click for details"}
                                </p>
                                {scheme.benefit_summary && (
                                    <p className="text-emerald-600 text-sm mt-3">
                                        Benefit: {scheme.benefit_summary}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                    
                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex justify-center items-center gap-6 mt-12">
                            <button 
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="text-slate-500 hover:text-emerald-600 disabled:opacity-30 disabled:hover:text-slate-500 transition-colors text-sm"
                            >
                                ← Previous
                            </button>
                            <span className="text-slate-400 text-sm">
                                Page {page} of {totalPages}
                            </span>
                            <button 
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
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
                    <p className="text-slate-400 text-sm">Try adjusting your search or category filters.</p>
                </div>
            )}
        </div>
    );
}
