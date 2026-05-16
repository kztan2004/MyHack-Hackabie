import { useEffect, useMemo, useState } from "react";
import { RefreshCw, WandSparkles } from "lucide-react";
import { api } from "@/lib/api";
import type { Match, Profile } from "@/lib/types";

type MatchMode = "company" | "program" | "participant";
type CompanyView = "mentor" | "program";

const modeLabel: Record<MatchMode, string> = {
  company: "Company",
  program: "Program",
  participant: "Participant"
};

export function MatchesPanel({ compact = false }: { compact?: boolean }) {
  const [mode, setMode] = useState<MatchMode>("company");
  const [companyView, setCompanyView] = useState<CompanyView>("mentor");
  const [companies, setCompanies] = useState<Profile[]>([]);
  const [programs, setPrograms] = useState<Profile[]>([]);
  const [participants, setParticipants] = useState<Profile[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState("");
  const [selectedProgramId, setSelectedProgramId] = useState("");
  const [selectedParticipantId, setSelectedParticipantId] = useState("");
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedId = mode === "company" ? selectedCompanyId : mode === "program" ? selectedProgramId : selectedParticipantId;
  const selectedProfile = useMemo(() => {
    const items = mode === "company" ? companies : mode === "program" ? programs : participants;
    return items.find((item) => item.id === selectedId);
  }, [companies, mode, participants, programs, selectedId]);

  const visibleMatches = useMemo(() => {
    const expectedType =
      mode === "company" ? (companyView === "mentor" ? "company_mentor" : "company_program") :
        mode === "program" ? "program_company" :
          "participant_program";
    const sourceType = mode;
    return matches.filter(
      (match) => match.match_type === expectedType && match.source_type === sourceType && match.source_id === selectedId
    );
  }, [companyView, matches, mode, selectedId]);

  async function loadProfiles() {
    const [companyProfiles, programProfiles, participantProfiles] = await Promise.all([
      api.listProfiles("company"),
      api.listProfiles("program"),
      api.listProfiles("participant")
    ]);
    setCompanies(companyProfiles);
    setPrograms(programProfiles);
    setParticipants(participantProfiles);
    setSelectedCompanyId((current) => current || companyProfiles[0]?.id || "");
    setSelectedProgramId((current) => current || programProfiles[0]?.id || "");
    setSelectedParticipantId((current) => current || participantProfiles[0]?.id || "");
  }

  async function load() {
    setError("");
    if (!selectedId) {
      setMatches([]);
      return;
    }
    try {
      if (mode === "company") {
        setMatches(await api.listCompanyMatches(selectedId));
      } else if (mode === "program") {
        setMatches(await api.listProgramMatches(selectedId));
      } else {
        setMatches(await api.listParticipantMatches(selectedId));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load matches");
    }
  }

  async function generate() {
    setLoading(true);
    setError("");
    try {
      await api.generateMatches();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to generate matches");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfiles().catch((err: unknown) =>
      setError(err instanceof Error ? err.message : "Unable to load match profiles")
    );
  }, []);

  useEffect(() => {
    load().catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to load matches"));
  }, [mode, selectedId]);

  const targetLabel = mode === "company" ? (companyView === "mentor" ? "Mentor" : "Program") :
    mode === "program" ? "Company" :
      "Program";

  return (
    <section>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className={`${compact ? "text-xl" : "text-2xl"} font-semibold text-ink`}>Matches</h1>
          <p className="mt-1 text-sm text-slate-500">
            {selectedProfile ? selectedProfile.name : `Select a ${mode}`}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={load}
            className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium text-ink hover:bg-panel"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          <button
            type="button"
            onClick={generate}
            disabled={loading || !selectedId}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-ink px-3 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60"
          >
            <WandSparkles size={16} />
            {loading ? "Generating" : "Generate"}
          </button>
        </div>
      </div>

      <div className="mb-4 grid gap-3 rounded-md border border-line bg-white p-4 lg:grid-cols-[260px_minmax(0,1fr)_260px]">
        <div>
          <div className="mb-1 text-sm font-medium text-slate-700">Match type</div>
          <div className="grid h-11 grid-cols-3 rounded-md border border-line bg-panel p-1">
            {(["company", "program", "participant"] as MatchMode[]).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setMode(item)}
                className={`rounded text-sm font-medium ${mode === item ? "bg-white text-ink shadow-sm" : "text-slate-500"}`}
              >
                {modeLabel[item]}
              </button>
            ))}
          </div>
        </div>
        <ProfileSelect
          label={modeLabel[mode]}
          value={selectedId}
          options={mode === "company" ? companies : mode === "program" ? programs : participants}
          onChange={(value) => {
            if (mode === "company") setSelectedCompanyId(value);
            if (mode === "program") setSelectedProgramId(value);
            if (mode === "participant") setSelectedParticipantId(value);
          }}
        />
        {mode === "company" ? (
          <div>
            <div className="mb-1 text-sm font-medium text-slate-700">Show</div>
            <div className="grid h-11 grid-cols-2 rounded-md border border-line bg-panel p-1">
              <button
                type="button"
                onClick={() => setCompanyView("mentor")}
                className={`rounded text-sm font-medium ${companyView === "mentor" ? "bg-white text-ink shadow-sm" : "text-slate-500"}`}
              >
                Mentors
              </button>
              <button
                type="button"
                onClick={() => setCompanyView("program")}
                className={`rounded text-sm font-medium ${companyView === "program" ? "bg-white text-ink shadow-sm" : "text-slate-500"}`}
              >
                Programs
              </button>
            </div>
          </div>
        ) : (
          <div className="rounded-md border border-line bg-panel px-3 py-2">
            <div className="text-xs font-semibold uppercase text-slate-500">Showing</div>
            <div className="mt-1 text-sm font-medium text-ink">
              {mode === "program" ? "Matched companies" : "Matched programs"}
            </div>
          </div>
        )}
      </div>

      {error ? <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      <div className="overflow-hidden rounded-md border border-line bg-white">
        <div className="grid grid-cols-[1fr_90px] gap-3 border-b border-line bg-panel px-4 py-3 text-xs font-semibold uppercase text-slate-500 md:grid-cols-[1.2fr_1.5fr_90px]">
          <span>{targetLabel}</span>
          <span className="hidden md:block">Why it matches</span>
          <span>Score</span>
        </div>
        {visibleMatches.length ? (
          visibleMatches.slice(0, compact ? 5 : undefined).map((match) => (
            <MatchRow key={match.id} match={match} />
          ))
        ) : (
          <div className="px-4 py-10 text-sm text-slate-500">
            {selectedId ? "No matches yet. Click Generate to calculate recommendations." : `Select a ${mode}.`}
          </div>
        )}
      </div>
    </section>
  );
}

function ProfileSelect({
  label,
  value,
  options,
  onChange
}: {
  label: string;
  value: string;
  options: Profile[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-pine"
      >
        <option value="">Select {label.toLowerCase()}</option>
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.name}
          </option>
        ))}
      </select>
    </label>
  );
}

function MatchRow({ match }: { match: Match }) {
  return (
    <article className="border-b border-line px-4 py-4 last:border-b-0">
      <div className="grid grid-cols-[1fr_90px] gap-3 md:grid-cols-[1.2fr_1.5fr_90px]">
        <div className="min-w-0">
          <div className="font-medium text-ink">{match.target_name}</div>
          <div className="text-xs capitalize text-slate-500">{match.target_type}</div>
        </div>
        <ul className="hidden space-y-1 text-sm text-slate-600 md:block">
          {match.explanation.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
        <div className="font-semibold text-pine">{Math.round(match.score * 100)}%</div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {match.shared_skills.map((skill) => (
          <span key={skill} className="rounded bg-amber-50 px-2 py-1 text-xs font-medium text-saffron">
            {skill}
          </span>
        ))}
      </div>
      <ul className="mt-3 space-y-1 text-sm text-slate-600 md:hidden">
        {match.explanation.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </article>
  );
}
