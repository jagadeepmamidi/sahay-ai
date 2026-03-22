'use client';

import { useState, useEffect } from 'react';
import { checkEligibility, getStates } from '@/lib/api';
import { EligibleScheme } from '@/types';

export default function EligibilityPage() {
    const [formData, setFormData] = useState({
        age: '',
        income: '',
        state: '',
        occupation: '',
    });
    const [indianStates, setIndianStates] = useState<string[]>([]);
    const [results, setResults] = useState<EligibleScheme[] | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchStates = async () => {
            try {
                const data = await getStates() as { states: string[] };
                setIndianStates(data.states);
            } catch (err) {
                console.error('Failed to fetch states:', err);
                setIndianStates(['Andhra Pradesh', 'Telangana', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Delhi', 'Uttar Pradesh', 'Gujarat']);
            }
        };
        fetchStates();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const data = await checkEligibility({
                age: formData.age ? parseInt(formData.age) : undefined,
                income: formData.income ? parseFloat(formData.income) : undefined,
                state: formData.state || undefined,
                occupation: formData.occupation || undefined
            }) as { schemes: EligibleScheme[] };
            
            setResults(data.schemes);
        } catch (err) {
            console.error('Eligibility check failed:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto px-6 py-12">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-semibold text-zinc-100 mb-2">Check Eligibility</h1>
                <p className="text-zinc-500 text-sm">Enter your details to find matching schemes</p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-zinc-400 text-sm mb-2">Age</label>
                        <input
                            type="number"
                            value={formData.age}
                            onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                            className="w-full px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-emerald-500/50 text-sm transition-colors"
                            placeholder="25"
                        />
                    </div>

                    <div>
                        <label className="block text-zinc-400 text-sm mb-2">Annual Income (₹)</label>
                        <input
                            type="number"
                            value={formData.income}
                            onChange={(e) => setFormData({ ...formData, income: e.target.value })}
                            className="w-full px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-emerald-500/50 text-sm transition-colors"
                            placeholder="300000"
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-zinc-400 text-sm mb-2">State</label>
                    <select
                        value={formData.state}
                        onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                        className="w-full px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-100 focus:outline-none focus:border-emerald-500/50 text-sm transition-colors"
                    >
                        <option value="" className="bg-zinc-900 text-zinc-500">Select state</option>
                        {indianStates.map(state => (
                            <option key={state} value={state} className="bg-zinc-900 text-zinc-100">{state}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-zinc-400 text-sm mb-2">Occupation</label>
                    <select
                        value={formData.occupation}
                        onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                        className="w-full px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-100 focus:outline-none focus:border-emerald-500/50 text-sm transition-colors"
                    >
                        <option value="" className="bg-zinc-900 text-zinc-500">Select occupation</option>
                        <option value="farmer" className="bg-zinc-900 text-zinc-100">Farmer</option>
                        <option value="student" className="bg-zinc-900 text-zinc-100">Student</option>
                        <option value="employee" className="bg-zinc-900 text-zinc-100">Employee</option>
                        <option value="self-employed" className="bg-zinc-900 text-zinc-100">Self Employed</option>
                        <option value="unemployed" className="bg-zinc-900 text-zinc-100">Unemployed</option>
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-400 transition-colors disabled:opacity-50 text-sm"
                >
                    {loading ? (
                        <span className="flex items-center justify-center gap-2">
                            Analyzing
                            <span className="flex gap-1">
                                <span className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <span className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <span className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </span>
                        </span>
                    ) : (
                        'Check Eligibility'
                    )}
                </button>
            </form>

            {/* Results */}
            {results && (
                <div className="mt-10 space-y-4">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-medium text-zinc-200">
                            {results.length} Matching Scheme{results.length !== 1 ? 's' : ''}
                        </h2>
                        <button 
                            onClick={() => setResults(null)} 
                            className="text-zinc-500 text-sm hover:text-zinc-300 transition-colors"
                        >
                            Clear
                        </button>
                    </div>
                    
                    {results.length > 0 ? (
                        <div className="space-y-4">
                            {results.map((res) => (
                                <div key={res.scheme.id} className="glass-card-accent p-6">
                                    <div className="flex justify-between items-start mb-3">
                                        <h3 className="text-zinc-100 font-medium text-lg">
                                            {res.scheme.name}
                                        </h3>
                                        <span className="badge-match">
                                            {Math.round(res.match_score * 100)}% Match
                                        </span>
                                    </div>
                                    <p className="text-zinc-400 text-sm mb-4">{res.scheme.category}</p>
                                    
                                    <div className="flex flex-wrap gap-2">
                                        {res.matched_criteria.map((c, i) => (
                                            <span key={i} className="text-xs text-zinc-400 bg-emerald-500/10 py-1.5 px-3 rounded-full border border-emerald-500/20">
                                                ✓ {c}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12 glass-card">
                            <p className="text-zinc-400 text-lg mb-2">No matches found</p>
                            <p className="text-zinc-500 text-sm">Try adjusting your parameters.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
