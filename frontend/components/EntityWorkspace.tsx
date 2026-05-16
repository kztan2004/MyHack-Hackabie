import { FormEvent, useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import type { EntityKind, Profile } from "@/lib/types";

const titleByKind: Record<EntityKind, string> = {
  mentor: "Mentors",
  company: "Companies",
  participant: "Participants",
  program: "Programs"
};

const singularByKind: Record<EntityKind, string> = {
  mentor: "Mentor",
  company: "Company",
  participant: "Participant",
  program: "Program"
};

const placeholderByKind: Record<EntityKind, string> = {
  mentor: "Example: AI mentor with fintech and product management experience...",
  company: "Example: Company building AI tools for banking infrastructure...",
  participant: "Example: Product lead working on fintech data analytics...",
  program: "Example: Program focused on AI, fintech, and regulatory compliance..."
};

export function EntityWorkspace({ kind }: { kind: EntityKind }) {
  const [items, setItems] = useState<Profile[]>([]);
  const [companies, setCompanies] = useState<Profile[]>([]);
  const [name, setName] = useState("");
  const [rawBio, setRawBio] = useState("");
  const [companyId, setCompanyId] = useState("");
  const [created, setCreated] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const title = titleByKind[kind];
  const canAttachCompany = kind === "participant";

  async function load() {
    const [profiles, companyProfiles] = await Promise.all([
      api.listProfiles(kind),
      canAttachCompany ? api.listProfiles("company") : Promise.resolve([])
    ]);
    setItems(profiles);
    setCompanies(companyProfiles);
  }

  useEffect(() => {
    setCreated(null);
    load().catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to load profiles"));
  }, [kind]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const profile = await api.createProfile(kind, {
        name,
        raw_bio: rawBio,
        company_id: canAttachCompany && companyId ? companyId : null
      });
      setCreated(profile);
      setName("");
      setRawBio("");
      setCompanyId("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save profile");
    } finally {
      setLoading(false);
    }
  }

  const countText = useMemo(() => `${items.length} ${items.length === 1 ? "record" : "records"}`, [items.length]);

  return (
    <section>
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">{title}</h1>
          <p className="mt-1 text-sm text-slate-500">{countText}</p>
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

      <div className="grid gap-5 xl:grid-cols-[420px_1fr]">
        <form onSubmit={submit} className="rounded-md border border-line bg-white p-4">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink">
            <Plus size={17} />
            Add {singularByKind[kind]}
          </div>
          <label className="block text-sm font-medium text-slate-700">
            Name
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              minLength={2}
              className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-pine"
            />
          </label>
          {canAttachCompany ? (
            <label className="mt-4 block text-sm font-medium text-slate-700">
              Company
              <select
                value={companyId}
                onChange={(event) => setCompanyId(event.target.value)}
                className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-pine"
              >
                <option value="">Unassigned</option>
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label className="mt-4 block text-sm font-medium text-slate-700">
            Bio
            <textarea
              value={rawBio}
              onChange={(event) => setRawBio(event.target.value)}
              required
              minLength={10}
              rows={7}
              placeholder={placeholderByKind[kind]}
              className="mt-1 w-full resize-none rounded-md border border-line p-3 outline-none focus:border-pine"
            />
          </label>
          {error ? <div className="mt-3 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
          <button
            type="submit"
            disabled={loading}
            className="mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-pine px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
          >
            <Sparkles size={17} />
            {loading ? "Processing" : "Extract and Save"}
          </button>
        </form>

        <div className="space-y-4">
          {created ? <ProfileResult profile={created} /> : null}
          <div className="grid gap-3 md:grid-cols-2">
            {items.map((item) => (
              <ProfileCard key={item.id} profile={item} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function ProfileResult({ profile }: { profile: Profile }) {
  return (
    <div className="rounded-md border border-pine bg-white p-4">
      <div className="mb-2 text-sm font-semibold text-pine">Latest AI extraction</div>
      <ProfileCard profile={profile} compact />
    </div>
  );
}

function ProfileCard({ profile, compact = false }: { profile: Profile; compact?: boolean }) {
  return (
    <article className={`${compact ? "" : "rounded-md border border-line bg-white p-4"} min-w-0`}>
      <div className="flex items-start justify-between gap-3">
        <h2 className="break-words text-base font-semibold text-ink">{profile.name}</h2>
        <span className="shrink-0 rounded bg-panel px-2 py-1 text-xs text-slate-500">
          {new Date(profile.created_at).toLocaleDateString()}
        </span>
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600">{profile.short_bio}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {profile.skills.length ? (
          profile.skills.map((skill) => (
            <span key={skill} className="rounded bg-amber-50 px-2 py-1 text-xs font-medium text-saffron">
              {skill}
            </span>
          ))
        ) : (
          <span className="text-sm text-slate-400">No explicit skills extracted</span>
        )}
      </div>
    </article>
  );
}
