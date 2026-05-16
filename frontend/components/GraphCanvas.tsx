import { useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import type { GraphData, GraphNode } from "@/lib/types";

const typeColor: Record<string, string> = {
  Mentor: "#0f766e",
  Company: "#2563eb",
  Participant: "#be3455",
  Program: "#d97706",
  Skill: "#4b5563"
};

const columns: Record<string, number> = {
  Mentor: 120,
  Participant: 280,
  Company: 470,
  Program: 650,
  Skill: 830
};

export function GraphCanvas({ compact = false }: { compact?: boolean }) {
  const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] });
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      setGraph(await api.readGraph());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load graph");
    }
  }

  useEffect(() => {
    load();
  }, []);

  const positioned = useMemo(() => positionNodes(graph.nodes), [graph.nodes]);
  const nodeById = useMemo(() => new Map(positioned.map((node) => [node.id, node])), [positioned]);

  return (
    <section>
      <div className="mb-4 flex items-end justify-between gap-3">
        <div>
          <h1 className={`${compact ? "text-xl" : "text-2xl"} font-semibold text-ink`}>Relationship Graph</h1>
          <p className="mt-1 text-sm text-slate-500">{graph.nodes.length} nodes, {graph.edges.length} relationships</p>
        </div>
        <button
          type="button"
          onClick={load}
          className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium text-ink hover:bg-panel"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      {error ? <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      <div className="overflow-hidden rounded-md border border-line bg-white">
        <svg viewBox="0 0 980 520" className={`${compact ? "h-[420px]" : "h-[620px]"} w-full bg-white`}>
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 z" fill="#94a3b8" />
            </marker>
          </defs>
          {graph.edges.map((edge, index) => {
            const source = nodeById.get(edge.source);
            const target = nodeById.get(edge.target);
            if (!source || !target) return null;
            const recommendation = edge.score !== null && edge.score !== undefined;
            return (
              <g key={`${edge.source}-${edge.target}-${edge.type}-${index}`}>
                <line
                  x1={source.x}
                  y1={source.y}
                  x2={target.x}
                  y2={target.y}
                  stroke={recommendation ? "#0f766e" : "#94a3b8"}
                  strokeWidth={recommendation ? 2.4 : 1.4}
                  markerEnd="url(#arrow)"
                />
                <text
                  x={(source.x + target.x) / 2}
                  y={(source.y + target.y) / 2 - 7}
                  textAnchor="middle"
                  className="fill-slate-500 text-[10px] font-medium"
                >
                  {edge.type}
                </text>
              </g>
            );
          })}
          {positioned.map((node) => (
            <GraphNodeShape key={node.id} node={node} />
          ))}
          {!graph.nodes.length ? (
            <text x="490" y="260" textAnchor="middle" className="fill-slate-500 text-sm">
              No graph relationships yet.
            </text>
          ) : null}
        </svg>
      </div>
    </section>
  );
}

type PositionedNode = GraphNode & { x: number; y: number };

function positionNodes(nodes: GraphNode[]): PositionedNode[] {
  const groups = nodes.reduce<Record<string, GraphNode[]>>((acc, node) => {
    acc[node.type] = [...(acc[node.type] ?? []), node];
    return acc;
  }, {});
  return Object.entries(groups).flatMap(([type, group]) => {
    const x = columns[type] ?? 500;
    const gap = Math.min(90, 420 / Math.max(group.length, 1));
    const start = 90;
    return group.map((node, index) => ({ ...node, x, y: start + index * gap }));
  });
}

function GraphNodeShape({ node }: { node: PositionedNode }) {
  const fill = typeColor[node.type] ?? "#64748b";
  const label = node.label.length > 22 ? `${node.label.slice(0, 21)}...` : node.label;
  return (
    <g className="node-shadow">
      <circle cx={node.x} cy={node.y} r={26} fill={fill} />
      <text x={node.x} y={node.y + 4} textAnchor="middle" className="fill-white text-[10px] font-bold">
        {node.type.slice(0, 1)}
      </text>
      <text x={node.x} y={node.y + 43} textAnchor="middle" className="fill-ink text-[11px] font-semibold">
        {label}
      </text>
    </g>
  );
}
