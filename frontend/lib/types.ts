export type EntityKind = "mentor" | "company" | "participant" | "program";

export type Profile = {
  id: string;
  name: string;
  raw_bio: string;
  short_bio: string;
  skills: string[];
  company_id?: string | null;
  created_at: string;
};

export type Match = {
  id: string;
  match_type: string;
  source_type: EntityKind;
  source_id: string;
  source_name: string;
  target_type: EntityKind;
  target_id: string;
  target_name: string;
  score: number;
  shared_skills: string[];
  explanation: string[];
  status: string;
  created_at: string;
};

export type GraphNode = {
  id: string;
  label: string;
  type: "Mentor" | "Company" | "Participant" | "Program" | "Skill" | string;
};

export type GraphEdge = {
  source: string;
  target: string;
  type: string;
  score?: number | null;
};

export type GraphData = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};
