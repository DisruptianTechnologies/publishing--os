'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  BookOpen,
  Cpu,
  Sparkles,
  Shield,
  Zap,
  Search,
  PenTool,
  BarChart3,
  Globe,
  CheckCircle,
  Star,
  Users,
  FileText,
  Target,
  TrendingUp,
  Lock,
  Brain,
  Layers,
  Store,
  Mail,
  HeartHandshake,
  Compass,
  AlertTriangle,
  Radio,
  Sliders,
  ChevronRight,
  Fingerprint,
  RefreshCw,
  Eye,
  Send,
} from 'lucide-react';

// --- PLATFORM ECOSYSTEM PILLARS ---
type SystemPillar = 'publishing' | 'marketplace' | 'audience';

// --- PIPELINE STAGES ---
const PIPELINE_STAGES = [
  { id: 'research', label: '1. Research', agent: 'Research Analyst', color: '#3b82f6', desc: 'Market demand & gap scoring' },
  { id: 'strategy', label: '2. Strategy', agent: 'Strategy Architect', color: '#6366f1', desc: 'USP & category positioning' },
  { id: 'outline', label: '3. Outline', agent: 'Master Outliner', color: '#8b5cf6', desc: 'Hierarchical chapter blueprint' },
  { id: 'writing', label: '4. Drafting', agent: 'Chapter Writer', color: '#a855f7', desc: 'Active voice, no AI tropes' },
  { id: 'editing', label: '5. Edit QA', agent: 'Dev Editor', color: '#d946ef', desc: 'Readability & structural critique' },
  { id: 'formatting', label: '6. Format', agent: 'Formatting Specialist', color: '#ec4899', desc: 'EPUB / PDF / Paperback ready' },
  { id: 'metadata', label: '7. Metadata', agent: 'SEO Strategist', color: '#f97316', desc: '7 KDP keywords & categories' },
  { id: 'compliance', label: '8. Compliance', agent: 'Compliance Guard', color: '#eab308', desc: 'Copyright & policy gating' },
  { id: 'marketplace', label: '9. Publish', agent: 'Marketplace Studio', color: '#22c55e', desc: 'Preflight & KDP/Etsy staging' },
  { id: 'audience', label: '10. Audience', agent: 'AudienceOS', color: '#06b6d4', desc: 'Consent-based reader growth' },
];

// --- 8 SPECIALIST AGENTS ---
const AGENTS = [
  {
    name: 'Research Analyst',
    role: 'Market Intelligence',
    output: 'Opportunity Score: 8.4/10',
    color: '#3b82f6',
    icon: Search,
    desc: 'Extracts real demand signals, competitor ranking weakness, and unmet reader pain points without hallucinations.',
  },
  {
    name: 'Strategy Architect',
    role: 'Positioning & Pricing',
    output: 'Pricing: $4.99 · 70% Royalty',
    color: '#6366f1',
    icon: Target,
    desc: 'Calculates optimal price bounds, customer reading level, series potential, and commercial launch roadmaps.',
  },
  {
    name: 'Master Outliner',
    role: 'Hierarchical Architecture',
    output: '12 Chapters · 45,000 Words',
    color: '#8b5cf6',
    icon: FileText,
    desc: 'Scaffolds hook-driven chapters, research placeholders, and clear reader promises for maximum retention.',
  },
  {
    name: 'Chapter Ghostwriter',
    role: 'Content Generation',
    output: 'Burstiness: High · 80% Active',
    color: '#a855f7',
    icon: PenTool,
    desc: 'Writes punchy, trope-free prose with alternating rhythm, real historical analogies, and zero filler padding.',
  },
  {
    name: 'Developmental Editor',
    role: 'Editorial QA',
    output: 'Flesch Score: 68 · 0 Blockers',
    color: '#d946ef',
    icon: Brain,
    desc: 'Issues numbered diagnostic critique notes, readability evaluations, and strict publication-readiness checks.',
  },
  {
    name: 'Formatting Engineer',
    role: 'Interior & Cover Styling',
    output: 'EPUB 3.2 · PDF 6x9 Ready',
    color: '#ec4899',
    icon: BookOpen,
    desc: 'Generates clean typographic layouts, automatic tables of contents, margin padding, and preflight package validation.',
  },
  {
    name: 'Metadata & SEO Specialist',
    role: 'A9 Algorithm Ranking',
    output: '7 Verified Keywords · 2 Paths',
    color: '#f97316',
    icon: Globe,
    desc: 'Formats KDP backend keyword tags, BISAC nodes, and compelling HTML descriptions with high conversion hooks.',
  },
  {
    name: 'Compliance Guard',
    role: 'Policy & Legal Safety',
    output: 'Status: Passed · 0 Infringements',
    color: '#eab308',
    icon: Shield,
    desc: 'Automates trademark screening, copyright safety audits, and mandatory AI-assistance disclosure records.',
  },
];

