import type { MouseEvent, ReactNode } from "react";
import { Building2, CircleDot, GitBranch, Handshake, Link2, Network, Rocket, Users } from "lucide-react";

const nav = [
  { href: "/", label: "Dashboard", icon: Network },
  { href: "/mentors", label: "Mentors", icon: Handshake },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/participants", label: "Participants", icon: Users },
  { href: "/programs", label: "Programs", icon: Rocket },
  { href: "/relationships", label: "Linkages", icon: Link2 },
  { href: "/matches", label: "Matches", icon: CircleDot },
  { href: "/graph", label: "Graph", icon: GitBranch }
];

export function AppShell({
  children,
  currentPath,
  onNavigate
}: {
  children: ReactNode;
  currentPath: string;
  onNavigate: (path: string) => void;
}) {
  function navigate(event: MouseEvent<HTMLAnchorElement>, path: string) {
    event.preventDefault();
    onNavigate(path);
  }

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white px-4 py-5 lg:block">
        <div className="mb-8 px-2">
          <div className="text-xl font-semibold tracking-normal text-ink">MYRantai</div>
          <div className="mt-1 text-sm text-slate-500">AI-Powered Ecosystem</div>
        </div>
        <nav className="space-y-1">
          {nav.map((item) => {
            const active = currentPath === item.href;
            const Icon = item.icon;
            return (
              <a
                key={item.href}
                href={item.href}
                onClick={(event) => navigate(event, item.href)}
                className={`flex h-11 items-center gap-3 rounded-md px-3 text-sm font-medium transition ${active ? "bg-ink text-white" : "text-slate-600 hover:bg-panel hover:text-ink"
                  }`}
              >
                <Icon size={18} />
                {item.label}
              </a>
            );
          })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <div className="border-b border-line bg-white px-5 py-4 lg:hidden">
          <div className="text-lg font-semibold text-ink">MYRantai</div>
        </div>
        <div className="mx-auto max-w-7xl px-5 py-6">{children}</div>
      </main>
    </div>
  );
}
