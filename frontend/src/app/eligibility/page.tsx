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
                <h1 className="text-3xl font-semibold text-slate-950 mb-2">Check Eligibility</h1>
                <p className="text-slate-500 text-sm">Enter your details to find matching schemes</p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-slate-600 text-sm mb-2">Age</label>
                        <input
                            type="number"
                            value={formData.age}
                            onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                            className="w-full px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 text-sm transition-colors"
                            placeholder="25"
                        />
                    </div>

                    <div>
                        <label className="block text-slate-600 text-sm mb-2">Annual Income (₹)</label>
                        <input
                            type="number"
                            value={formData.income}
                            onChange={(e) => setFormData({ ...formData, income: e.target.value })}
                            className="w-full px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 text-sm transition-colors"
                            placeholder="300000"
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-slate-600 text-sm mb-2">State</label>
                    <select
                        value={formData.state}
                        onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                        className="w-full px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 text-sm transition-colors"
                    >
                        <option value="" className="text-slate-400">Select state</option>
                        {indianStates.map(state => (
                            <option key={state} value={state}>{state}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-slate-600 text-sm mb-2">Occupation</label>
                    <select
                        value={formData.occupation}
                        onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                        className="w-full px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 text-sm transition-colors"
                    >
                        <option value="" className="text-slate-400">Select occupation</option>
                        <option value="farmer">Farmer</option>
                        <option value="student">Student</option>
                        <option value="employee">Employee</option>
                        <option value="self-employed">Self Employed</option>
                        <option value="unemployed">Unemployed</option>
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-500 transition-colors disabled:opacity-50 text-sm"
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
                        <h2 className="text-lg font-medium text-slate-800">
                            {results.length} Matching Scheme{results.length !== 1 ? 's' : ''}
                        </h2>
                        <button 
                            onClick={() => setResults(null)} 
                            className="text-slate-400 text-sm hover:text-slate-600 transition-colors"
                        >
                            Clear
                        </button>
                    </div>
                    
                    {results.length > 0 ? (
                        <div className="space-y-4">
                            {results.map((res) => (
                                <div key={res.scheme.id} className="glass-card p-6 hover:border-emerald-200 transition-colors">
                                    <div className="flex justify-between items-start mb-3">
                                        <h3 className="text-slate-800 font-medium text-lg">
                                            {res.scheme.name}
                                        </h3>
                                        <span className="text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
                                            {Math.round(res.match_score * 100)}% Match
                                        </span>
                                    </div>
                                    <p className="text-slate-500 text-sm mb-4">{res.scheme.category}</p>
                                    
                                    <div className="flex flex-wrap gap-2">
                                        {res.matched_criteria.map((c, i) => (
                                            <span key={i} className="text-xs text-emerald-700 bg-emerald-50 py-1.5 px-3 rounded-full border border-emerald-100">
                                                ✓ {c}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12 glass-card">
                            <p className="text-slate-600 text-lg mb-2">No matches found</p>
                            <p className="text-slate-400 text-sm">Try adjusting your parameters.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
