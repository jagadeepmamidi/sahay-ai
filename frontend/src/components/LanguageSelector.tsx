'use client';

interface Language {
    code: string;
    name: string;
    nativeName?: string;
    flag?: string;
}

const LANGUAGES: Language[] = [
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', flag: '🇮🇳' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', flag: '🇮🇳' },
    { code: 'en', name: 'English', nativeName: 'EN', flag: '🇬🇧' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', flag: '🇮🇳' },
    { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', flag: '🇮🇳' },
    { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', flag: '🇮🇳' },
    { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', flag: '🇮🇳' },
    { code: 'mr', name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳' },
    { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', flag: '🇮🇳' },
    { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', flag: '🇮🇳' },
    { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
];

interface LanguageSelectorProps {
    value: string;
    onChange: (language: string) => void;
    showNativeNames?: boolean;
    compact?: boolean;
}

export function LanguageSelector({ 
    value, 
    onChange, 
    showNativeNames = true,
    compact = false 
}: LanguageSelectorProps) {
    const currentLanguage = LANGUAGES.find(l => l.code === value) || LANGUAGES[2];

    if (compact) {
        return (
            <div className="relative inline-block">
                <select
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="
                        appearance-none bg-zinc-900 border border-zinc-800 text-zinc-100 
                        px-3 py-1.5 pr-8 rounded-lg text-sm cursor-pointer
                        focus:outline-none focus:border-emerald-500/50
                        transition-colors
                    "
                >
                    {LANGUAGES.map(lang => (
                        <option key={lang.code} value={lang.code}>
                            {lang.flag} {showNativeNames ? lang.nativeName : lang.name}
                        </option>
                    ))}
                </select>
                <svg 
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </div>
        );
    }

    return (
        <div className="flex flex-wrap gap-2">
            {LANGUAGES.slice(0, 3).map(lang => (
                <button
                    key={lang.code}
                    onClick={() => onChange(lang.code)}
                    className={`
                        px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                        ${value === lang.code 
                            ? 'bg-emerald-500 text-white' 
                            : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200'
                        }
                    `}
                >
                    <span className="mr-1">{lang.flag}</span>
                    {showNativeNames ? lang.nativeName : lang.name}
                </button>
            ))}
            
            <div className="relative">
                <select
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="
                        appearance-none bg-zinc-800 text-zinc-400 
                        pl-3 pr-8 py-1.5 rounded-lg text-sm
                        focus:outline-none focus:ring-2 focus:ring-emerald-500/50
                        cursor-pointer hover:bg-zinc-700
                        transition-colors
                    "
                >
                    <option value="" disabled>More...</option>
                    {LANGUAGES.slice(3).map(lang => (
                        <option key={lang.code} value={lang.code}>
                            {lang.flag} {lang.nativeName}
                        </option>
                    ))}
                </select>
                <svg 
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </div>
        </div>
    );
}

interface CurrentLanguageDisplayProps {
    language: string;
    showFlag?: boolean;
}

export function CurrentLanguageDisplay({ language, showFlag = true }: CurrentLanguageDisplayProps) {
    const lang = LANGUAGES.find(l => l.code === language) || LANGUAGES[2];
    
    return (
        <div className="flex items-center gap-2">
            {showFlag && <span className="text-lg">{lang.flag}</span>}
            <div>
                <span className="font-medium text-zinc-200">{lang.name}</span>
                {lang.nativeName !== lang.name && (
                    <span className="text-zinc-500 text-sm ml-1">({lang.nativeName})</span>
                )}
            </div>
        </div>
    );
}

export { LANGUAGES };
