import { useEffect, useState } from "react";
import { Building2, Handshake, Rocket, Users } from "lucide-react";
import { api } from "@/lib/api";
import type { EntityKind } from "@/lib/types";
import { EntityWorkspace } from "@/components/EntityWorkspace";
import { GraphCanvas } from "@/components/GraphCanvas";
import { MatchesPanel } from "@/components/MatchesPanel";
import { RelationshipsPanel } from "@/components/RelationshipsPanel";

const statConfig: Array<{ kind: EntityKind; label: string; icon: typeof Handshake; color: string }> = [
  { kind: "mentor", label: "Mentors", icon: Handshake, color: "text-pine" },
  { kind: "company", label: "Companies", icon: Building2, color: "text-blue-600" },
  { kind: "participant", label: "Participants", icon: Users, color: "text-berry" },
  { kind: "program", label: "Programs", icon: Rocket, color: "text-saffron" }
];

export function Dashboard() {
  const [counts, setCounts] = useState<Record<EntityKind, number>>({
    mentor: 0,
    company: 0,
    participant: 0,
    program: 0
  });

  useEffect(() => {
    Promise.all(statConfig.map((item) => api.listProfiles(item.kind)))
      .then((values) => {
        setCounts({
          mentor: values[0].length,
          company: values[1].length,
          participant: values[2].length,
          program: values[3].length
        });
      })
      .catch(() => undefined);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">Programmable ecosystem relationships</p>
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        {statConfig.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.kind} className="rounded-md border border-line bg-white p-4">
              <div className={`mb-3 ${item.color}`}>
                <Icon size={22} />
              </div>
              <div className="text-2xl font-semibold text-ink">{counts[item.kind]}</div>
              <div className="text-sm text-slate-500">{item.label}</div>
            </div>
          );
        })}
      </div>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)]">
        <GraphCanvas compact />
      </div>
      <RelationshipsPanel />
      <EntityWorkspace kind="mentor" />
    </div>
  );
}
