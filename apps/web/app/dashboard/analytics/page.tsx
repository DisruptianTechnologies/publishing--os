'use client';

import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Cpu,
  Clock,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Activity,
  FileText,
  CheckCircle,
} from 'lucide-react';

const AGENT_COST_DATA = [
  { agent: 'Research Analyst', model: 'gemini-2.0-flash', calls: 38, tokens: '142k', cost_usd: 0.43, pct: 15 },
  { agent: 'Strategy Architect', model: 'gemini-1.5-pro', calls: 19, tokens: '86k', cost_usd: 0.65, pct: 22 },
  { agent: 'Master Outliner', model: 'gemini-1.5-pro', calls: 14, tokens: '64k', cost_usd: 0.48, pct: 16 },
  { agent: 'Chapter Ghostwriter', model: 'gemini-1.5-pro', calls: 28, tokens: '380k', cost_usd: 1.14, pct: 39 },
  { agent: 'Developmental Editor', model: 'gemini-1.5-flash', calls: 24, tokens: '110k', cost_usd: 0.18, pct: 6 },
  { agent: 'Formatting Specialist', model: 'gemini-2.0-flash', calls: 8, tokens: '22k', cost_usd: 0.06, pct: 2 },
];

const PIPELINE_VELOCITY = [
  { stage: '1. Market Research', avgDuration: '1.4 min', successRate: '100%', bottleneck: false },
  { stage: '2. Product Strategy', avgDuration: '2.1 min', successRate: '98%', bottleneck: false },
  { stage: '3. Outlining', avgDuration: '3.5 min', successRate: '95%', bottleneck: false },
  { stage: '4. Chapter Drafting', avgDuration: '12.8 min', successRate: '96%', bottleneck: true },
  { stage: '5. Dev Editorial QA', avgDuration: '4.2 min', successRate: '92%', bottleneck: false },
  { stage: '6. KDP Formatting', avgDuration: '1.8 min', successRate: '99%', bottleneck: false },
];

export default function AnalyticsDashboardPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | 'all'>('30d');

  const totalCost = AGENT_COST_DATA.reduce((acc, cur) => acc + cur.cost_usd, 0);

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Observability & Cost Tower
            </span>
            <span className="text-xs text-slate-500">Live Agent Usage Telemetry</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white font-[Outfit]">
            Analytics & Operations
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Granular token budgeting, real-time agent cost telemetry, pipeline velocity benchmarks, and tenant usage metrics.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-900/60 p-1 rounded-xl border border-white/10 text-xs">
          {(['7d', '30d', 'all'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {range.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Top 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Total AI Spend</span>
            <DollarSign size={16} className="text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">
            ${totalCost.toFixed(2)}
          </div>
          <div className="flex items-center gap-1 text-[11px] text-emerald-400 mt-1 font-medium">
            <ArrowDownRight size={13} />
            <span>34% lower than OpenAI standard</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Total Tokens Consumed</span>
            <Cpu size={16} className="text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">804,290</div>
          <div className="text-[11px] text-blue-400/80 mt-1">Across 131 agent tasks</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Avg. Pipeline Velocity</span>
            <Clock size={16} className="text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">25.8 min</div>
          <div className="flex items-center gap-1 text-[11px] text-purple-400 mt-1 font-medium">
            <ArrowUpRight size={13} />
            <span>Idea to formatted publication</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Human Approval Gate Pass</span>
            <CheckCircle size={16} className="text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">94.2%</div>
          <div className="text-[11px] text-cyan-400/80 mt-1">5.8% rejected or revised</div>
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Cost Breakdown */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <DollarSign size={18} className="text-emerald-400" />
              <h2 className="text-base font-semibold text-white font-[Outfit]">
                Agent Cost & Consumption Breakdown
              </h2>
            </div>
            <span className="text-xs text-slate-500">By Specialist Agent</span>
          </div>

          <div className="space-y-3 pt-2">
            {AGENT_COST_DATA.map((row) => (
              <div key={row.agent} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <div>
                    <span className="font-semibold text-white">{row.agent}</span>
                    <span className="text-slate-500 ml-2 font-mono text-[10px]">({row.model})</span>
                  </div>
                  <div className="text-right font-mono">
                    <span className="text-emerald-400 font-semibold">${row.cost_usd.toFixed(2)}</span>
                    <span className="text-slate-500 text-[10px] ml-1.5">({row.tokens})</span>
                  </div>
                </div>
                <div className="w-full h-1.5 rounded-full bg-white/5 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500"
                    style={{ width: `${row.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline Velocity & Bottlenecks */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity size={18} className="text-blue-400" />
              <h2 className="text-base font-semibold text-white font-[Outfit]">
                Pipeline Stage Velocity & QA Gates
              </h2>
            </div>
            <span className="text-xs text-slate-500">Live Benchmarks</span>
          </div>

          <div className="space-y-2.5 pt-2">
            {PIPELINE_VELOCITY.map((stage) => (
              <div
                key={stage.stage}
                className="flex items-center justify-between p-3 rounded-xl bg-slate-950/40 border border-white/5 text-xs"
              >
                <div>
                  <div className="font-medium text-slate-200">{stage.stage}</div>
                  <div className="text-[11px] text-slate-500">Success Rate: {stage.successRate}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-slate-300 font-medium">{stage.avgDuration}</span>
                  {stage.bottleneck ? (
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      High Load
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Optimal
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
