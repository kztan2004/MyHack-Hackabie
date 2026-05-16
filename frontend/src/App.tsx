import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Dashboard } from "@/components/Dashboard";
import { EntityWorkspace } from "@/components/EntityWorkspace";
import { GraphCanvas } from "@/components/GraphCanvas";
import { MatchesPanel } from "@/components/MatchesPanel";

const routes = {
  "/": <Dashboard />,
  "/mentors": <EntityWorkspace kind="mentor" />,
  "/companies": <EntityWorkspace kind="company" />,
  "/participants": <EntityWorkspace kind="participant" />,
  "/programs": <EntityWorkspace kind="program" />,
  "/matches": <MatchesPanel />,
  "/graph": <GraphCanvas />
};

type RoutePath = keyof typeof routes;

function normalizePath(pathname: string): RoutePath {
  return pathname in routes ? (pathname as RoutePath) : "/";
}

export function App() {
  const [path, setPath] = useState<RoutePath>(() => normalizePath(window.location.pathname));

  useEffect(() => {
    function onPopState() {
      setPath(normalizePath(window.location.pathname));
    }
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const navigate = useMemo(
    () => (targetPath: string) => {
      const normalized = normalizePath(targetPath);
      if (normalized !== path) {
        window.history.pushState({}, "", normalized);
        setPath(normalized);
      }
    },
    [path]
  );

  return (
    <AppShell currentPath={path} onNavigate={navigate}>
      {routes[path]}
    </AppShell>
  );
}
