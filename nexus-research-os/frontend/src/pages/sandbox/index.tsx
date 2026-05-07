'use client';

import React, { useState } from 'react';
import axios from 'axios';

interface ExecutionResult {
  success: boolean;
  output: string;
  error: string;
  exit_code: number;
  execution_time: number;
}

export default function SandboxPage() {
  const [code, setCode] = useState(`# Write your Python code here
import numpy as np

# Example: Calculate mean of random array
data = np.random.randn(100)
mean_value = np.mean(data)
print(f"Mean of 100 random numbers: {mean_value:.4f}")

# Example: Simple calculation
result = sum(range(1, 101))
print(f"Sum of 1 to 100: {result}")
`);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [packages, setPackages] = useState('numpy,pandas,matplotlib');

  const handleExecute = async () => {
    setLoading(true);
    setResult(null);

    try {
      const token = localStorage.getItem('token');
      const packageList = packages.split(',').map(p => p.trim()).filter(p => p);
      
      const response = await axios.post(
        '/api/v1/sandbox/execute',
        {
          code,
          language: 'python',
          timeout: 30,
          packages: packageList
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setResult(response.data);
    } catch (error: any) {
      setResult({
        success: false,
        output: '',
        error: error.response?.data?.detail || 'Execution failed',
        exit_code: -1,
        execution_time: 0
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Code Sandbox</h1>
          <p className="mt-2 text-sm text-gray-500">
            Execute Python code in a secure, isolated environment
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Code Editor */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-medium text-gray-900">Code Editor</h2>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={packages}
                    onChange={(e) => setPackages(e.target.value)}
                    placeholder="numpy,pandas,..."
                    className="px-3 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
            <div className="p-4">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-96 font-mono text-sm bg-gray-50 border border-gray-300 rounded-lg p-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                spellCheck={false}
              />
              <button
                onClick={handleExecute}
                disabled={loading}
                className="mt-4 w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Executing...' : '▶ Execute Code'}
              </button>
            </div>
          </div>

          {/* Output */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h2 className="text-lg font-medium text-gray-900">Output</h2>
            </div>
            <div className="p-4">
              {!result && !loading && (
                <div className="text-center text-gray-500 py-20">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p className="mt-2">Execute code to see results</p>
                </div>
              )}

              {loading && (
                <div className="flex items-center justify-center py-20">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
                </div>
              )}

              {result && (
                <div className="space-y-4">
                  {/* Status */}
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {result.success ? '✓ Success' : '✗ Failed'}
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-gray-500">Exit Code</div>
                      <div className="font-mono">{result.exit_code}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-gray-500">Execution Time</div>
                      <div className="font-mono">{result.execution_time.toFixed(3)}s</div>
                    </div>
                  </div>

                  {/* Output */}
                  {result.output && (
                    <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto max-h-64">
                      <div className="text-xs text-gray-500 mb-2">STDOUT</div>
                      <pre className="font-mono text-sm whitespace-pre-wrap">{result.output}</pre>
                    </div>
                  )}

                  {/* Error */}
                  {result.error && (
                    <div className="bg-red-50 text-red-800 p-4 rounded-lg overflow-auto max-h-64">
                      <div className="text-xs text-red-600 mb-2">STDERR</div>
                      <pre className="font-mono text-sm whitespace-pre-wrap">{result.error}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Security Information</h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Code executes in isolated Docker containers</li>
                  <li>No network access allowed</li>
                  <li>Memory limited to 512MB</li>
                  <li>Execution timeout: 30 seconds</li>
                  <li>File system is read-only except for /tmp</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