// --- PRICING TIERS ---
const PLANS = [
  {
    name: 'Free Starter',
    price: '$0',
    period: 'forever',
    desc: 'Explore the platform and test single book research',
    features: ['1 active project', 'Market Research Agent', 'Basic 10-chapter outline', '10,000 monthly token budget', 'Community support'],
    cta: 'Start Free',
    popular: false,
  },
  {
    name: 'Author Pro',
    price: '$29',
    period: 'per month',
    desc: 'For solo fiction and non-fiction creators',
    features: [
      '5 active projects',
      'All 8 AI Specialist Agents',
      'Human Approval Control Tower',
      'Marketplace Studio (KDP & Etsy)',
      '500,000 monthly token budget',
      'EPUB & PDF Interior Export',
      'Email support',
    ],
    cta: 'Start Creating',
    popular: true,
  },
  {
    name: 'Publishing Agency',
    price: '$79',
    period: 'per month',
    desc: 'For publishers, digital stores & authority brands',
    features: [
      '25 active projects',
      'AudienceOS Community & Nurture Engine',
      'First-Class Consent & Opt-in Records',
      'Priority Agent Job Worker Queue',
      '2,500,000 monthly token budget',
      'Custom Autonomy Levels & Kill Switches',
      'Dedicated Slack & Priority SLA',
    ],
    cta: 'Launch Agency Suite',
    popular: false,
  },
];

