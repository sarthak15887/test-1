'use client';

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { ForceGraph2D } from 'react-force-graph';

interface Node {
  id: string;
  label: string;
  properties: Record<string, any>;
}

interface GraphData {
  nodes: Node[];
  links: Array<{ source: string; target: string; type: string }>;
}

export default function KnowledgeExplorerPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const fgRef = useRef<any>();

  useEffect(() => {
    fetchStats();
    searchGraph('');
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/knowledge/stats', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const searchGraph = async (query: string) => {
    if (!query) {
      // Load initial graph data
      setGraphData({ nodes: [], links: [] });
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        '/api/v1/knowledge/search',
        { query, limit: 50 },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const nodes = response.data.results.map((result: any) => ({
        id: result.id,
        label: result.label || result.properties?.name || result.id,
        properties: result.properties || {},
        val: Math.sqrt(result.score || 1) * 5
      }));

      setGraphData({ nodes, links: [] });
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = async (node: Node) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `/api/v1/knowledge/entities/${node.id}?depth=2`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const nodes = response.data.nodes.map((n: any) => ({
        id: n.id,
        label: n.label || n.properties?.name || n.id,
        properties: n.properties || {}
      }));

      setGraphData({ nodes, links: [] });
      
      if (fgRef.current) {
        fgRef.current.centerAt(
          nodes.find((n: any) => n.id === node.id)?.x || 0,
          nodes.find((n: any) => n.id === node.id)?.y || 0,
          1000
        );
        fgRef.current.zoom(1.5, 1000);
      }
    } catch (error) {
      console.error('Failed to load entity:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Knowledge Explorer</h1>
          <p className="mt-2 text-sm text-gray-500">
            Explore and visualize the research knowledge graph
          </p>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.node_count || 0}</div>
                <div className="text-xs text-gray-500">Entities</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.relationship_count || 0}</div>
                <div className="text-xs text-gray-500">Relationships</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {(stats.label_counts || []).length}
                </div>
                <div className="text-xs text-gray-500">Entity Types</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {(stats.relationship_types || []).length}
                </div>
                <div className="text-xs text-gray-500">Relation Types</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex gap-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchGraph(searchQuery)}
              placeholder="Search entities..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => searchGraph(searchQuery)}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
      </div>

      {/* Graph Visualization */}
      <main className="h-[calc(100vh-280px)]">
        {graphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No results</h3>
              <p className="mt-1 text-sm text-gray-500">Search for entities to explore the knowledge graph.</p>
            </div>
          </div>
        ) : (
          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            nodeLabel={(node: any) => `${node.label}`}
            nodeColor={() => '#3b82f6'}
            nodeRelSize={6}
            linkColor={() => '#9ca3af'}
            linkWidth={1}
            onNodeClick={handleNodeClick}
            backgroundColor="#f9fafb"
            showNavInfo={false}
          />
        )}
      </main>
    </div>
  );
}
