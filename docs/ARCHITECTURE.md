# Architecture

MYRantai is organized around reusable relationship intelligence rather than directory-style records.

## Profile Enrichment

Every profile creation request runs through:

1. `ProfileAIService`
2. `SkillExtractionService`
3. `ShortBioService`
4. `EmbeddingService`
5. `EcosystemRepository`
6. `Neo4jService`
7. `MatchingService`

The Gemini prompts require valid JSON and prohibit unsupported skills. The backend then filters every returned skill against the original bio. This gives the platform a second guardrail even when model output is imperfect.

## Relationship Model

PostgreSQL is the operational source of truth for profiles, skills, and match records.

Neo4j is the relationship memory:

- `(Participant)-[:WORKS_FOR]->(Company)`
- `(Company)-[:ENROLLED_IN]->(Program)`
- `(Participant)-[:PARTICIPATES_IN]->(Program)`
- `(Mentor)-[:HAS_SKILL]->(Skill)`
- `(Company)-[:HAS_SKILL]->(Skill)`
- `(Participant)-[:HAS_SKILL]->(Skill)`
- `(Program)-[:FOCUSES_ON]->(Skill)`
- `(Company)-[:COMPANY_MENTOR]->(Mentor)`
- `(Company)-[:COMPANY_PROGRAM]->(Program)`
- `(Program)-[:PROGRAM_COMPANY]->(Company)`
- `(Participant)-[:PARTICIPANT_PROGRAM]->(Program)`

## Matching

The current matching engine is intentionally transparent. It combines explicit overlap, embedding similarity, and relationship/program context into one score while returning human-readable explanations.

Supported directional match stories:

- `company_mentor`: a startup company needs a mentor to guide business growth.
- `company_program`: a company finds programs that can grow its participants' skills.
- `program_company`: a program finds companies that fit its focus areas.
- `participant_program`: a participant finds programs that fit their professional skill profile.

The engine can later be upgraded to:

- use Gemini embeddings
- store vectors in `pgvector`
- include relationship decay over time
- include engagement outcomes
- expose programmable relationship policies per ecosystem owner
