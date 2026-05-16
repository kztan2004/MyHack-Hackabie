CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS mentors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    raw_bio TEXT NOT NULL,
    short_bio TEXT NOT NULL,
    embedding JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    raw_bio TEXT NOT NULL,
    short_bio TEXT NOT NULL,
    embedding JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    raw_bio TEXT NOT NULL,
    short_bio TEXT NOT NULL,
    embedding JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    raw_bio TEXT NOT NULL,
    short_bio TEXT NOT NULL,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    embedding JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS profile_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('mentor', 'company', 'participant', 'program')),
    entity_id UUID NOT NULL,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(entity_type, entity_id, skill_id)
);

CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_type TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('mentor', 'company', 'participant', 'program')),
    source_id UUID NOT NULL,
    source_name TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('mentor', 'company', 'participant', 'program')),
    target_id UUID NOT NULL,
    target_name TEXT NOT NULL,
    score NUMERIC(5,4) NOT NULL,
    explanation JSONB NOT NULL DEFAULT '[]'::jsonb,
    shared_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'recommended',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(match_type, source_id, target_id)
);

CREATE TABLE IF NOT EXISTS company_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(company_id, program_id)
);

CREATE TABLE IF NOT EXISTS participant_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(participant_id, program_id)
);

CREATE INDEX IF NOT EXISTS idx_profile_skills_entity ON profile_skills(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_matches_source ON matches(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_matches_target ON matches(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_matches_type ON matches(match_type);
CREATE INDEX IF NOT EXISTS idx_company_programs_company ON company_programs(company_id);
CREATE INDEX IF NOT EXISTS idx_participant_programs_participant ON participant_programs(participant_id);
