'use client';

import { BrainCircuit, TrendingUp, Clock, CheckCircle } from 'lucide-react';

const stats = [
  {
    name: 'Active Agents',
    value: '12',
    change: '+3 this week',
    icon: BrainCircuit,
    trend: 'positive'
  },
  {
    name: 'Research Runs',
    value: '847',
    change: '+12% from last month',
    icon: TrendingUp,
    trend: 'positive'
  },
  {
    name: 'Avg. Completion Time',
    value: '4.2 min',
    change: '-0.8 min faster',
    icon: Clock,
    trend: 'positive'
  },
  {
    name: 'Success Rate',
    value: '94.3%',
    change: '+2.1% improvement',
    icon: CheckCircle,
    trend: 'positive'
  },
];

const recentRuns = [
  {
    id: 1,
    name: 'Literature Review: CRISPR Applications',
    agent: 'Literature Review Agent',
    status: 'completed',
    duration: '3m 24s',
    tokens: 45230,
    timestamp: '2 minutes ago'
  },
  {
    id: 2,
    name: 'Hypothesis Generation: Protein Folding',
    agent: 'Hypothesis Agent',
    status: 'running',
    duration: '1m 12s',
    tokens: 12450,
    timestamp: '5 minutes ago'
  },
  {
    id: 3,
    name: 'Experimental Design: Cell Culture',
    agent: 'Experimental Design Agent',
    status: 'completed',
    duration: '5m 47s',
    tokens: 67890,
    timestamp: '1 hour ago'
  },
  {
    id: 4,
    name: 'Data Analysis: Genomic Sequencing',
    agent: 'Analysis Agent',
    status: 'failed',
    duration: '0m 45s',
    tokens: 8920,
    timestamp: '2 hours ago'
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-dark-900">Dashboard</h1>
        <p className="mt-1 text-sm text-dark-500">
          Overview of your research activities and agent performance
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm border border-dark-200"
          >
            <dt>
              <div className="absolute rounded-md bg-primary-500 p-3">
                <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <p className="ml-16 truncate text-sm font-medium text-dark-500">{stat.name}</p>
            </dt>
            <dd className="ml-16 flex items-baseline">
              <p className="text-2xl font-semibold text-dark-900">{stat.value}</p>
              <p className={`ml-2 flex items-baseline text-sm font-semibold ${
                stat.trend === 'positive' ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.change}
              </p>
            </dd>
          </div>
        ))}
      </div>

      {/* Recent Runs Table */}
      <div className="rounded-xl bg-white shadow-sm border border-dark-200">
        <div className="px-6 py-4 border-b border-dark-200">
          <h2 className="text-lg font-semibold text-dark-900">Recent Agent Runs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-dark-200">
            <thead className="bg-dark-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">
                  Run Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-dark-200">
              {recentRuns.map((run) => (
                <tr key={run.id} className="hover:bg-dark-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-dark-900">{run.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-dark-500">{run.agent}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      run.status === 'completed' 
                        ? 'bg-green-100 text-green-800'
                        : run.status === 'running'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-500">
                    {run.duration}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-500">
                    {run.tokens.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-500">
                    {run.timestamp}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 p-6 text-white">
          <h3 className="text-lg font-semibold">Start New Research</h3>
          <p className="mt-2 text-sm text-primary-100">
            Launch an autonomous agent to explore your research question
          </p>
          <button className="mt-4 inline-flex items-center px-4 py-2 bg-white text-primary-600 rounded-lg text-sm font-medium hover:bg-primary-50 transition-colors">
            Create Agent Run
          </button>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 p-6 text-white">
          <h3 className="text-lg font-semibold">Upload Documents</h3>
          <p className="mt-2 text-sm text-purple-100">
            Add research papers, datasets, or notes to your knowledge base
          </p>
          <button className="mt-4 inline-flex items-center px-4 py-2 bg-white text-purple-600 rounded-lg text-sm font-medium hover:bg-purple-50 transition-colors">
            Upload Files
          </button>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 p-6 text-white">
          <h3 className="text-lg font-semibold">View Knowledge Graph</h3>
          <p className="mt-2 text-sm text-orange-100">
            Explore connections between concepts in your research domain
          </p>
          <button className="mt-4 inline-flex items-center px-4 py-2 bg-white text-orange-600 rounded-lg text-sm font-medium hover:bg-orange-50 transition-colors">
            Open Graph
          </button>
        </div>
      </div>
    </div>
  );
}
