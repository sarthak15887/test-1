/**
 * KnowledgeGraph Component - Interactive visualization of research knowledge graph.
 * Uses D3.js for rendering nodes and relationships.
 */
'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';

export interface GraphNode {
  id: string;
  label: string;
  type: 'entity' | 'concept' | 'method' | 'result';
  properties?: Record<string, any>;
}

export interface GraphLink {
  source: string;
  target: string;
  relationship: string;
  weight?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface KnowledgeGraphProps {
  data: GraphData;
  width?: number;
  height?: number;
  onNodeClick?: (node: GraphNode) => void;
  onLinkClick?: (link: GraphLink) => void;
  enableZoom?: boolean;
  enableDrag?: boolean;
}

const NODE_COLORS: Record<string, string> = {
  entity: '#3b82f6',
  concept: '#8b5cf6',
  method: '#10b981',
  result: '#f59e0b',
};

const NODE_RADIUS: Record<string, number> = {
  entity: 20,
  concept: 15,
  method: 12,
  result: 18,
};

export const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({
  data,
  width = 800,
  height = 600,
  onNodeClick,
  onLinkClick,
  enableZoom = true,
  enableDrag = true,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; content: string } | null>(null);

  const drawGraph = useCallback(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.1, 4]).on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

    if (enableZoom) {
      svg.call(zoom as any);
    }

    // Create main group
    const g = svg.append('g');

    // Create arrow markers for links
    svg.append('defs').selectAll('marker')
      .data(['end'])
      .enter().append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 28)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('fill', '#9ca3af')
      .attr('d', 'M0,-5L10,0L0,5');

    // Initialize force simulation
    const simulation = d3.forceSimulation<d3.SimulationNodeDatum>(data.nodes as any)
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('link', d3.forceLink(data.links as any).id((d: any) => d.id).distance(150))
      .force('collide', d3.forceCollide().radius(30));

    // Draw links
    const links = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', '#9ca3af')
      .attr('stroke-width', (d) => Math.sqrt(d.weight || 1))
      .attr('marker-end', 'url(#arrowhead)')
      .on('click', (event, d) => {
        if (onLinkClick) onLinkClick(d);
      });

    // Add link labels
    const linkLabels = g.append('g')
      .attr('class', 'link-labels')
      .selectAll('text')
      .data(data.links)
      .enter().append('text')
      .attr('font-size', '10px')
      .attr('fill', '#6b7280')
      .attr('text-anchor', 'middle')
      .text((d) => d.relationship);

    // Draw nodes
    const nodes = g.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', (d) => NODE_RADIUS[d.type] || 15)
      .attr('fill', (d) => NODE_COLORS[d.type] || '#3b82f6')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .attr('cursor', 'pointer')
      .on('click', (event, d) => {
        setSelectedNode(d);
        if (onNodeClick) onNodeClick(d);
      })
      .on('mouseover', (event, d) => {
        setTooltip({
          x: event.pageX,
          y: event.pageY,
          content: `${d.label} (${d.type})`,
        });
      })
      .on('mouseout', () => {
        setTooltip(null);
      })
      .call(
        enableDrag
          ? (drag as any)
          : (selection: any) => selection.on('drag', null)
      );

    // Add node labels
    const nodeLabels = g.append('g')
      .attr('class', 'node-labels')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .attr('dx', (d) => (NODE_RADIUS[d.type] || 15) + 5)
      .attr('dy', 4)
      .attr('font-size', '12px')
      .attr('fill', '#374151')
      .text((d) => d.label);

    // Drag behavior
    const drag = d3.drag<SVGCircleElement, d3.SimulationNodeDatum>()
      .on('start', (event) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      })
      .on('drag', (event) => {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      })
      .on('end', (event) => {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      });

    // Update positions on tick
    simulation.on('tick', () => {
      links
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      linkLabels
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

      nodes
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      nodeLabels
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });
  }, [data, width, height, enableZoom, enableDrag, onNodeClick, onLinkClick]);

  useEffect(() => {
    drawGraph();
  }, [drawGraph]);

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="border border-gray-200 rounded-lg bg-white"
      />
      
      {/* Tooltip */}
      {tooltip && (
        <div
          className="fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded shadow-lg pointer-events-none"
          style={{ left: tooltip.x + 10, top: tooltip.y + 10 }}
        >
          {tooltip.content}
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white bg-opacity-90 p-3 rounded-lg shadow-md">
        <h4 className="text-sm font-semibold mb-2">Node Types</h4>
        <div className="space-y-1">
          {Object.entries(NODE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs capitalize">{type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Node Info */}
      {selectedNode && (
        <div className="absolute top-4 right-4 bg-white bg-opacity-95 p-4 rounded-lg shadow-lg max-w-xs">
          <h3 className="font-semibold text-lg mb-2">{selectedNode.label}</h3>
          <p className="text-sm text-gray-600 mb-2">Type: {selectedNode.type}</p>
          {selectedNode.properties && (
            <div className="text-xs space-y-1">
              {Object.entries(selectedNode.properties).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-gray-500">{key}:</span>
                  <span className="font-medium">{String(value)}</span>
                </div>
              ))}
            </div>
          )}
          <button
            onClick={() => setSelectedNode(null)}
            className="mt-3 text-xs text-blue-600 hover:underline"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
};

export default KnowledgeGraph;
