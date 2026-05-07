/**
 * CodeSandbox Component - Secure code execution environment with live output.
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface CodeSandboxProps {
  runId?: string;
  initialCode?: string;
  language?: 'python' | 'javascript' | 'r';
  onExecutionComplete?: (result: any) => void;
}

export const CodeSandbox: React.FC<CodeSandboxProps> = ({
  runId,
  initialCode = '',
  language = 'python',
  onExecutionComplete,
}) => {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [executionTime, setExecutionTime] = useState<number | null>(null);
  const outputRef = useRef<HTMLDivElement>(null);

  // WebSocket connection for real-time output streaming
  const { lastMessage, sendMessage, connected } = useWebSocket(
    runId ? `/ws/agent/${runId}` : null
  );

  // Scroll to bottom of output when new output arrives
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        if (data.type === 'log' || data.type === 'output') {
          setOutput((prev) => [...prev, data.message]);
        } else if (data.type === 'execution_complete') {
          setIsRunning(false);
          setExecutionTime(data.execution_time);
          if (onExecutionComplete) {
            onExecutionComplete(data.result);
          }
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    }
  }, [lastMessage, onExecutionComplete]);

  const handleExecute = async () => {
    setIsRunning(true);
    setOutput([]);
    setExecutionTime(null);

    const startTime = Date.now();

    try {
      // Send code to backend for execution
      const response = await fetch('/api/v1/sandbox/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language,
          run_id: runId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Execution failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.output) {
        setOutput((prev) => [...prev, ...result.output.split('\n')]);
      }

      setExecutionTime(Date.now() - startTime);
      
      if (onExecutionComplete) {
        onExecutionComplete(result);
      }
    } catch (error: any) {
      setOutput((prev) => [...prev, `Error: ${error.message}`]);
    } finally {
      setIsRunning(false);
    }
  };

  const handleClear = () => {
    setOutput([]);
    setExecutionTime(null);
  };

  const exampleCode = {
    python: `# Example Python code
import numpy as np
import matplotlib.pyplot as plt

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

print("Computing sine wave...")
print(f"Generated {len(x)} data points")
print(f"Min value: {y.min():.3f}")
print(f"Max value: {y.max():.3f}")

# Return results
{"result": "success", "mean": float(np.mean(y))}`,
    javascript: `// Example JavaScript code
const data = Array.from({ length: 100 }, (_, i) => Math.sin(i * 0.1));

console.log("Computing sine wave...");
console.log(\`Generated \${data.length} data points\`);
console.log(\`Min value: \${Math.min(...data).toFixed(3)}\`);
console.log(\`Max value: \${Math.max(...data).toFixed(3)}\`);

return { result: "success", mean: data.reduce((a, b) => a + b, 0) / data.length };`,
    r: `# Example R code
x <- seq(0, 10, length.out = 100)
y <- sin(x)

cat("Computing sine wave...\\n")
cat(sprintf("Generated %d data points\\n", length(x)))
cat(sprintf("Min value: %.3f\\n", min(y)))
cat(sprintf("Max value: %.3f\\n", max(y)))

list(result = "success", mean = mean(y))`,
  };

  const loadExample = () => {
    setCode(exampleCode[language]);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-gray-200">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-3">
          <select
            value={language}
            onChange={(e) => setCode(exampleCode[e.target.value as keyof typeof exampleCode])}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="r">R</option>
          </select>
          
          <button
            onClick={loadExample}
            className="px-3 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Load Example
          </button>
        </div>

        <div className="flex items-center gap-2">
          {executionTime && (
            <span className="text-xs text-gray-500">
              Execution time: {executionTime}ms
            </span>
          )}
          
          <button
            onClick={handleClear}
            disabled={isRunning}
            className="px-3 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            Clear Output
          </button>
          
          <button
            onClick={handleExecute}
            disabled={isRunning || !connected}
            className="px-4 py-1.5 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? 'Running...' : 'Execute'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Code Editor */}
        <div className="flex-1 flex flex-col border-r border-gray-200">
          <div className="px-3 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b border-gray-200">
            Code Editor
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 p-4 font-mono text-sm resize-none focus:outline-none"
            placeholder="Enter your code here..."
            spellCheck={false}
          />
        </div>

        {/* Output Console */}
        <div className="flex-1 flex flex-col bg-gray-900">
          <div className="px-3 py-2 text-xs font-medium text-gray-400 bg-gray-800 border-b border-gray-700">
            Console Output
          </div>
          <div
            ref={outputRef}
            className="flex-1 p-4 overflow-auto font-mono text-sm text-green-400"
          >
            {output.length === 0 ? (
              <div className="text-gray-500 italic">
                Output will appear here after execution...
              </div>
            ) : (
              output.map((line, index) => (
                <div key={index} className="whitespace-pre-wrap">
                  {line}
                </div>
              ))
            )}
            
            {isRunning && (
              <div className="mt-2 text-blue-400 animate-pulse">Executing...</div>
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between px-3 py-2 text-xs border-t border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              connected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-gray-600">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <div className="text-gray-500">
          Language: {language.toUpperCase()} | Lines: {code.split('\n').length}
        </div>
      </div>
    </div>
  );
};

export default CodeSandbox;
