import React from 'react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-primary-900">
      {/* Navigation */}
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="h-10 w-10 bg-primary-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">N</span>
            </div>
            <span className="text-white text-xl font-bold">Nexus Research OS</span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-dark-300 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-dark-300 hover:text-white transition-colors">How It Works</a>
            <a href="#pricing" className="text-dark-300 hover:text-white transition-colors">Pricing</a>
            <button className="text-white hover:text-primary-300 transition-colors">Sign In</button>
            <button className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg font-medium transition-colors">
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="container mx-auto px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight">
            Autonomous AI for{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-purple-400">
              Scientific Discovery
            </span>
          </h1>
          <p className="mt-6 text-xl text-dark-300 max-w-2xl mx-auto">
            Empower your research with intelligent agents that automate literature reviews, 
            generate hypotheses, design experiments, and analyze data across all scientific domains.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button className="w-full sm:w-auto bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors shadow-lg shadow-primary-500/25">
              Start Researching Free
            </button>
            <button className="w-full sm:w-auto bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors backdrop-blur-sm">
              Watch Demo
            </button>
          </div>
          
          {/* Stats */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <div className="text-3xl font-bold text-white">10,000+</div>
              <div className="mt-1 text-dark-400">Research Runs</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">500+</div>
              <div className="mt-1 text-dark-400">Research Labs</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">94%</div>
              <div className="mt-1 text-dark-400">Success Rate</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">10x</div>
              <div className="mt-1 text-dark-400">Faster Research</div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <section id="features" className="mt-32">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              Everything You Need for Modern Research
            </h2>
            <p className="mt-4 text-xl text-dark-400">
              Powerful AI tools designed by researchers, for researchers
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
              <div className="h-12 w-12 bg-primary-500/20 rounded-xl flex items-center justify-center mb-6">
                <svg className="h-6 w-6 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Autonomous Agents</h3>
              <p className="text-dark-400">
                Multi-agent systems that plan, execute, and verify research tasks with minimal human intervention.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
              <div className="h-12 w-12 bg-purple-500/20 rounded-xl flex items-center justify-center mb-6">
                <svg className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Knowledge Graphs</h3>
              <p className="text-dark-400">
                Build interconnected knowledge bases that reveal hidden patterns and relationships in your research.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
              <div className="h-12 w-12 bg-green-500/20 rounded-xl flex items-center justify-center mb-6">
                <svg className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Secure Execution</h3>
              <p className="text-dark-400">
                Run code and simulations in isolated environments with enterprise-grade security and compliance.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-32">
        <div className="container mx-auto px-6 py-12">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="h-8 w-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">N</span>
              </div>
              <span className="text-white font-semibold">Nexus Research OS</span>
            </div>
            <p className="text-dark-400 text-sm">
              © 2024 Nexus Research. Built for the future of scientific discovery.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
