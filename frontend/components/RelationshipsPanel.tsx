import { FormEvent, useEffect, useState } from "react";
import { Link2, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";

export function RelationshipsPanel() {
  const [companies, setCompanies] = useState<Profile[]>([]);
  const [participants, setParticipants] = useState<Profile[]>([]);
  const [programs, setPrograms] = useState<Profile[]>([]);
  const [companyId, setCompanyId] = useState("");
  const [companyProgramId, setCompanyProgramId] = useState("");
  const [participantId, setParticipantId] = useState("");
  const [participantProgramId, setParticipantProgramId] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setError("");
    const [companyProfiles, participantProfiles, programProfiles] = await Promise.all([
      api.listProfiles("company"),
      api.listProfiles("participant"),
      api.listProfiles("program")
    ]);
    setCompanies(companyProfiles);
    setParticipants(participantProfiles);
    setPrograms(programProfiles);
  }

  useEffect(() => {
    load().catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to load relationships"));
  }, []);

  async function submitCompanyProgram(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("");
    setError("");
    try {
      await api.linkCompanyProgram({ company_id: companyId, program_id: companyProgramId });
      setStatus("Company linked to program");
      setCompanyProgramId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to link company and program");
    } finally {
      setLoading(false);
    }
  }

  async function submitParticipantProgram(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("");
    setError("");
    try {
      await api.linkParticipantProgram({ participant_id: participantId, program_id: participantProgramId });
      setStatus("Participant linked to program");
      setParticipantProgramId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to link participant and program");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Relationships</h1>
          <p className="mt-1 text-sm text-slate-500">Program enrollment and participation</p>
        </div>
        <button
          type="button"
          onClick={() => load()}
          className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium text-ink hover:bg-panel"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      {error ? <div className="mb-3 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      {status ? <div className="mb-3 rounded-md bg-emerald-50 p-3 text-sm text-pine">{status}</div> : null}
      <div className="grid gap-3 md:grid-cols-2">
        <RelationshipForm
          title="Company program"
          leftLabel="Company"
          leftValue={companyId}
          leftOptions={companies}
          onLeftChange={setCompanyId}
          rightLabel="Program"
          rightValue={companyProgramId}
          rightOptions={programs}
          onRightChange={setCompanyProgramId}
          onSubmit={submitCompanyProgram}
          loading={loading}
        />
        <RelationshipForm
          title="Participant program"
          leftLabel="Participant"
          leftValue={participantId}
          leftOptions={participants}
          onLeftChange={setParticipantId}
          rightLabel="Program"
          rightValue={participantProgramId}
          rightOptions={programs}
          onRightChange={setParticipantProgramId}
          onSubmit={submitParticipantProgram}
          loading={loading}
        />
      </div>
    </section>
  );
}

type RelationshipFormProps = {
  title: string;
  leftLabel: string;
  leftValue: string;
  leftOptions: Profile[];
  onLeftChange: (value: string) => void;
  rightLabel: string;
  rightValue: string;
  rightOptions: Profile[];
  onRightChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  loading: boolean;
};

function RelationshipForm({
  title,
  leftLabel,
  leftValue,
  leftOptions,
  onLeftChange,
  rightLabel,
  rightValue,
  rightOptions,
  onRightChange,
  onSubmit,
  loading
}: RelationshipFormProps) {
  const disabled = loading || !leftValue || !rightValue;

  return (
    <form onSubmit={onSubmit} className="rounded-md border border-line bg-white p-4">
      <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink">
        <Link2 size={17} />
        {title}
      </div>
      <label className="block text-sm font-medium text-slate-700">
        {leftLabel}
        <select
          value={leftValue}
          onChange={(event) => onLeftChange(event.target.value)}
          className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-pine"
        >
          <option value="">Select {leftLabel.toLowerCase()}</option>
          {leftOptions.map((option) => (
            <option key={option.id} value={option.id}>
              {option.name}
            </option>
          ))}
        </select>
      </label>
      <label className="mt-4 block text-sm font-medium text-slate-700">
        {rightLabel}
        <select
          value={rightValue}
          onChange={(event) => onRightChange(event.target.value)}
          className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-pine"
        >
          <option value="">Select {rightLabel.toLowerCase()}</option>
          {rightOptions.map((option) => (
            <option key={option.id} value={option.id}>
              {option.name}
            </option>
          ))}
        </select>
      </label>
      <button
        type="submit"
        disabled={disabled}
        className="mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60"
      >
        <Link2 size={17} />
        Link
      </button>
    </form>
  );
}
