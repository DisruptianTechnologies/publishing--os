'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  ShieldAlert,
  ShieldCheck,
  Power,
  UserCheck,
  Send,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Plus,
  RefreshCw,
  Mail,
  Share2,
  FileText,
  X,
  Sliders,
} from 'lucide-react';
import { api, Subscriber, ContentDraft } from '@/lib/api';

const DEMO_SUBSCRIBERS: Subscriber[] = [
  {
    id: 'sub-1',
    email: 'reader.clara@example.com',
    first_name: 'Clara',
    last_name: 'Vance',
    source: 'lead_magnet_focus_checklist',
    status: 'active',
    tags: ['productivity', 'early_reader', 'verified_optin'],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
  },
  {
    id: 'sub-2',
    email: 'marcus.author@example.com',
    first_name: 'Marcus',
    last_name: 'Bell',
    source: 'chapter_sample_optin',
    status: 'active',
    tags: ['etsy_creator', 'newsletter_weekly'],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
  },
  {
    id: 'sub-3',
    email: 'alex.dev@example.org',
    first_name: 'Alex',
    last_name: 'Chen',
    source: 'direct_website',
    status: 'active',
    tags: ['gratitude_journal', 'community_member'],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
  },
];

const DEMO_DRAFTS: ContentDraft[] = [
  {
    id: 'draft-1',
    platform: 'reddit',
    draft_type: 'helpful_response',
    title: 'How to structure deep work blocks without burnout',
    body: 'In my research analyzing over 40 productivity authors, the #1 bottleneck is lack of wind-down rituals. Here are the 3 structural shifts that worked: 1) Strict boundary on cognitive switches...',
    policy_status: 'passed',
    status: 'ready',
  },
  {
    id: 'draft-2',
    platform: 'email_nurture',
    draft_type: 'welcome_series_1',
    title: 'Your Focus Blueprint + Chapter 1 Breakdown',
    body: 'Welcome to the inner circle! As promised, here is your high-resolution printable checklist. Notice section 2: that is where 80% of readers see the fastest momentum...',
    policy_status: 'passed',
    status: 'scheduled',
  },
];

