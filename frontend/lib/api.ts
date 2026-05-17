import type { EntityKind, GraphData, Match, Profile } from "@/lib/types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const endpointByKind: Record<EntityKind, string> = {
  mentor: "mentors",
  company: "companies",
  participant: "participants",
  program: "programs"
};

type CreateProfilePayload = {
  name: string;
  raw_bio: string;
  company_id?: string | null;
};

type CompanyProgramPayload = {
  company_id: string;
  program_id: string;
};

type ParticipantProgramPayload = {
  participant_id: string;
  program_id: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      // Bypass ngrok's browser interstitial when the backend is tunnelled via ngrok
      "ngrok-skip-browser-warning": "true",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return (await response.json()) as T;
}

export const api = {
  createProfile(kind: EntityKind, payload: CreateProfilePayload) {
    return request<Profile>(`/${endpointByKind[kind]}`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  listProfiles(kind: EntityKind) {
    return request<Profile[]>(`/${endpointByKind[kind]}`);
  },
  listMatches() {
    return request<Match[]>("/matches");
  },
  listCompanyMatches(companyId: string) {
    return request<Match[]>(`/matches/company/${companyId}`);
  },
  listProgramMatches(programId: string) {
    return request<Match[]>(`/matches/program/${programId}`);
  },
  listParticipantMatches(participantId: string) {
    return request<Match[]>(`/matches/participant/${participantId}`);
  },
  generateMatches() {
    return request<Match[]>("/matches/generate", { method: "POST" });
  },
  linkCompanyProgram(payload: CompanyProgramPayload) {
    return request<Profile>("/relationships/company-program", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  linkParticipantProgram(payload: ParticipantProgramPayload) {
    return request<Profile>("/relationships/participant-program", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  readGraph() {
    return request<GraphData>("/graph");
  }
};
