-- =========================================
-- Sahay AI - Supabase Database Schema
-- =========================================
-- Run this SQL in Supabase Dashboard > SQL Editor
-- to create all required tables.
-- =========================================

-- 1. Schemes table - stores all government scheme data
CREATE TABLE IF NOT EXISTS schemes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_hindi TEXT,
    category TEXT,
    scheme_type TEXT DEFAULT 'central',
    ministry TEXT,
    description TEXT,
    benefits TEXT,
    benefit_amount TEXT,
    eligibility_summary TEXT,
    eligibility_criteria JSONB DEFAULT '[]',
    documents_required JSONB DEFAULT '[]',
    application_process TEXT,
    apply_url TEXT,
    helpline TEXT,
    states TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster searches
CREATE INDEX IF NOT EXISTS idx_schemes_category ON schemes(category);
CREATE INDEX IF NOT EXISTS idx_schemes_type ON schemes(scheme_type);
CREATE INDEX IF NOT EXISTS idx_schemes_active ON schemes(is_active);
CREATE INDEX IF NOT EXISTS idx_schemes_name ON schemes USING gin(to_tsvector('english', name));

-- 2. Sessions table - persists conversation history
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    messages JSONB DEFAULT '[]',
    user_profile JSONB DEFAULT '{}',
    language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Feedback table - stores user feedback on responses
CREATE TABLE IF NOT EXISTS feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
    message_index INTEGER,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback(session_id);

-- 4. Analytics events table - tracks usage
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_type TEXT NOT NULL,
    session_id TEXT,
    language TEXT,
    intent TEXT,
    scheme_id TEXT,
    query_text TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics_events(created_at);

-- 5. Enable Row Level Security (optional - for production)
-- ALTER TABLE schemes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Public read access for schemes
-- CREATE POLICY "Public can read schemes" ON schemes
--     FOR SELECT USING (true);
