import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export default function GraphView({ data, width = 800, height = 600 }) {
  const svgRef = useRef(null)

  useEffect(() => {
    if (!data || !svgRef.current) return

    const { nodes, edges } = data
    if (!nodes?.length) return

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove()

    const svg = d3.select(svgRef.current)
      .attr('width', '100%')
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)

    // Defs: arrowhead marker + radial gradient
    const defs = svg.append('defs')

    defs.append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 28)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', 'rgba(124,92,252,0.6)')

    // Background
    svg.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'transparent')

    const nodesMap = new Map(nodes.map(n => [n.id, { ...n }]))

    const links = edges.map(e => ({
      source: e.source,
      target: e.target,
      score: e.score,
      status: e.status,
    })).filter(e => nodesMap.has(e.source) && nodesMap.has(e.target))

    const nodesList = [...nodesMap.values()]

    // Simulation
    const simulation = d3.forceSimulation(nodesList)
      .force('link', d3.forceLink(links).id(d => d.id).distance(160).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(50))

    // Main group (zoomable)
    const g = svg.append('g')

    svg.call(
      d3.zoom()
        .scaleExtent([0.3, 3])
        .on('zoom', (event) => g.attr('transform', event.transform))
    )

    // Edges
    const link = g.append('g').selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', d => d.status === 'accepted' ? 'rgba(16,185,129,0.6)' : d.status === 'rejected' ? 'rgba(239,68,68,0.3)' : 'rgba(124,92,252,0.4)')
      .attr('stroke-width', d => 1 + d.score * 3)
      .attr('stroke-dasharray', d => d.status === 'pending' ? '4,3' : null)
      .attr('marker-end', 'url(#arrow)')

    // Edge score labels
    const linkLabel = g.append('g').selectAll('text')
      .data(links)
      .join('text')
      .attr('text-anchor', 'middle')
      .attr('font-size', 10)
      .attr('fill', 'rgba(192,132,252,0.8)')
      .text(d => `${Math.round(d.score * 100)}%`)

    // Node groups
    const node = g.append('g').selectAll('g')
      .data(nodesList)
      .join('g')
      .attr('cursor', 'pointer')
      .call(
        d3.drag()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x; d.fy = d.y
          })
          .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null; d.fy = null
          })
      )

    // Node circles
    node.append('circle')
      .attr('r', d => d.type === 'startup' ? 26 : 22)
      .attr('fill', d => d.type === 'startup' ? 'rgba(124,92,252,0.25)' : 'rgba(16,185,129,0.2)')
      .attr('stroke', d => d.type === 'startup' ? 'rgba(124,92,252,0.8)' : 'rgba(16,185,129,0.7)')
      .attr('stroke-width', 2)

    // Node emoji
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', d => d.type === 'startup' ? 18 : 15)
      .text(d => d.type === 'startup' ? '🚀' : '🧑‍💼')

    // Node label
    node.append('text')
      .attr('y', d => d.type === 'startup' ? 38 : 34)
      .attr('text-anchor', 'middle')
      .attr('font-size', 11)
      .attr('font-weight', '600')
      .attr('fill', d => d.type === 'startup' ? '#c084fc' : '#6ee7b7')
      .text(d => d.label.length > 14 ? d.label.slice(0, 13) + '…' : d.label)

    // Tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      linkLabel
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2 - 6)

      node.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    return () => simulation.stop()
  }, [data, width, height])

  return (
    <div className="w-full rounded-2xl overflow-hidden border border-white/10" style={{ background: 'rgba(5,5,16,0.6)' }}>
      <svg ref={svgRef} className="w-full" style={{ minHeight: `${height}px` }} />
    </div>
  )
}