export default function LandingPage() {
  const [activePillar, setActivePillar] = useState<SystemPillar>('publishing');

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 overflow-x-hidden selection:bg-blue-500/30 selection:text-white">
      {/* Dynamic Background Atmosphere */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[1000px] h-[550px] bg-gradient-to-b from-blue-600/15 via-indigo-600/10 to-transparent blur-[120px] rounded-full" />
        <div className="absolute top-[35%] left-[-10%] w-[600px] h-[600px] bg-purple-600/10 blur-[140px] rounded-full" />
        <div className="absolute top-[60%] right-[-10%] w-[650px] h-[650px] bg-cyan-600/10 blur-[150px] rounded-full" />
        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              'linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)',
            backgroundSize: '48px 48px',
          }}
        />
      </div>

      {/* TOP NOTIFICATION BAR */}
      <div className="relative z-50 bg-gradient-to-r from-blue-900/40 via-indigo-900/40 to-slate-900/40 border-b border-white/5 py-2 px-4 text-center text-xs font-medium text-blue-200/90 flex items-center justify-center gap-2">
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span>Kindlepreneur 2.0 Live Operating System: 8 Agents Online · Policy Engine Active · Multi-Tenant Isolated</span>
      </div>

      {/* NAVIGATION BAR */}
      <header className="sticky top-0 z-50 backdrop-blur-2xl bg-[#020617]/75 border-b border-white/10 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/25 border border-white/20">
              <Layers className="text-white w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  Kindlepreneur 2.0
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  OS
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Publishing & Audience Operating System</p>
            </div>
          </div>

          <nav className="hidden lg:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#matrix" className="hover:text-white transition-colors flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-blue-400" /> Platform Matrix
            </a>
            <a href="#pipeline" className="hover:text-white transition-colors flex items-center gap-1.5">
              <Compass className="w-4 h-4 text-indigo-400" /> 10-Stage Pipeline
            </a>
            <a href="#marketplace" className="hover:text-white transition-colors flex items-center gap-1.5">
              <Store className="w-4 h-4 text-emerald-400" /> Marketplace Studio
            </a>
            <a href="#audience" className="hover:text-white transition-colors flex items-center gap-1.5">
              <HeartHandshake className="w-4 h-4 text-cyan-400" /> AudienceOS
            </a>
            <a href="#control" className="hover:text-white transition-colors flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-amber-400" /> Policy Control
            </a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
          </nav>

          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="hidden sm:inline-flex text-xs font-semibold uppercase tracking-wider text-slate-300 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-white/5"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:opacity-95 shadow-lg shadow-indigo-500/30 border border-white/20 transition-all hover:scale-105 active:scale-95"
            >
              Launch Platform
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* HERO SECTION WITH ANTIGRAVITY SPATIAL DEPTH */}
      <section className="relative pt-20 pb-28 perspective-container overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
          {/* Spatial Floating Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full mb-8 text-xs font-semibold tracking-wide bg-slate-900/80 border border-blue-500/30 text-blue-300 shadow-xl shadow-blue-900/30 backdrop-blur-xl floating-layer-3">
            <Sparkles className="w-3.5 h-3.5 text-blue-400 animate-pulse" />
            <span>The Unified Multi-Agent Publishing & Growth Operating System</span>
            <div className="h-3 w-[1px] bg-slate-700" />
            <span className="text-emerald-400 font-mono">v2.0 Production MVP</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black tracking-tight mb-8 leading-[1.04]">
            From Validated Idea
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
              To Bestseller & Audience.
            </span>
          </h1>

          <p className="text-lg sm:text-xl max-w-3xl mx-auto mb-12 text-slate-300 leading-relaxed font-normal">
            Kindlepreneur 2.0 unifies <span className="text-white font-semibold">Publishing OS</span>,{' '}
            <span className="text-white font-semibold">Marketplace Studio</span>, and{' '}
            <span className="text-white font-semibold">AudienceOS</span> into a supervised agentic command center. Eight specialist
            AI agents research, draft, edit, format, audit compliance, and grow your audience under strict policy gates.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
            <Link
              href="/dashboard/projects/new"
              className="w-full sm:w-auto px-8 py-4 rounded-2xl text-base font-bold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:shadow-2xl hover:shadow-blue-500/40 border border-white/20 transition-all hover:scale-105 active:scale-95 flex items-center justify-center gap-3"
            >
              Start New Book Project
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#matrix"
              className="w-full sm:w-auto px-8 py-4 rounded-2xl text-base font-semibold text-slate-200 bg-slate-900/80 hover:bg-slate-800/80 border border-white/10 hover:border-white/20 backdrop-blur-xl transition-all flex items-center justify-center gap-2"
            >
              Explore Connected Matrix
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </a>
          </div>

          {/* ========================================================
              ANTIGRAVITY ISOMETRIC PLATFORM DECK (INTERACTIVE MATRIX)
             ======================================================== */}
          <div id="matrix" className="mt-6 mb-16 relative">
            <div className="flex items-center justify-center gap-2 p-1.5 max-w-md mx-auto mb-8 rounded-2xl bg-slate-900/90 border border-white/10 backdrop-blur-xl shadow-2xl">
              <button
                onClick={() => setActivePillar('publishing')}
                className={`flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                  activePillar === 'publishing'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                Publishing OS
              </button>
              <button
                onClick={() => setActivePillar('marketplace')}
                className={`flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                  activePillar === 'marketplace'
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Store className="w-3.5 h-3.5" />
                Marketplace Studio
              </button>
              <button
                onClick={() => setActivePillar('audience')}
                className={`flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                  activePillar === 'audience'
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <HeartHandshake className="w-3.5 h-3.5" />
                AudienceOS
              </button>
            </div>

            {/* 3D Isometric Command Deck Container */}
            <div className="relative max-w-5xl mx-auto rounded-3xl p-6 sm:p-10 border border-white/15 bg-gradient-to-b from-slate-900/90 via-[#0a0f24]/90 to-slate-950/95 backdrop-blur-2xl shadow-2xl shadow-black/80 isometric-deck">
              {/* Terminal Header Bar */}
              <div className="flex items-center justify-between pb-6 mb-6 border-b border-white/10 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  <span className="ml-3 font-mono text-slate-400 text-[11px]">
                    kindlepreneur-os // control-tower // active_node: {activePillar.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-slate-400 font-mono text-[11px]">
                  <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    AUTONOMY LEVEL: SUPERVISED (2)
                  </span>
                  <span className="hidden sm:inline">POLICY GATES: ENFORCING</span>
                </div>
              </div>

              {/* Dynamic View by Selected Pillar */}
              {activePillar === 'publishing' && (
                <div className="space-y-6 text-left">
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                      <div className="text-xs uppercase tracking-widest font-bold text-blue-400 mb-1">
                        Core Pipeline Engine
                      </div>
                      <h3 className="text-2xl font-bold text-white">Hierarchical Book Production Engine</h3>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-mono">
                      <Fingerprint className="w-3.5 h-3.5 text-blue-400" />
                      ARTIFACT: MANUSCRIPT_V3.EPUB
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-blue-400 flex items-center gap-1.5">
                          <Search className="w-3.5 h-3.5" /> Market Research
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">CONF: 0.94</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">High Demand, Low Differentiation</p>
                      <p className="text-xs text-slate-400">Opportunity Score 8.4 · 7 verified competitor weakness angles identified.</p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-purple-400 flex items-center gap-1.5">
                          <PenTool className="w-3.5 h-3.5" /> Chapter Writer
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">TOKENS: 42K</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">Burstiness & Continuity Tracking</p>
                      <p className="text-xs text-slate-400">Drafted 12 chapters with zero AI clichés and grounded case study placeholders.</p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                          <Shield className="w-3.5 h-3.5" /> Editorial & Policy QA
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">GATE: HUMAN</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">Awaiting Author Sign-off</p>
                      <p className="text-xs text-slate-400">Readability index 72. Copyright & trademark checks cleared with zero flags.</p>
                    </div>
                  </div>
                </div>
              )}

              {activePillar === 'marketplace' && (
                <div className="space-y-6 text-left">
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                      <div className="text-xs uppercase tracking-widest font-bold text-emerald-400 mb-1">
                        Marketplace Studio
                      </div>
                      <h3 className="text-2xl font-bold text-white">Preflight Package Validation & Connectors</h3>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-mono">
                      <Store className="w-3.5 h-3.5 text-emerald-400" />
                      IDEMPOTENCY: SHA256_ACTIVE
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                          <CheckCircle className="w-3.5 h-3.5" /> KDP Preflight Check
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">PASSED</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">Interior & Cover Audited</p>
                      <p className="text-xs text-slate-400">EPUB interior meets KDP guidelines. Royalty tier calculated at 70% ($4.99 USD).</p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-teal-400 flex items-center gap-1.5">
                          <Globe className="w-3.5 h-3.5" /> Amazon SP-API Adapter
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/20 text-teal-300">SANDBOX</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">Idempotent Staging Job</p>
                      <p className="text-xs text-slate-400">Mock ASIN generated: B098F21A. External effects isolated until human release.</p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-orange-400 flex items-center gap-1.5">
                          <Star className="w-3.5 h-3.5" /> Etsy Digital Marketplace
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-orange-500/20 text-orange-300">OAUTH 2.0</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">Digital Printable Packs</p>
                      <p className="text-xs text-slate-400">13 SEO tags, listing image mockups, and instant download PDF package staged.</p>
                    </div>
                  </div>
                </div>
              )}

              {activePillar === 'audience' && (
                <div className="space-y-6 text-left">
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                      <div className="text-xs uppercase tracking-widest font-bold text-cyan-400 mb-1">
                        AudienceOS Intelligence
                      </div>
                      <h3 className="text-2xl font-bold text-white">Value-First Growth & First-Class Consent</h3>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-mono">
                      <Shield className="w-3.5 h-3.5 text-cyan-400" />
                      CAN-SPAM & GDPR READY
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
                          <Compass className="w-3.5 h-3.5" /> Community Discovery
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">REDDIT / X</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">r/selfpublish Intent Signals</p>
                      <p className="text-xs text-slate-400">Monitors discussion gaps and formulates value-driven answers without spam links.</p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                          <Fingerprint className="w-3.5 h-3.5" /> Consent Engine
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">EXPLICIT OPT-IN</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">Immutable Consent Records</p>
                      <p className="text-xs text-slate-400">Timestamp, IP, mechanism, and opt-in legal basis recorded per subscriber.</p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-800/50 border border-white/5 weightless-card">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5" /> Global Kill Switch
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300">CIRCUIT BREAKER</span>
                      </div>
                      <p className="text-sm font-semibold text-white mb-2">Emergency Outbound Halt</p>
                      <p className="text-xs text-slate-400">Instantly halt email dispatch or outreach platform-wide with one click.</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Status Bar */}
              <div className="mt-8 pt-6 border-t border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs font-medium text-slate-400">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                  <span>Durable State Machine: PostgreSQL + Redis + arq Workers active</span>
                </div>
                <Link
                  href="/dashboard"
                  className="flex items-center gap-1 text-blue-400 hover:text-blue-300 font-semibold transition-colors"
                >
                  Enter Live Control Center <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================
          THE 10-STAGE PIPELINE (CONNECTING THE WHOLE PLATFORM)
         ======================================================== */}
      <section id="pipeline" className="py-24 border-t border-white/5 bg-slate-950/40 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 mb-4">
              End-to-End Workflow
            </div>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-4 text-white">
              The 10-Stage Research-to-Revenue Pipeline
            </h2>
            <p className="text-slate-400 text-base">
              Every stage produces durable, versioned artifacts with complete provenance, citations, and human approval checkpoints.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {PIPELINE_STAGES.map((stage, idx) => (
              <div
                key={stage.id}
                className="p-5 rounded-2xl bg-slate-900/60 border border-white/5 hover:border-white/20 transition-all hover:-translate-y-2 group weightless-card"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-bold font-mono text-slate-400">STEP {idx + 1}</span>
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: stage.color }} />
                </div>
                <h4 className="text-base font-bold text-white mb-1 group-hover:text-blue-300 transition-colors">
                  {stage.label}
                </h4>
                <div className="text-xs font-semibold text-slate-300 mb-2">{stage.agent}</div>
                <p className="text-xs text-slate-400 leading-relaxed">{stage.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================================================
          THE 8 SPECIALIST AGENTS GRID
         ======================================================== */}
      <section id="agents" className="py-24 border-t border-white/5 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest text-blue-400 bg-blue-500/10 border border-blue-500/20 mb-4">
              Agent Swarm
            </div>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-4 text-white">
              Eight Narrow Specialist Agents
            </h2>
            <p className="text-slate-400 text-base">
              No generic chatbot. Each agent executes within a strict schema contract with input validation, output verification, and cost budgets.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {AGENTS.map((agent) => {
              const Icon = agent.icon;
              return (
                <div
                  key={agent.name}
                  className="p-6 rounded-2xl bg-slate-900/60 border border-white/5 hover:border-white/20 transition-all hover:-translate-y-2 group weightless-card flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg"
                        style={{ backgroundColor: `${agent.color}20`, border: `1px solid ${agent.color}40` }}
                      >
                        <Icon className="w-5 h-5" style={{ color: agent.color }} />
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-white/5">
                        SCHEMA ENFORCED
                      </span>
                    </div>
                    <h4 className="text-lg font-bold text-white mb-0.5">{agent.name}</h4>
                    <div className="text-xs font-medium text-slate-400 mb-3">{agent.role}</div>
                    <p className="text-xs text-slate-400 leading-relaxed mb-4">{agent.desc}</p>
                  </div>
                  <div className="pt-3 border-t border-white/5 text-[11px] font-mono text-slate-300 flex items-center justify-between">
                    <span className="text-slate-500">Benchmark:</span>
                    <span className="font-semibold" style={{ color: agent.color }}>
                      {agent.output}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ========================================================
          HUMAN APPROVAL CONTROL TOWER & POLICY ENGINE
         ======================================================== */}
      <section id="control" className="py-24 border-t border-white/5 bg-slate-950/40 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest text-amber-400 bg-amber-500/10 border border-amber-500/20 mb-4">
                Policy as a Blocking Layer
              </div>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-6 text-white leading-tight">
                Policy-Bounded Autonomy.
                <br />
                <span className="text-amber-400">Zero Unsupervised Risk.</span>
              </h2>
              <p className="text-slate-300 text-base leading-relaxed mb-6">
                In Kindlepreneur 2.0, policy is not a warning toast—it is a mandatory code interception layer. Irreversible actions
                such as marketplace publishing, mass emailing, budget modifications, and compliance waivers require explicit human authorization.
              </p>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-white">Idempotent Side Effects</h5>
                    <p className="text-xs text-slate-400">
                      Every publishing job generates deterministic SHA-256 keys to prevent duplicate store submissions or billing charges.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-white">First-Class Consent Registry</h5>
                    <p className="text-xs text-slate-400">
                      Subscriber acquisition binds immutable timestamped records with opt-in mechanism and IP provenance for full GDPR compliance.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-white">Emergency Kill Switches</h5>
                    <p className="text-xs text-slate-400">
                      Platform-wide circuit breakers instantly cut off email dispatch or community distribution with a single administrator toggle.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Simulated Approval Card (Weightless Spatial UI) */}
            <div className="p-8 rounded-3xl bg-slate-900/90 border border-white/10 shadow-2xl backdrop-blur-2xl weightless-card relative">
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-300">
                    PENDING APPROVAL GATEWAY
                  </span>
                </div>
                <span className="text-[11px] font-mono text-slate-400">RISK SCORE: 0.15 (LOW)</span>
              </div>

              <h4 className="text-lg font-bold text-white mb-2">Publishing Gate: "Mindful Productivity Handbook"</h4>
              <p className="text-xs text-slate-300 mb-4 leading-relaxed">
                Compliance Agent passed 5/5 checks. KDP preflight package passed with 70% royalty threshold ($4.99 USD).
                Awaiting author confirmation to trigger Amazon SP-API sandbox dispatch.
              </p>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-white/5 mb-6 text-xs font-mono space-y-1.5 text-slate-400">
                <div>&gt; MARKETPLACE: Amazon KDP (Kindle Store)</div>
                <div>&gt; FORMAT: EPUB 3.2 Interior + High-Res Cover (300 DPI)</div>
                <div>&gt; IDEMPOTENCY KEY: 8f9b2d...471a</div>
                <div className="text-emerald-400">&gt; ESTIMATED TOKENS CONSUMED: 124,500 ($0.23 USD)</div>
              </div>

              <div className="flex items-center gap-3">
                <Link
                  href="/dashboard/approvals"
                  className="flex-1 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase tracking-wider text-center transition-all shadow-lg shadow-emerald-600/30"
                >
                  Approve Publication
                </Link>
                <Link
                  href="/dashboard/approvals"
                  className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs uppercase tracking-wider text-center border border-white/10 transition-all"
                >
                  Review Details
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================
          PRICING PLANS
         ======================================================== */}
      <section id="pricing" className="py-24 border-t border-white/5 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 mb-4">
              Transparent Pricing
            </div>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tight mb-4 text-white">
              Built for Solo Authors & Growing Publishers
            </h2>
            <p className="text-slate-400 text-base">
              Every tier comes with complete tenant data isolation, encrypted credentials, and automated safety policies.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {PLANS.map((plan) => (
              <div
                key={plan.name}
                className={`p-8 rounded-3xl border transition-all hover:-translate-y-2 flex flex-col justify-between weightless-card relative ${
                  plan.popular
                    ? 'bg-gradient-to-b from-slate-900/90 via-indigo-950/40 to-slate-900/90 border-indigo-500/40 shadow-2xl shadow-indigo-900/30'
                    : 'bg-slate-900/50 border-white/10'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-1 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-[10px] font-extrabold uppercase tracking-widest shadow-md">
                    Most Popular
                  </div>
                )}
                <div>
                  <h4 className="text-xl font-bold text-white mb-2">{plan.name}</h4>
                  <p className="text-xs text-slate-400 mb-6">{plan.desc}</p>
                  <div className="flex items-baseline gap-1 mb-8">
                    <span className="text-5xl font-black text-white">{plan.price}</span>
                    <span className="text-xs text-slate-400">/{plan.period}</span>
                  </div>

                  <div className="space-y-3 mb-8">
                    {plan.features.map((feature) => (
                      <div key={feature} className="flex items-center gap-2.5 text-xs text-slate-300">
                        <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <Link
                  href="/dashboard"
                  className={`w-full py-3.5 px-4 rounded-xl text-center text-xs font-bold uppercase tracking-wider transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-indigo-500/30 hover:opacity-90'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-white/10 bg-[#010411] py-16 relative z-10 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <Layers className="text-white w-4 h-4" />
              </div>
              <span className="font-extrabold text-white text-base">Kindlepreneur 2.0</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              The multi-tenant, multi-agent publishing and audience-growth operating system.
            </p>
          </div>

          <div>
            <h5 className="font-bold text-white mb-3 uppercase tracking-wider text-[11px]">Core Platform</h5>
            <ul className="space-y-2">
              <li><Link href="/dashboard" className="hover:text-white transition-colors">Command Center</Link></li>
              <li><Link href="/dashboard/projects" className="hover:text-white transition-colors">Publishing OS</Link></li>
              <li><Link href="/dashboard/research" className="hover:text-white transition-colors">Marketplace Studio</Link></li>
              <li><Link href="/dashboard/approvals" className="hover:text-white transition-colors">Approval Inbox</Link></li>
            </ul>
          </div>

          <div>
            <h5 className="font-bold text-white mb-3 uppercase tracking-wider text-[11px]">Safety & Standards</h5>
            <ul className="space-y-2">
              <li><span className="text-slate-400">Policy-Bounded Autonomy</span></li>
              <li><span className="text-slate-400">First-Class Consent Data</span></li>
              <li><span className="text-slate-400">Idempotent Publishing</span></li>
              <li><span className="text-slate-400">Amazon & Etsy Preflight</span></li>
            </ul>
          </div>

          <div>
            <h5 className="font-bold text-white mb-3 uppercase tracking-wider text-[11px]">System Status</h5>
            <div className="p-4 rounded-xl bg-slate-900 border border-white/5 space-y-2">
              <div className="flex items-center justify-between">
                <span>FastAPI Backend:</span>
                <span className="text-emerald-400 font-mono font-bold">PORT 8000 OK</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Next.js Web:</span>
                <span className="text-emerald-400 font-mono font-bold">PORT 3000 OK</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Specialist Agents:</span>
                <span className="text-blue-400 font-mono font-bold">8/8 LOADED</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 Kindlepreneur 2.0. All rights reserved.</p>
          <p className="text-slate-500">Supervised AI Publishing & Audience Operating System.</p>
        </div>
      </footer>
    </div>
  );
}
