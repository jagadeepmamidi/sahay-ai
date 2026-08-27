'use client';

const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ' },
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
  compact = false,
}: LanguageSelectorProps) {
  return (
    <select
      aria-label="Response language"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className={compact ? "min-h-10 w-auto" : undefined}
    >
      {LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {showNativeNames ? `${lang.name} (${lang.nativeName})` : lang.name}
        </option>
      ))}
    </select>
  );
}

export { LANGUAGES };
