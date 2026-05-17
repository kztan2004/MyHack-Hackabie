from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_embedding_service, get_graph_service, get_profile_ai_service, get_repository
from app.core.config import Settings, get_settings
from app.core.security import Token, create_access_token, require_auth
from app.graph.neo4j_service import Neo4jService
from app.repositories.ecosystem import EcosystemRepository
from app.schemas.entities import (
    CompanyProgramLink,
    GraphRead,
    MatchRead,
    ParticipantCreate,
    ParticipantProgramLink,
    ParticipantRead,
    ProfileCreate,
    ProfileRead,
    TokenRequest,
)
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService
from app.services.profile_service import ProfileAIService

router = APIRouter()


@router.post("/auth/token", response_model=Token)
async def login(payload: TokenRequest, settings: Settings = Depends(get_settings)) -> Token:
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return Token(access_token=create_access_token(payload.username, settings))


@router.post("/mentors", response_model=ProfileRead, dependencies=[Depends(require_auth)])
async def create_mentor(
    payload: ProfileCreate,
    repository: EcosystemRepository = Depends(get_repository),
    profile_ai: ProfileAIService = Depends(get_profile_ai_service),
    graph: Neo4jService | None = Depends(get_graph_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> ProfileRead:
    profile = await _create_profile("mentor", payload, repository, profile_ai, graph)
    await MatchingService(repository, embedding_service, graph).generate()
    return await _profile_response("mentor", profile, repository)


@router.post("/companies", response_model=ProfileRead, dependencies=[Depends(require_auth)])
async def create_company(
    payload: ProfileCreate,
    repository: EcosystemRepository = Depends(get_repository),
    profile_ai: ProfileAIService = Depends(get_profile_ai_service),
    graph: Neo4jService | None = Depends(get_graph_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> ProfileRead:
    profile = await _create_profile("company", payload, repository, profile_ai, graph)
    await MatchingService(repository, embedding_service, graph).generate()
    return await _profile_response("company", profile, repository)


@router.post("/participants", response_model=ParticipantRead, dependencies=[Depends(require_auth)])
async def create_participant(
    payload: ParticipantCreate,
    repository: EcosystemRepository = Depends(get_repository),
    profile_ai: ProfileAIService = Depends(get_profile_ai_service),
    graph: Neo4jService | None = Depends(get_graph_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> ParticipantRead:
    available_skills = await repository.get_all_skill_names()
    short_bio, skills, embedding = await profile_ai.enrich(payload.name, payload.raw_bio, available_skills)
    profile = await repository.create_profile(
        "participant",
        payload.name,
        payload.raw_bio,
        short_bio,
        skills,
        embedding,
        company_id=payload.company_id,
    )
    if graph:
        await graph.upsert_profile("participant", profile.id, profile.name, profile.short_bio, skills)
        if payload.company_id:
            await graph.link_participant_company(profile.id, payload.company_id)
    await MatchingService(repository, embedding_service, graph).generate()
    response = await _profile_response("participant", profile, repository)
    return ParticipantRead(**response.model_dump(), company_id=profile.company_id)


@router.post("/programs", response_model=ProfileRead, dependencies=[Depends(require_auth)])
async def create_program(
    payload: ProfileCreate,
    repository: EcosystemRepository = Depends(get_repository),
    profile_ai: ProfileAIService = Depends(get_profile_ai_service),
    graph: Neo4jService | None = Depends(get_graph_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> ProfileRead:
    profile = await _create_profile("program", payload, repository, profile_ai, graph)
    await MatchingService(repository, embedding_service, graph).generate()
    return await _profile_response("program", profile, repository)


@router.get("/mentors", response_model=list[ProfileRead], dependencies=[Depends(require_auth)])
async def list_mentors(repository: EcosystemRepository = Depends(get_repository)) -> list[ProfileRead]:
    return [await _profile_response("mentor", item, repository) for item in await repository.list_profiles("mentor")]


@router.get("/companies", response_model=list[ProfileRead], dependencies=[Depends(require_auth)])
async def list_companies(repository: EcosystemRepository = Depends(get_repository)) -> list[ProfileRead]:
    return [await _profile_response("company", item, repository) for item in await repository.list_profiles("company")]


@router.get("/participants", response_model=list[ParticipantRead], dependencies=[Depends(require_auth)])
async def list_participants(repository: EcosystemRepository = Depends(get_repository)) -> list[ParticipantRead]:
    profiles = await repository.list_profiles("participant")
    responses = []
    for profile in profiles:
        base = await _profile_response("participant", profile, repository)
        responses.append(ParticipantRead(**base.model_dump(), company_id=profile.company_id))
    return responses


@router.get("/programs", response_model=list[ProfileRead], dependencies=[Depends(require_auth)])
async def list_programs(repository: EcosystemRepository = Depends(get_repository)) -> list[ProfileRead]:
    return [await _profile_response("program", item, repository) for item in await repository.list_profiles("program")]


@router.post("/relationships/company-program", dependencies=[Depends(require_auth)])
async def link_company_program(
    payload: CompanyProgramLink,
    repository: EcosystemRepository = Depends(get_repository),
    profile_ai: ProfileAIService = Depends(get_profile_ai_service),
    graph: Neo4jService | None = Depends(get_graph_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> ProfileRead:
    linked = await repository.link_company_program(payload.company_id, payload.program_id)
    if not linked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company or program not found")
    if graph:
        await graph.link_company_program(payload.company_id, payload.program_id)
    
    # AI Enrichment: Update company profile based on program context
    company = await repository.get_profile("company", payload.company_id)
    program = await repository.get_profile("program", payload.program_id)
    if company and program:
        combined_bio = f"{company.raw_bio}\n\n[Context]: Participating in program: {program.name}. {program.raw_bio}"
        available_skills = await repository.get_all_skill_names()
        short_bio, skills, embedding = await profile_ai.enrich(company.name, combined_bio, available_skills)
        await repository.update_profile_ai_fields("company", company.id, short_bio, skills, embedding)
        if graph:
            await graph.upsert_profile("company", company.id, company.name, short_bio, skills)
        company = await repository.get_profile("company", payload.company_id)

    await MatchingService(repository, embedding_service, graph).generate()
    return await _profile_response("company", company, repository)


@router.post("/relationships/participant-program", dependencies=[Depends(require_auth)])
async def link_participant_program(
    payload: ParticipantProgramLink,
    repository: EcosystemRepository = Depends(get_repository),
    profile_ai: ProfileAIService = Depends(get_profile_ai_service),
    graph: Neo4jService | None = Depends(get_graph_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> ProfileRead:
    # 1. Establish the basic link
    linked = await repository.link_participant_program(payload.participant_id, payload.program_id)
    if not linked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant or program not found")
    
    # 2. AI Enrichment: Update participant profile based on program context
    participant = await repository.get_profile("participant", payload.participant_id)
    program = await repository.get_profile("program", payload.program_id)
    
    if participant and program:
        # Create a combined context for the AI
        combined_bio = f"{participant.raw_bio}\n\n[Activity]: Joined the program: {program.name}. {program.raw_bio}"
        available_skills = await repository.get_all_skill_names()
        
        # Re-enrich the participant
        short_bio, skills, embedding = await profile_ai.enrich(participant.name, combined_bio, available_skills)
        
        # Update the participant in DB
        await repository.update_profile_ai_fields("participant", participant.id, short_bio, skills, embedding)
        
        # Update the graph profile
        if graph:
            await graph.upsert_profile("participant", participant.id, participant.name, short_bio, skills)

    # 3. Graph link and matching
    if graph:
        await graph.link_participant_program(payload.participant_id, payload.program_id)
    
    await MatchingService(repository, embedding_service, graph).generate()
    return await _profile_response("participant", participant, repository)


@router.get("/matches", response_model=list[MatchRead], dependencies=[Depends(require_auth)])
async def list_matches(repository: EcosystemRepository = Depends(get_repository)) -> list[MatchRead]:
    return [MatchRead(**row) for row in await repository.list_matches()]


@router.get("/matches/company/{company_id}", response_model=list[MatchRead], dependencies=[Depends(require_auth)])
async def get_company_matches(
    company_id: UUID,
    repository: EcosystemRepository = Depends(get_repository),
) -> list[MatchRead]:
    return [MatchRead(**row) for row in await repository.list_matches(company_id=company_id)]


@router.get("/matches/program/{program_id}", response_model=list[MatchRead], dependencies=[Depends(require_auth)])
async def get_program_matches(
    program_id: UUID,
    repository: EcosystemRepository = Depends(get_repository),
) -> list[MatchRead]:
    return [MatchRead(**row) for row in await repository.list_matches(source_type="program", source_id=program_id)]


@router.get("/matches/participant/{participant_id}", response_model=list[MatchRead], dependencies=[Depends(require_auth)])
async def get_participant_matches(
    participant_id: UUID,
    repository: EcosystemRepository = Depends(get_repository),
) -> list[MatchRead]:
    return [MatchRead(**row) for row in await repository.list_matches(source_type="participant", source_id=participant_id)]


@router.post("/matches/generate", response_model=list[MatchRead], dependencies=[Depends(require_auth)])
async def generate_matches(
    repository: EcosystemRepository = Depends(get_repository),
    graph: Neo4jService | None = Depends(get_graph_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> list[MatchRead]:
    # Clean up any stale zero-score edges from before the skillless-link fix.
    if graph:
        await graph.delete_zero_score_matches()
    await MatchingService(repository, embedding_service, graph).generate()
    return [MatchRead(**row) for row in await repository.list_matches()]


@router.get("/graph", response_model=GraphRead, dependencies=[Depends(require_auth)])
async def read_graph(graph: Neo4jService | None = Depends(get_graph_service)) -> GraphRead:
    if not graph:
        return GraphRead(nodes=[], edges=[])
    return GraphRead.model_validate(await graph.read_graph())


async def _create_profile(
    entity_type: str,
    payload: ProfileCreate,
    repository: EcosystemRepository,
    profile_ai: ProfileAIService,
    graph: Neo4jService | None,
):
    available_skills = await repository.get_all_skill_names()
    short_bio, skills, embedding = await profile_ai.enrich(payload.name, payload.raw_bio, available_skills)
    profile = await repository.create_profile(entity_type, payload.name, payload.raw_bio, short_bio, skills, embedding)
    if graph:
        await graph.upsert_profile(entity_type, profile.id, profile.name, profile.short_bio, skills)
    return profile


async def _profile_response(entity_type: str, profile, repository: EcosystemRepository) -> ProfileRead:
    return ProfileRead(
        id=profile.id,
        name=profile.name,
        raw_bio=profile.raw_bio,
        short_bio=profile.short_bio,
        skills=await repository.get_skill_names(entity_type, profile.id),
        created_at=profile.created_at,
    )