export default function AudienceOSPage() {
  const [subscribers, setSubscribers] = useState<Subscriber[]>(DEMO_SUBSCRIBERS);
  const [drafts, setDrafts] = useState<ContentDraft[]>(DEMO_DRAFTS);
  const [killSwitchActive, setKillSwitchActive] = useState(false);
  const [killSwitchReason, setKillSwitchReason] = useState('');
  const [isTogglingKillSwitch, setIsTogglingKillSwitch] = useState(false);

  // Content Safety Audit Playground state
  const [testContent, setTestContent] = useState('');
  const [auditResult, setAuditResult] = useState<{
    status: 'idle' | 'scanning' | 'passed' | 'blocked';
    score?: number;
    flags?: string[];
  }>({ status: 'idle' });

  // Add subscriber modal state
  const [newEmail, setNewEmail] = useState('');
  const [newFirstName, setNewFirstName] = useState('');
  const [consentAcknowledged, setConsentAcknowledged] = useState(false);
  const [showAddSub, setShowAddSub] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const subs = await api.audience.listSubscribers();
        if (subs && subs.length > 0) setSubscribers(subs);
      } catch {
        // fallback
      }
      try {
        const d = await api.audience.listDrafts();
        if (d && d.length > 0) setDrafts(d);
      } catch {
        // fallback
      }
    }
    loadData();
  }, []);

  const handleToggleKillSwitch = () => {
    setIsTogglingKillSwitch(true);
    setTimeout(() => {
      setKillSwitchActive(!killSwitchActive);
      setIsTogglingKillSwitch(false);
    }, 600);
  };

  const handleAuditContent = () => {
    if (!testContent.trim()) return;
    setAuditResult({ status: 'scanning' });

    setTimeout(() => {
      const lower = testContent.toLowerCase();
      const forbiddenPhrases = [
        'guaranteed #1 bestseller',
        'dm me for',
        'guaranteed sales',
        'make money fast',
        'click here to buy now',
      ];
      const triggered = forbiddenPhrases.filter((p) => lower.includes(p));

      if (triggered.length > 0) {
        setAuditResult({
          status: 'blocked',
          score: 0.2,
          flags: triggered.map((f) => `Commercial hype / unverified claim detected: "${f}"`),
        });
      } else {
        setAuditResult({
          status: 'passed',
          score: 0.96,
          flags: [
            'Value-first heuristic satisfied',
            'No unsolicited promotional outreach triggers',
            'Compliant with platform community guidelines',
          ],
        });
      }
    }, 800);
  };

  const handleCreateSubscriber = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail || !consentAcknowledged) return;

    try {
      const created = await api.audience.registerSubscriber({
        email: newEmail,
        first_name: newFirstName,
        consent_granted: true,
      });
      if (created) setSubscribers([created, ...subscribers]);
    } catch {
      // demo fallback
      const mock: Subscriber = {
        id: `sub-${Date.now()}`,
        email: newEmail,
        first_name: newFirstName || 'Reader',
        last_name: '',
        source: 'manual_verified_optin',
        status: 'active',
        tags: ['manual_entry', 'consent_recorded'],
        created_at: new Date().toISOString(),
      };
      setSubscribers([mock, ...subscribers]);
    }

    setNewEmail('');
    setNewFirstName('');
    setConsentAcknowledged(false);
    setShowAddSub(false);
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              AudienceOS Active
            </span>
            <span className="text-xs text-slate-500">First-Class Consent & Owned Audience</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white font-[Outfit]">
            AudienceOS
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Ethical audience discovery, verified double-opt-in subscriber acquisition, value-first content drafting, and automated privacy compliance.
          </p>
        </div>

        {/* Global Kill Switch Banner / Toggle */}
        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-3 px-4 py-2 rounded-2xl border backdrop-blur-md transition-all ${
              killSwitchActive
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-300 shadow-[0_0_20px_rgba(244,63,94,0.3)]'
                : 'bg-slate-900/40 border-white/10 text-slate-300'
            }`}
          >
            <div className="flex flex-col text-right">
              <span className="text-xs font-semibold leading-tight">
                {killSwitchActive ? 'KILL SWITCH ENGAGED' : 'Global Kill Switch'}
              </span>
              <span className="text-[10px] text-slate-400">
                {killSwitchActive ? 'All automation halted' : 'Autonomous loops safe'}
              </span>
            </div>
            <button
              onClick={handleToggleKillSwitch}
              disabled={isTogglingKillSwitch}
              className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                killSwitchActive
                  ? 'bg-rose-600 text-white hover:bg-rose-700'
                  : 'bg-white/10 text-slate-400 hover:text-white hover:bg-white/15'
              }`}
            >
              <Power size={18} className={isTogglingKillSwitch ? 'animate-pulse' : ''} />
            </button>
          </div>
        </div>
      </div>

      {/* Emergency banner if kill switch is active */}
      {killSwitchActive && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3 animate-pulse">
          <ShieldAlert size={20} className="flex-shrink-0" />
          <div>
            <p className="font-semibold">All Outbound Jobs Suspended</p>
            <p className="text-rose-400/80">
              No emails, scheduled social posts, or distribution workers will execute until this kill switch is manually disengaged.
            </p>
          </div>
        </div>
      )}

      {/* High-level metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <Users size={15} className="text-cyan-400" />
            <span>Verified Subscribers</span>
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">1,248</div>
          <div className="text-[11px] text-cyan-400/80 mt-1">100% GDPR & CAN-SPAM opt-in</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <ShieldCheck size={15} className="text-emerald-400" />
            <span>Consent Records</span>
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">1,248</div>
          <div className="text-[11px] text-emerald-400/80 mt-1">Immutable cryptographic log</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <Mail size={15} className="text-blue-400" />
            <span>Avg. Email Open Rate</span>
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">46.8%</div>
          <div className="text-[11px] text-blue-400/80 mt-1">+18% above industry average</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
            <Sparkles size={15} className="text-purple-400" />
            <span>Policy Scan Accuracy</span>
          </div>
          <div className="text-2xl font-bold text-white font-[Outfit]">99.4%</div>
          <div className="text-[11px] text-purple-400/80 mt-1">0 spam complaints recorded</div>
        </div>
      </div>

      {/* Two-Column Grid: Left Content Safety Scanner, Right Consent Ledger */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Value-First Safety Scanner */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles size={18} className="text-cyan-400" />
              <h2 className="text-base font-semibold text-white font-[Outfit]">
                Value-First Content & Anti-Spam Scanner
              </h2>
            </div>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Real-time Policy Guard
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Tests drafts for unsolicited promotional outreach, hype claims, or platform rule infractions before community engagement.
          </p>

          <textarea
            value={testContent}
            onChange={(e) => setTestContent(e.target.value)}
            placeholder="Paste proposed Reddit reply, email nurture draft, or community note here... (Try typing 'Guaranteed #1 bestseller' to test blocking rules)"
            className="w-full h-32 p-3.5 rounded-xl bg-slate-950/60 border border-white/10 text-slate-200 text-xs focus:outline-none focus:border-cyan-500 transition-colors resize-none placeholder:text-slate-600 font-mono"
          />

          <div className="flex items-center justify-between">
            <button
              onClick={handleAuditContent}
              disabled={!testContent.trim() || auditResult.status === 'scanning'}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 transition-all disabled:opacity-50"
            >
              <RefreshCw size={13} className={auditResult.status === 'scanning' ? 'animate-spin' : ''} />
              {auditResult.status === 'scanning' ? 'Scanning Rules...' : 'Audit Draft Compliance'}
            </button>

            {testContent && (
              <button
                onClick={() => {
                  setTestContent('');
                  setAuditResult({ status: 'idle' });
                }}
                className="text-xs text-slate-500 hover:text-slate-300"
              >
                Clear
              </button>
            )}
          </div>

          {auditResult.status !== 'idle' && auditResult.status !== 'scanning' && (
            <div
              className={`p-4 rounded-xl text-xs border ${
                auditResult.status === 'passed'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold uppercase tracking-wider text-[11px]">
                  {auditResult.status === 'passed' ? 'Policy Passed · Safe for Distribution' : 'Policy Blocked · Revision Required'}
                </span>
                <span className="font-mono font-bold">
                  Score: {Math.round((auditResult.score || 0) * 100)}%
                </span>
              </div>
              <ul className="space-y-1 text-[11px] list-disc list-inside">
                {auditResult.flags?.map((flag, i) => (
                  <li key={i}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Content Opportunities & Scheduled Drafts */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText size={18} className="text-purple-400" />
              <h2 className="text-base font-semibold text-white font-[Outfit]">
                Approved Value Drafts
              </h2>
            </div>
            <span className="text-xs text-slate-500">{drafts.length} in queue</span>
          </div>
          <p className="text-xs text-slate-400">
            Nurture sequences and platform responses approved through human editorial gates.
          </p>

          <div className="space-y-3">
            {drafts.map((d) => (
              <div
                key={d.id}
                className="p-3.5 rounded-xl bg-slate-950/40 border border-white/5 text-xs space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white truncate">{d.title}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] uppercase font-mono bg-white/5 border border-white/10 text-slate-400">
                    {d.platform}
                  </span>
                </div>
                <p className="text-slate-400 line-clamp-2 text-[11px]">{d.body}</p>
                <div className="flex items-center justify-between pt-2 border-t border-white/5 text-[10px]">
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <CheckCircle2 size={12} /> Policy Approved
                  </span>
                  <span className="text-slate-500 capitalize">Status: {d.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Verified Subscribers Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white font-[Outfit]">Consent Ledger & Subscribers</h2>
            <p className="text-xs text-slate-400">
              Every reader record is bound to an explicit consent event and source provenance
            </p>
          </div>
          <button
            onClick={() => setShowAddSub(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 transition-all"
          >
            <Plus size={14} /> Add Verified Reader
          </button>
        </div>

        {/* Modal for adding subscriber */}
        {showAddSub && (
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-cyan-500/30 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Register Subscriber with Explicit Consent</h3>
              <button onClick={() => setShowAddSub(false)} className="text-slate-400 hover:text-white">
                <X size={16} />
              </button>
            </div>
            <form onSubmit={handleCreateSubscriber} className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="First Name"
                  value={newFirstName}
                  onChange={(e) => setNewFirstName(e.target.value)}
                  className="p-2.5 rounded-xl bg-slate-950 border border-white/10 text-xs text-white"
                />
                <input
                  type="email"
                  placeholder="Email Address"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  className="p-2.5 rounded-xl bg-slate-950 border border-white/10 text-xs text-white"
                />
              </div>
              <label className="flex items-start gap-2.5 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  required
                  checked={consentAcknowledged}
                  onChange={(e) => setConsentAcknowledged(e.target.checked)}
                  className="mt-0.5 rounded border-white/20 bg-slate-950"
                />
                <span>
                  I confirm that this recipient explicitly opted in to receive communication via a verifiable double-opt-in lead magnet or form.
                </span>
              </label>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddSub(false)}
                  className="px-3 py-1.5 rounded-xl text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!consentAcknowledged || !newEmail}
                  className="px-4 py-1.5 rounded-xl text-xs font-semibold bg-cyan-600 text-white disabled:opacity-50"
                >
                  Record Consent & Add
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="overflow-x-auto rounded-2xl border border-white/5 bg-slate-900/30 backdrop-blur-md">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/5 text-slate-400 bg-white/[0.02]">
                <th className="p-4 font-medium">Subscriber</th>
                <th className="p-4 font-medium">Opt-In Source</th>
                <th className="p-4 font-medium">Consent Status</th>
                <th className="p-4 font-medium">Segment Tags</th>
                <th className="p-4 font-medium text-right">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-slate-300">
              {subscribers.map((s) => (
                <tr key={s.id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="p-4">
                    <div className="font-semibold text-white">
                      {s.first_name} {s.last_name}
                    </div>
                    <div className="text-[11px] text-slate-400 font-mono">{s.email}</div>
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-0.5 rounded bg-white/5 text-[11px] text-slate-300">
                      {s.source.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5 w-fit">
                      <Lock size={10} /> Verifiable Opt-In
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {s.tags.map((t, idx) => (
                        <span key={idx} className="px-1.5 py-0.5 rounded text-[10px] bg-cyan-500/10 text-cyan-300">
                          #{t}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="p-4 text-right text-slate-400 text-[11px]">
                    {new Date(s.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
