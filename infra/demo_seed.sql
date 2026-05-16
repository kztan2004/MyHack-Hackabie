INSERT INTO companies (id, name, raw_bio, short_bio, embedding) VALUES
  (
    '11111111-1111-1111-1111-111111111111',
    'FinAI Labs',
    'FinAI Labs is a startup building AI and data analytics tools for fintech risk, banking infrastructure, and regulatory compliance.',
    'FinAI Labs builds AI fintech risk tools for banking infrastructure and regulatory compliance.',
    '[]'::jsonb
  ),
  (
    '11111111-1111-1111-1111-111111111112',
    'CloudCart Systems',
    'CloudCart Systems is a SaaS company using cloud, cybersecurity, product management, and go-to-market operations to help retailers modernize commerce.',
    'CloudCart Systems helps retailers modernize commerce with SaaS, cloud, cybersecurity, and go-to-market operations.',
    '[]'::jsonb
  ),
  (
    '11111111-1111-1111-1111-111111111113',
    'GreenForge Robotics',
    'GreenForge Robotics is a climate tech and manufacturing startup using robotics, supply chain analytics, and operations systems for efficient factories.',
    'GreenForge Robotics applies climate tech, robotics, supply chain analytics, and operations to manufacturing.',
    '[]'::jsonb
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO mentors (id, name, raw_bio, short_bio, embedding) VALUES
  (
    '22222222-2222-2222-2222-222222222221',
    'Asha Raman',
    'AI and fintech mentor with product management, regulatory compliance, fundraising, and banking infrastructure experience.',
    'AI and fintech mentor with product management, compliance, fundraising, and banking infrastructure experience.',
    '[]'::jsonb
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    'Marcus Lee',
    'SaaS go-to-market mentor focused on cloud platforms, cybersecurity, sales, marketing, and product management.',
    'SaaS go-to-market mentor focused on cloud, cybersecurity, sales, marketing, and product management.',
    '[]'::jsonb
  ),
  (
    '22222222-2222-2222-2222-222222222223',
    'Priya Nair',
    'Operations mentor with manufacturing, robotics, supply chain, climate tech, and data analytics expertise.',
    'Operations mentor with manufacturing, robotics, supply chain, climate tech, and analytics expertise.',
    '[]'::jsonb
  ),
  (
    '22222222-2222-2222-2222-222222222224',
    'Daniel Koh',
    'Venture capital and fundraising mentor for early stage startups working on AI, SaaS, strategy, and go-to-market.',
    'Venture capital and fundraising mentor for AI and SaaS startups scaling strategy and go-to-market.',
    '[]'::jsonb
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO programs (id, name, raw_bio, short_bio, embedding) VALUES
  (
    '33333333-3333-3333-3333-333333333331',
    'AI Growth Accelerator',
    'Program focused on AI, machine learning, data analytics, product management, and fundraising for startup growth.',
    'Program focused on AI, analytics, product management, and fundraising for startup growth.',
    '[]'::jsonb
  ),
  (
    '33333333-3333-3333-3333-333333333332',
    'Fintech Compliance Lab',
    'Program focused on fintech, banking infrastructure, payments, cybersecurity, and regulatory compliance.',
    'Program focused on fintech, banking infrastructure, payments, cybersecurity, and regulatory compliance.',
    '[]'::jsonb
  ),
  (
    '33333333-3333-3333-3333-333333333333',
    'Advanced Manufacturing Sprint',
    'Program focused on manufacturing, robotics, supply chain, operations, climate tech, and data analytics.',
    'Program focused on manufacturing, robotics, supply chain, operations, climate tech, and analytics.',
    '[]'::jsonb
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO participants (id, name, raw_bio, short_bio, company_id, embedding) VALUES
  (
    '44444444-4444-4444-4444-444444444441',
    'Nadia Lim',
    'Product lead working on fintech data analytics, AI, and regulatory compliance workflows.',
    'Product lead working on fintech analytics, AI, and regulatory compliance workflows.',
    '11111111-1111-1111-1111-111111111111',
    '[]'::jsonb
  ),
  (
    '44444444-4444-4444-4444-444444444442',
    'Owen Tan',
    'Cloud engineer focused on SaaS infrastructure, cybersecurity, and operations automation.',
    'Cloud engineer focused on SaaS infrastructure, cybersecurity, and operations automation.',
    '11111111-1111-1111-1111-111111111112',
    '[]'::jsonb
  ),
  (
    '44444444-4444-4444-4444-444444444443',
    'Mei Chen',
    'Operations analyst using supply chain data analytics, manufacturing systems, and robotics workflows.',
    'Operations analyst using supply chain analytics, manufacturing systems, and robotics workflows.',
    '11111111-1111-1111-1111-111111111113',
    '[]'::jsonb
  ),
  (
    '44444444-4444-4444-4444-444444444444',
    'Farid Aziz',
    'Startup associate learning go-to-market, sales, marketing, strategy, and fundraising.',
    'Startup associate learning go-to-market, sales, marketing, strategy, and fundraising.',
    '11111111-1111-1111-1111-111111111112',
    '[]'::jsonb
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO skills (id, name, normalized_name) VALUES
  ('55555555-5555-5555-5555-555555555501', 'AI', 'ai'),
  ('55555555-5555-5555-5555-555555555502', 'Machine Learning', 'machine learning'),
  ('55555555-5555-5555-5555-555555555503', 'Data Analytics', 'data analytics'),
  ('55555555-5555-5555-5555-555555555504', 'Fintech', 'fintech'),
  ('55555555-5555-5555-5555-555555555505', 'Banking Infrastructure', 'banking infrastructure'),
  ('55555555-5555-5555-5555-555555555506', 'Regulatory Compliance', 'regulatory compliance'),
  ('55555555-5555-5555-5555-555555555507', 'Product Management', 'product management'),
  ('55555555-5555-5555-5555-555555555508', 'Fundraising', 'fundraising'),
  ('55555555-5555-5555-5555-555555555509', 'Cloud', 'cloud'),
  ('55555555-5555-5555-5555-555555555510', 'Cybersecurity', 'cybersecurity'),
  ('55555555-5555-5555-5555-555555555511', 'SaaS', 'saas'),
  ('55555555-5555-5555-5555-555555555512', 'Go-To-Market', 'go to market'),
  ('55555555-5555-5555-5555-555555555513', 'Sales', 'sales'),
  ('55555555-5555-5555-5555-555555555514', 'Marketing', 'marketing'),
  ('55555555-5555-5555-5555-555555555515', 'Manufacturing', 'manufacturing'),
  ('55555555-5555-5555-5555-555555555516', 'Robotics', 'robotics'),
  ('55555555-5555-5555-5555-555555555517', 'Supply Chain', 'supply chain'),
  ('55555555-5555-5555-5555-555555555518', 'Operations', 'operations'),
  ('55555555-5555-5555-5555-555555555519', 'Climate Tech', 'climate tech'),
  ('55555555-5555-5555-5555-555555555520', 'Strategy', 'strategy'),
  ('55555555-5555-5555-5555-555555555521', 'Payments', 'payments')
ON CONFLICT (normalized_name) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO profile_skills (entity_type, entity_id, skill_id) VALUES
  ('company', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555501'),
  ('company', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555503'),
  ('company', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555504'),
  ('company', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555505'),
  ('company', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555506'),
  ('company', '11111111-1111-1111-1111-111111111112', '55555555-5555-5555-5555-555555555507'),
  ('company', '11111111-1111-1111-1111-111111111112', '55555555-5555-5555-5555-555555555509'),
  ('company', '11111111-1111-1111-1111-111111111112', '55555555-5555-5555-5555-555555555510'),
  ('company', '11111111-1111-1111-1111-111111111112', '55555555-5555-5555-5555-555555555511'),
  ('company', '11111111-1111-1111-1111-111111111112', '55555555-5555-5555-5555-555555555512'),
  ('company', '11111111-1111-1111-1111-111111111113', '55555555-5555-5555-5555-555555555503'),
  ('company', '11111111-1111-1111-1111-111111111113', '55555555-5555-5555-5555-555555555515'),
  ('company', '11111111-1111-1111-1111-111111111113', '55555555-5555-5555-5555-555555555516'),
  ('company', '11111111-1111-1111-1111-111111111113', '55555555-5555-5555-5555-555555555517'),
  ('company', '11111111-1111-1111-1111-111111111113', '55555555-5555-5555-5555-555555555518'),
  ('mentor', '22222222-2222-2222-2222-222222222221', '55555555-5555-5555-5555-555555555501'),
  ('mentor', '22222222-2222-2222-2222-222222222221', '55555555-5555-5555-5555-555555555504'),
  ('mentor', '22222222-2222-2222-2222-222222222221', '55555555-5555-5555-5555-555555555506'),
  ('mentor', '22222222-2222-2222-2222-222222222221', '55555555-5555-5555-5555-555555555507'),
  ('mentor', '22222222-2222-2222-2222-222222222221', '55555555-5555-5555-5555-555555555508'),
  ('mentor', '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555507'),
  ('mentor', '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555509'),
  ('mentor', '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555510'),
  ('mentor', '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555511'),
  ('mentor', '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555512'),
  ('mentor', '22222222-2222-2222-2222-222222222223', '55555555-5555-5555-5555-555555555503'),
  ('mentor', '22222222-2222-2222-2222-222222222223', '55555555-5555-5555-5555-555555555515'),
  ('mentor', '22222222-2222-2222-2222-222222222223', '55555555-5555-5555-5555-555555555516'),
  ('mentor', '22222222-2222-2222-2222-222222222223', '55555555-5555-5555-5555-555555555517'),
  ('mentor', '22222222-2222-2222-2222-222222222223', '55555555-5555-5555-5555-555555555518'),
  ('mentor', '22222222-2222-2222-2222-222222222224', '55555555-5555-5555-5555-555555555501'),
  ('mentor', '22222222-2222-2222-2222-222222222224', '55555555-5555-5555-5555-555555555508'),
  ('mentor', '22222222-2222-2222-2222-222222222224', '55555555-5555-5555-5555-555555555511'),
  ('mentor', '22222222-2222-2222-2222-222222222224', '55555555-5555-5555-5555-555555555512'),
  ('mentor', '22222222-2222-2222-2222-222222222224', '55555555-5555-5555-5555-555555555520'),
  ('program', '33333333-3333-3333-3333-333333333331', '55555555-5555-5555-5555-555555555501'),
  ('program', '33333333-3333-3333-3333-333333333331', '55555555-5555-5555-5555-555555555502'),
  ('program', '33333333-3333-3333-3333-333333333331', '55555555-5555-5555-5555-555555555503'),
  ('program', '33333333-3333-3333-3333-333333333331', '55555555-5555-5555-5555-555555555507'),
  ('program', '33333333-3333-3333-3333-333333333331', '55555555-5555-5555-5555-555555555508'),
  ('program', '33333333-3333-3333-3333-333333333332', '55555555-5555-5555-5555-555555555504'),
  ('program', '33333333-3333-3333-3333-333333333332', '55555555-5555-5555-5555-555555555505'),
  ('program', '33333333-3333-3333-3333-333333333332', '55555555-5555-5555-5555-555555555506'),
  ('program', '33333333-3333-3333-3333-333333333332', '55555555-5555-5555-5555-555555555510'),
  ('program', '33333333-3333-3333-3333-333333333332', '55555555-5555-5555-5555-555555555521'),
  ('program', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555503'),
  ('program', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555515'),
  ('program', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555516'),
  ('program', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555517'),
  ('program', '33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555518'),
  ('participant', '44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555501'),
  ('participant', '44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555503'),
  ('participant', '44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555504'),
  ('participant', '44444444-4444-4444-4444-444444444441', '55555555-5555-5555-5555-555555555506'),
  ('participant', '44444444-4444-4444-4444-444444444442', '55555555-5555-5555-5555-555555555509'),
  ('participant', '44444444-4444-4444-4444-444444444442', '55555555-5555-5555-5555-555555555510'),
  ('participant', '44444444-4444-4444-4444-444444444442', '55555555-5555-5555-5555-555555555511'),
  ('participant', '44444444-4444-4444-4444-444444444442', '55555555-5555-5555-5555-555555555518'),
  ('participant', '44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555503'),
  ('participant', '44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555515'),
  ('participant', '44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555516'),
  ('participant', '44444444-4444-4444-4444-444444444443', '55555555-5555-5555-5555-555555555517'),
  ('participant', '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555508'),
  ('participant', '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555512'),
  ('participant', '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555513'),
  ('participant', '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555514')
ON CONFLICT (entity_type, entity_id, skill_id) DO NOTHING;

INSERT INTO company_programs (company_id, program_id) VALUES
  ('11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333332'),
  ('11111111-1111-1111-1111-111111111112', '33333333-3333-3333-3333-333333333331'),
  ('11111111-1111-1111-1111-111111111113', '33333333-3333-3333-3333-333333333333')
ON CONFLICT (company_id, program_id) DO NOTHING;

INSERT INTO participant_programs (participant_id, program_id) VALUES
  ('44444444-4444-4444-4444-444444444441', '33333333-3333-3333-3333-333333333332'),
  ('44444444-4444-4444-4444-444444444442', '33333333-3333-3333-3333-333333333331'),
  ('44444444-4444-4444-4444-444444444443', '33333333-3333-3333-3333-333333333333'),
  ('44444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333331')
ON CONFLICT (participant_id, program_id) DO NOTHING;

INSERT INTO matches (
  match_type,
  source_type,
  source_id,
  source_name,
  target_type,
  target_id,
  target_name,
  score,
  shared_skills,
  explanation
) VALUES
  (
    'company_mentor',
    'company',
    '11111111-1111-1111-1111-111111111111',
    'FinAI Labs',
    'mentor',
    '22222222-2222-2222-2222-222222222221',
    'Asha Raman',
    0.8600,
    '["AI", "Fintech", "Regulatory Compliance"]'::jsonb,
    '["Startup company needs a mentor whose skills can guide business growth.", "Shared explicit skills: AI, Fintech, Regulatory Compliance", "Strong fintech and compliance mentorship fit."]'::jsonb
  ),
  (
    'company_mentor',
    'company',
    '11111111-1111-1111-1111-111111111112',
    'CloudCart Systems',
    'mentor',
    '22222222-2222-2222-2222-222222222222',
    'Marcus Lee',
    0.8400,
    '["Cloud", "Cybersecurity", "SaaS", "Go-To-Market"]'::jsonb,
    '["Startup company needs a mentor whose skills can guide business growth.", "Shared explicit skills: Cloud, Cybersecurity, SaaS, Go-To-Market", "Strong SaaS scale-up and go-to-market fit."]'::jsonb
  ),
  (
    'company_mentor',
    'company',
    '11111111-1111-1111-1111-111111111113',
    'GreenForge Robotics',
    'mentor',
    '22222222-2222-2222-2222-222222222223',
    'Priya Nair',
    0.8800,
    '["Data Analytics", "Manufacturing", "Robotics", "Supply Chain", "Operations"]'::jsonb,
    '["Startup company needs a mentor whose skills can guide business growth.", "Shared explicit skills: Manufacturing, Robotics, Supply Chain, Operations", "Strong manufacturing operations fit."]'::jsonb
  ),
  (
    'company_program',
    'company',
    '11111111-1111-1111-1111-111111111111',
    'FinAI Labs',
    'program',
    '33333333-3333-3333-3333-333333333332',
    'Fintech Compliance Lab',
    0.9000,
    '["Fintech", "Banking Infrastructure", "Regulatory Compliance"]'::jsonb,
    '["Company can use this program to grow participant skills.", "Shared explicit skills: Fintech, Banking Infrastructure, Regulatory Compliance", "Existing company-program relationship increases confidence."]'::jsonb
  ),
  (
    'company_program',
    'company',
    '11111111-1111-1111-1111-111111111112',
    'CloudCart Systems',
    'program',
    '33333333-3333-3333-3333-333333333331',
    'AI Growth Accelerator',
    0.7600,
    '["Product Management", "Fundraising"]'::jsonb,
    '["Company can use this program to grow participant skills.", "Shared explicit skills: Product Management, Fundraising", "Existing company-program relationship increases confidence."]'::jsonb
  ),
  (
    'company_program',
    'company',
    '11111111-1111-1111-1111-111111111113',
    'GreenForge Robotics',
    'program',
    '33333333-3333-3333-3333-333333333333',
    'Advanced Manufacturing Sprint',
    0.9200,
    '["Data Analytics", "Manufacturing", "Robotics", "Supply Chain", "Operations"]'::jsonb,
    '["Company can use this program to grow participant skills.", "Shared explicit skills: Manufacturing, Robotics, Supply Chain, Operations", "Existing company-program relationship increases confidence."]'::jsonb
  ),
  (
    'program_company',
    'program',
    '33333333-3333-3333-3333-333333333332',
    'Fintech Compliance Lab',
    'company',
    '11111111-1111-1111-1111-111111111111',
    'FinAI Labs',
    0.9000,
    '["Fintech", "Banking Infrastructure", "Regulatory Compliance"]'::jsonb,
    '["Program can recruit companies whose teams match its focus areas.", "Shared explicit skills: Fintech, Banking Infrastructure, Regulatory Compliance", "Existing company-program relationship increases confidence."]'::jsonb
  ),
  (
    'program_company',
    'program',
    '33333333-3333-3333-3333-333333333333',
    'Advanced Manufacturing Sprint',
    'company',
    '11111111-1111-1111-1111-111111111113',
    'GreenForge Robotics',
    0.9200,
    '["Data Analytics", "Manufacturing", "Robotics", "Supply Chain", "Operations"]'::jsonb,
    '["Program can recruit companies whose teams match its focus areas.", "Shared explicit skills: Manufacturing, Robotics, Supply Chain, Operations", "Existing company-program relationship increases confidence."]'::jsonb
  ),
  (
    'participant_program',
    'participant',
    '44444444-4444-4444-4444-444444444441',
    'Nadia Lim',
    'program',
    '33333333-3333-3333-3333-333333333332',
    'Fintech Compliance Lab',
    0.7800,
    '["Fintech", "Regulatory Compliance"]'::jsonb,
    '["Participant can join this program to improve relevant professional skills.", "Shared explicit skills: Fintech, Regulatory Compliance"]'::jsonb
  ),
  (
    'participant_program',
    'participant',
    '44444444-4444-4444-4444-444444444443',
    'Mei Chen',
    'program',
    '33333333-3333-3333-3333-333333333333',
    'Advanced Manufacturing Sprint',
    0.8200,
    '["Data Analytics", "Manufacturing", "Robotics", "Supply Chain"]'::jsonb,
    '["Participant can join this program to improve relevant professional skills.", "Shared explicit skills: Manufacturing, Robotics, Supply Chain"]'::jsonb
  )
ON CONFLICT (match_type, source_id, target_id) DO UPDATE SET
  score = EXCLUDED.score,
  shared_skills = EXCLUDED.shared_skills,
  explanation = EXCLUDED.explanation,
  status = 'recommended';
