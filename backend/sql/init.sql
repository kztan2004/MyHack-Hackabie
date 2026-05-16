-- ─────────────────────────────────────────────────────────────────────────────
-- EcosystemGraph AI — Database Schema + Seed Data
-- ─────────────────────────────────────────────────────────────────────────────

-- Startups table
CREATE TABLE IF NOT EXISTS startups (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    industry            VARCHAR(100),
    stage               VARCHAR(50) CHECK (stage IN ('idea', 'pre-seed', 'seed', 'growth', 'scale')),
    description         TEXT,
    tags                TEXT[],
    clean_description   TEXT,
    ai_confidence       NUMERIC(4, 3) DEFAULT 0,
    enriched_at         TIMESTAMP WITH TIME ZONE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mentors table
CREATE TABLE IF NOT EXISTS mentors (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    expertise_tags      TEXT[],
    experience_years    INTEGER DEFAULT 0,
    bio                 TEXT,
    clean_bio           TEXT,
    enriched_at         TIMESTAMP WITH TIME ZONE,
    rating              NUMERIC(3, 2) DEFAULT 0.00,
    total_feedback      INTEGER DEFAULT 0,
    available           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Programs table (stub for future use)
CREATE TABLE IF NOT EXISTS programs (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    focus_areas         TEXT[],
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Match logs table
CREATE TABLE IF NOT EXISTS match_logs (
    id                  SERIAL PRIMARY KEY,
    startup_id          INTEGER REFERENCES startups(id) ON DELETE CASCADE,
    mentor_id           INTEGER REFERENCES mentors(id) ON DELETE CASCADE,
    score               NUMERIC(5, 4) NOT NULL,
    reason              TEXT,
    status              VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id                  SERIAL PRIMARY KEY,
    startup_id          INTEGER REFERENCES startups(id) ON DELETE CASCADE,
    mentor_id           INTEGER REFERENCES mentors(id) ON DELETE CASCADE,
    action              VARCHAR(20) NOT NULL CHECK (action IN ('accepted', 'rejected')),
    comments            TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─── Seed Data: Mentors ──────────────────────────────────────────────────────
INSERT INTO mentors (name, expertise_tags, experience_years, bio, available) VALUES
  ('Sarah Chen',
   ARRAY['Fintech', 'AI', 'Credit Scoring', 'Machine Learning', 'Lending'],
   12,
   'Serial entrepreneur with 12 years in fintech. Founded 2 lending platforms, exited 1. Deep expertise in AI-driven credit scoring and regulatory compliance.',
   TRUE),

  ('Marcus Rivera',
   ARRAY['SaaS', 'B2B', 'Product Management', 'Growth', 'Enterprise Sales'],
   9,
   'Former VP Product at a $500M SaaS unicorn. Expert in B2B product strategy, enterprise sales cycles, and scaling from $1M to $50M ARR.',
   TRUE),

  ('Priya Nair',
   ARRAY['Healthtech', 'AI', 'Medical Devices', 'FDA Compliance', 'Clinical Trials'],
   15,
   'Physician-turned-entrepreneur. Led 3 FDA-cleared medical AI products. Advisor to 20+ healthtech startups on regulatory pathways and clinical validation.',
   TRUE),

  ('James O''Brien',
   ARRAY['Cybersecurity', 'Cloud', 'Zero Trust', 'Enterprise', 'CISO'],
   11,
   'Former CISO at Fortune 500 companies. Advisor to early-stage cybersecurity startups on go-to-market strategy and enterprise sales.',
   TRUE),

  ('Aiko Tanaka',
   ARRAY['EdTech', 'Consumer Apps', 'UX', 'Gamification', 'Mobile'],
   8,
   'Built and sold an EdTech platform serving 2M students. Expert in engagement design, gamification, and mobile-first consumer apps.',
   TRUE),

  ('David Osei',
   ARRAY['CleanTech', 'Impact', 'ESG', 'Energy', 'Carbon Markets', 'Hardware'],
   10,
   'Climate tech investor and operator. Led hardware and energy projects across Southeast Asia and Africa. Deep networks in carbon markets and ESG investment.',
   TRUE),

  ('Rachel Kim',
   ARRAY['AI', 'NLP', 'LLM', 'Developer Tools', 'API', 'Open Source'],
   7,
   'Principal engineer at a top AI lab. Built LLM infrastructure serving 50M+ daily requests. Passionate about developer tools and open-source AI.',
   TRUE),

  ('Carlos Mendez',
   ARRAY['Logistics', 'Supply Chain', 'Marketplace', 'Operations', 'Latin America'],
   13,
   'Co-founded a logistics marketplace that scaled to 15 countries. Expert in supply chain optimization, marketplace dynamics, and emerging market expansion.',
   TRUE)
ON CONFLICT DO NOTHING;

-- ─── Seed Data: Startups ─────────────────────────────────────────────────────
INSERT INTO startups (name, industry, stage, description, tags) VALUES
  ('LendAI',
   'Fintech',
   'seed',
   'We are building an AI-powered lending platform that uses alternative data sources for credit scoring, targeting underbanked populations in Southeast Asia.',
   ARRAY['AI', 'Lending', 'Credit Scoring', 'Fintech', 'Southeast Asia']),

  ('HealthBot Pro',
   'Healthtech',
   'pre-seed',
   'A conversational AI assistant for chronic disease management that integrates with EHR systems and provides personalized care recommendations.',
   ARRAY['AI', 'Health', 'NLP', 'EHR', 'Chronic Disease']),

  ('SecureStack',
   'Cybersecurity',
   'growth',
   'Zero-trust security platform for cloud-native enterprises. We automate security policy enforcement across multi-cloud environments.',
   ARRAY['Zero Trust', 'Cloud', 'Security', 'Enterprise', 'Automation']),

  ('EduQuest',
   'EdTech',
   'seed',
   'Gamified learning platform for K-12 STEM education. Uses adaptive AI to personalize curriculum and reward learning milestones.',
   ARRAY['EdTech', 'Gamification', 'AI', 'K-12', 'STEM']),

  ('GreenTrace',
   'CleanTech',
   'pre-seed',
   'Carbon footprint tracking and reporting SaaS for SMEs. Automates ESG reporting and connects businesses to verified carbon offset markets.',
   ARRAY['CleanTech', 'ESG', 'Carbon', 'SaaS', 'Sustainability'])
ON CONFLICT DO NOTHING;
