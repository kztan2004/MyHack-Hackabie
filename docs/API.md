# API Documentation

Base URL: `http://localhost:8000/api`

## Auth

`POST /auth/token`

```json
{
  "username": "admin",
  "password": "admin"
}
```

Returns:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

Set `DISABLE_AUTH=true` for local demo mode.

## Profiles

`POST /mentors`

`POST /companies`

`POST /programs`

```json
{
  "name": "Asha Raman",
  "raw_bio": "AI and fintech mentor with product management experience."
}
```

`POST /participants`

```json
{
  "name": "Nadia Lim",
  "raw_bio": "Product lead working on fintech data analytics.",
  "company_id": "optional-company-uuid"
}
```

Response:

```json
{
  "id": "uuid",
  "name": "Asha Raman",
  "raw_bio": "...",
  "short_bio": "AI and fintech mentor with product management experience.",
  "skills": ["AI", "Fintech", "Product Management"],
  "created_at": "2026-05-16T10:00:00Z"
}
```

List endpoints:

- `GET /mentors`
- `GET /companies`
- `GET /participants`
- `GET /programs`

## Relationships

`POST /relationships/company-program`

```json
{
  "company_id": "company-uuid",
  "program_id": "program-uuid"
}
```

Returns:

```json
{
  "status": "linked"
}
```

The backend persists the relationship, mirrors it to Neo4j when available, merges the program's explicit skills into the company profile, and recomputes ecosystem matches.

`POST /relationships/participant-program`

```json
{
  "participant_id": "participant-uuid",
  "program_id": "program-uuid"
}
```

Returns:

```json
{
  "status": "linked"
}
```

The backend persists the relationship and mirrors it to Neo4j when available.

## Matches

`POST /matches/generate`

Recomputes ecosystem matches for:

- `company_mentor`
- `company_program`
- `program_company`
- `participant_program`

`GET /matches`

`GET /matches/company/{id}`

`GET /matches/program/{id}`

`GET /matches/participant/{id}`

Response:

```json
[
  {
    "id": "uuid",
    "match_type": "company_mentor",
    "source_type": "company",
    "source_id": "company-uuid",
    "source_name": "FinAI Labs",
    "target_type": "mentor",
    "target_id": "mentor-uuid",
    "target_name": "Asha Raman",
    "score": 0.82,
    "shared_skills": ["AI", "Fintech"],
    "explanation": [
      "Startup company needs a mentor whose skills can guide business growth.",
      "Shared explicit skills: AI, Fintech",
      "Profile summaries and skill text show semantic alignment."
    ],
    "status": "recommended",
    "created_at": "2026-05-16T10:00:00Z"
  }
]
```

Score calculation:

- 45% exact normalized skill overlap between source and target skills
- 40% embedding similarity over short bio plus explicit skills
- 15% relationship/program bonus, currently used when a company is already linked to a program

The match stories are directional. `company_mentor` answers which mentors can guide a startup company. `company_program` answers which programs can grow the company's participant skills. `program_company` answers which companies fit a program's focus. `participant_program` answers which programs fit a participant's skill profile.

## Graph

`GET /graph`

Returns Neo4j-backed graph data:

```json
{
  "nodes": [
    { "id": "uuid", "label": "Asha Raman", "type": "Mentor" }
  ],
  "edges": [
    { "source": "company-uuid", "target": "mentor-uuid", "type": "COMPANY_MENTOR", "score": 0.82 }
  ]
}
```
