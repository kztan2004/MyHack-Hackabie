import type { Profile } from "@/lib/types";

export function ProfileCard({ profile, compact = false, highlight = false }: { profile: Profile; compact?: boolean; highlight?: boolean }) {
  return (
    <article className={`${compact ? "" : "rounded-md border bg-white p-4"} ${highlight ? "border-pine ring-1 ring-pine/20 shadow-lg" : "border-line"} min-w-0 transition-all`}>
      <div className="flex items-start justify-between gap-3">
        <h2 className="break-words text-base font-semibold text-ink">{profile.name}</h2>
        <span className="shrink-0 rounded bg-panel px-2 py-1 text-xs text-slate-500">
          {new Date(profile.created_at).toLocaleDateString()}
        </span>
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-600 italic">
        {highlight ? "✨ AI Enhanced: " : ""}{profile.short_bio}
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {profile.skills.length ? (
          profile.skills.map((skill) => (
            <span key={skill} className="rounded bg-amber-50 px-2 py-1 text-xs font-medium text-saffron border border-amber-200/50">
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
