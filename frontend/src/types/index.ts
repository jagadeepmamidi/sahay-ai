// API types for Sahay AI

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
    language?: string;
}

export interface SchemeCard {
    id: string;
    name: string;
    category: string;
    benefit_summary: string;
    eligibility_summary: string;
    apply_url?: string;
}

export interface ChatRequest {
    message: string;
    session_id?: string;
    language?: string;
    user_profile?: UserProfile;
}

export interface ChatResponse {
    success: boolean;
    message: string;
    session_id: string;
    detected_language: string;
    response_language: string;
    intent?: string;
    confidence?: number;
    schemes?: SchemeCard[];
    suggested_questions?: string[];
    timestamp: string;
}

export interface UserProfile {
    age?: number;
    gender?: string;
    state?: string;
    income?: number;
    occupation?: string;
    caste_category?: string;
    is_bpl?: boolean;
    has_land?: boolean;
    land_size_acres?: number;
}

export interface Scheme {
    id: string;
    name: string;
    name_hindi?: string;
    category: string;
    scheme_type: 'central' | 'state' | 'both';
    ministry: string;
    description: string;
    benefits: string;
    benefit_amount?: string;
    eligibility_summary: string;
    documents_required: SchemeDocument[];
    application_process: string;
    apply_url?: string;
    helpline?: string;
    last_updated: string;
    is_active: boolean;
}

export interface SchemeDocument {
    name: string;
    description: string;
    is_mandatory: boolean;
}

export interface SchemeListItem {
    id: string;
    name: string;
    name_hindi?: string;
    category: string;
    scheme_type: 'central' | 'state' | 'both';
    benefit_summary: string;
    eligibility_summary: string;
    is_active: boolean;
}

export interface SchemeListResponse {
    success: boolean;
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    schemes: SchemeListItem[];
}

export interface EligibleScheme {
    scheme: SchemeListItem;
    match_score: number;
    matched_criteria: string[];
    missing_criteria: string[];
}

export interface EligibilityCheckResponse {
    success: boolean;
    user_profile: UserProfile;
    total_eligible: number;
    schemes: EligibleScheme[];
}

export interface Language {
    code: string;
    name: string;
}

export const SUPPORTED_LANGUAGES: Language[] = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi (हिंदी)' },
    { code: 'te', name: 'Telugu (తెలుగు)' },
    { code: 'ta', name: 'Tamil (தமிழ்)' },
    { code: 'bn', name: 'Bengali (বাংলা)' },
    { code: 'mr', name: 'Marathi (मराठी)' },
    { code: 'gu', name: 'Gujarati (ગુજરાતી)' },
    { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
    { code: 'ml', name: 'Malayalam (മലയാളം)' },
    { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)' },
    { code: 'or', name: 'Odia (ଓଡ଼ିଆ)' },
];
