import { useEffect, useMemo, useRef, useState } from "react";
import { RefreshCw, ZoomIn, ZoomOut, Maximize } from "lucide-react";
import * as d3 from "d3";
import { api } from "@/lib/api";
import type { GraphData } from "@/lib/types";

export function GraphCanvas({ compact = false }: { compact?: boolean }) {
  const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] });
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

  const filteredGraph = useMemo(() => {
    if (!search.trim()) return graph;
    const term = search.toLowerCase();
    const matches = graph.nodes.filter((n) => n.label.toLowerCase().includes(term));
    const matchIds = new Set(matches.map((n) => n.id));
    
    // One chain: matched nodes + their immediate neighbors
    const edges = graph.edges.filter((e) => matchIds.has(e.source) || matchIds.has(e.target));
    const neighborIds = new Set<string>();
    edges.forEach((e) => {
      neighborIds.add(e.source);
      neighborIds.add(e.target);
    });

    return {
      nodes: graph.nodes.filter((n) => matchIds.has(n.id) || neighborIds.has(n.id)),
      edges
    };
  }, [graph, search]);

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

  useEffect(() => {
    if (!svgRef.current || !filteredGraph.nodes.length) return;

    const width = 800;
    const height = compact ? 300 : 500;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    svg
      .attr("viewBox", [0, 0, width, height])
      .style("background-color", "#0f172a")
      .style("border-radius", "0.75rem");

    // Main container for zooming
    const g = svg.append("g");

    // Zoom setup
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 5])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    zoomRef.current = zoomBehavior;
    svg.call(zoomBehavior);

    const nodesList = filteredGraph.nodes.map(d => ({ ...d }));
    const edgesList = filteredGraph.edges.map(d => ({ ...d }));

    const simulation = d3.forceSimulation(nodesList as any)
      .force("link", d3.forceLink(edgesList).id((d: any) => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(50));

    // Links inside the zoom group
    const link = g.append("g")
      .selectAll("line")
      .data(edgesList)
      .join("line")
      .attr("stroke", (d: any) => (d.score !== null && d.score !== undefined) ? 'rgba(16,185,129,0.4)' : 'rgba(124,92,252,0.3)')
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", (d: any) => (d.score === null || d.score === undefined) ? '4,3' : null);

    // Node groups inside the zoom group
    const node = g.append("g")
      .selectAll("g")
      .data(nodesList)
      .join("g")
      .attr("cursor", "grab")
      .call(d3.drag<any, any>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        }) as any);

    // Node circles
    node.append("circle")
      .attr("r", (d: any) => {
        if (d.type === 'Company') return 26;
        if (d.type === 'Program') return 24;
        if (d.type === 'Skill') return 18;
        if (d.type === 'Mentor') return 20;
        return 22; // Participant
      })
      .attr("fill", (d: any) => {
        if (d.type === 'Company') return 'rgba(124,92,252,0.2)';
        if (d.type === 'Program') return 'rgba(245,158,11,0.2)';
        if (d.type === 'Mentor') return 'rgba(59,130,246,0.2)';
        if (d.type === 'Skill') return 'rgba(236,72,153,0.2)';
        return 'rgba(16,185,129,0.2)'; // Participant
      })
      .attr("stroke", (d: any) => {
        if (d.type === 'Company') return 'rgba(124,92,252,0.8)';
        if (d.type === 'Program') return 'rgba(245,158,11,0.8)';
        if (d.type === 'Mentor') return 'rgba(59,130,246,0.8)';
        if (d.type === 'Skill') return 'rgba(236,72,153,0.7)';
        return 'rgba(16,185,129,0.7)'; // Participant
      })
      .attr("stroke-width", 2);

    // Emojis
    node.append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", (d: any) => {
        if (d.type === 'Company') return 18;
        if (d.type === 'Program') return 16;
        if (d.type === 'Skill') return 12;
        if (d.type === 'Mentor') return 14;
        return 15;
      })
      .text((d: any) => {
        if (d.type === 'Company') return '🏢';
        if (d.type === 'Program') return '🎓';
        if (d.type === 'Mentor') return '🧑‍💼';
        if (d.type === 'Skill') return '🏷️';
        return '👥'; // Participant
      });

    // Labels
    node.append("text")
      .text((d: any) => d.label.length > 20 ? d.label.slice(0, 18) + "..." : d.label)
      .attr("y", (d: any) => {
        if (d.type === 'Company') return 38;
        if (d.type === 'Program') return 36;
        if (d.type === 'Skill') return 28;
        if (d.type === 'Mentor') return 30;
        return 34;
      })
      .attr("text-anchor", "middle")
      .style("font-size", "10px")
      .style("font-weight", "600")
      .attr("fill", (d: any) => {
        if (d.type === 'Company') return '#c084fc';
        if (d.type === 'Program') return '#fcd34d';
        if (d.type === 'Mentor') return '#93c5fd';
        if (d.type === 'Skill') return '#f472b6';
        return '#6ee7b7';
      });

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [filteredGraph, compact]);

  const handleReset = () => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current)
        .transition()
        .duration(750)
        .call(zoomRef.current.transform, d3.zoomIdentity);
    }
  };

  return (
    <section>
      <div className="mb-4 flex items-end justify-between gap-3">
        <div>
          <h1 className={`${compact ? "text-xl" : "text-2xl"} font-semibold text-ink`}>Relationship Graph</h1>
          <p className="mt-1 text-sm text-slate-500">{graph.nodes.length} nodes, {graph.edges.length} relationships</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <input
              type="text"
              placeholder="Search node..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-10 w-48 rounded-md border border-line bg-white px-3 py-1 text-sm outline-none focus:border-pine"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-ink"
              >
                ×
              </button>
            )}
          </div>
          <button
            type="button"
            onClick={handleReset}
            title="Reset View"
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-line bg-white text-ink hover:bg-panel"
          >
            <Maximize size={18} />
          </button>
          <button
            type="button"
            onClick={load}
            className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium text-ink hover:bg-panel"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>
      
      {error ? <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      
      <div 
        ref={containerRef}
        className="relative overflow-hidden rounded-xl border border-line shadow-2xl"
        style={{ height: compact ? "400px" : "600px" }}
      >
        <svg 
          ref={svgRef} 
          className="h-full w-full cursor-crosshair"
        />
        
        {!filteredGraph.nodes.length && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-500 font-medium bg-[#0f172a]">
            {search ? "No matching relationships found." : "No graph relationships yet."}
          </div>
        )}

        <div className="absolute bottom-4 right-4 flex flex-col gap-2">
          <button 
            onClick={() => {
              if (svgRef.current && zoomRef.current) {
                d3.select(svgRef.current).transition().call(zoomRef.current.scaleBy, 1.3);
              }
            }}
            className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 bg-slate-900/80 backdrop-blur-sm text-white hover:bg-slate-800"
          >
            <ZoomIn size={16} />
          </button>
          <button 
            onClick={() => {
              if (svgRef.current && zoomRef.current) {
                d3.select(svgRef.current).transition().call(zoomRef.current.scaleBy, 0.7);
              }
            }}
            className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 bg-slate-900/80 backdrop-blur-sm text-white hover:bg-slate-800"
          >
            <ZoomOut size={16} />
          </button>
        </div>
      </div>
    </section>
  );
}
