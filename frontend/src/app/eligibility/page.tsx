"use client";

import { useEffect, useState } from "react";
import { checkEligibility, getStates } from "@/lib/api";
import { EligibleScheme } from "@/types";

export default function EligibilityPage() {
  const [formData, setFormData] = useState({
    age: "",
    income: "",
    state: "",
    occupation: "",
    gender: "",
    is_bpl: false,
    has_land: false,
  });
  const [indianStates, setIndianStates] = useState<string[]>([]);
  const [results, setResults] = useState<EligibleScheme[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getStates()
      .then((data) => setIndianStates((data as { states: string[] }).states))
      .catch(() => {
        setIndianStates(["Andhra Pradesh", "Maharashtra", "Tamil Nadu", "Uttar Pradesh", "Delhi"]);
      });
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = (await checkEligibility({
        age: formData.age ? parseInt(formData.age, 10) : undefined,
        income: formData.income ? parseFloat(formData.income) : undefined,
        state: formData.state || undefined,
        occupation: formData.occupation || undefined,
        gender: formData.gender || undefined,
        is_bpl: formData.is_bpl,
        has_land: formData.has_land,
      })) as { schemes: EligibleScheme[] };
      setResults(data.schemes);
    } catch {
      setError("Could not run the eligibility check. Confirm the API is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="shell py-10 md:py-14">
      <h1 className="max-w-2xl text-4xl font-semibold tracking-tight">Likely eligibility</h1>
      <p className="lede mt-3">
        This is a first-pass match against scheme rules. The ministry portal is still the source of truth.
      </p>

      <form onSubmit={handleSubmit} className="bezel mt-8 max-w-2xl">
        <div className="bezel-inner space-y-5 p-6 md:p-8">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm">
              Age
              <input
                className="mt-2"
                type="number"
                min={1}
                max={120}
                value={formData.age}
                onChange={(event) => setFormData({ ...formData, age: event.target.value })}
                placeholder="42"
              />
            </label>
            <label className="block text-sm">
              Annual income (Rs.)
              <input
                className="mt-2"
                type="number"
                min={0}
                value={formData.income}
                onChange={(event) => setFormData({ ...formData, income: event.target.value })}
                placeholder="180000"
              />
            </label>
          </div>
          <label className="block text-sm">
            State
            <select
              className="mt-2"
              value={formData.state}
              onChange={(event) => setFormData({ ...formData, state: event.target.value })}
            >
              <option value="">Select state</option>
              {indianStates.map((state) => (
                <option key={state} value={state}>
                  {state}
                </option>
              ))}
            </select>
          </label>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm">
              Occupation
              <select
                className="mt-2"
                value={formData.occupation}
                onChange={(event) => setFormData({ ...formData, occupation: event.target.value })}
              >
                <option value="">Select occupation</option>
                <option value="farmer">Farmer</option>
                <option value="student">Student</option>
                <option value="employee">Salaried</option>
                <option value="self-employed">Self employed</option>
                <option value="unemployed">Unemployed</option>
              </select>
            </label>
            <label className="block text-sm">
              Gender
              <select
                className="mt-2"
                value={formData.gender}
                onChange={(event) => setFormData({ ...formData, gender: event.target.value })}
              >
                <option value="">Prefer not to say</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
              </select>
            </label>
          </div>
          <div className="flex flex-wrap gap-6 text-sm">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.is_bpl}
                onChange={(event) => setFormData({ ...formData, is_bpl: event.target.checked })}
              />
              BPL / SECC household
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.has_land}
                onChange={(event) => setFormData({ ...formData, has_land: event.target.checked })}
              />
              Own cultivable land
            </label>
          </div>
          {error && <p className="text-sm text-red-700">{error}</p>}
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? "Matching records" : "Check matches"}
          </button>
        </div>
      </form>

      {results && (
        <div className="mt-10 max-w-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">{results.length} ranked matches</h2>
            <button type="button" onClick={() => setResults(null)} className="text-sm text-[var(--muted)]">
              Clear
            </button>
          </div>
          {results.length === 0 && (
            <div className="bezel">
              <div className="bezel-inner p-8 text-center text-[var(--muted)]">
                No strong matches. Add occupation or income and try again.
              </div>
            </div>
          )}
          {results.map((item) => (
            <article key={item.scheme.id} className="bezel">
              <div className="bezel-inner p-5">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-semibold">{item.scheme.name}</h3>
                  <span className="scheme-chip">{Math.round(item.match_score * 100)}% match</span>
                </div>
                <p className="mt-2 text-sm text-[var(--muted)]">{item.scheme.category}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.matched_criteria.map((criterion) => (
                    <span key={criterion} className="rounded-full bg-[var(--paper)] px-3 py-1 text-xs">
                      {criterion}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
