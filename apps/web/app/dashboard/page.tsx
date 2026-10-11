'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@clerk/nextjs';
import { FolderOpen, CheckSquare, DollarSign, FileText, Plus, ArrowRight, Search, Target, PenTool, Zap, Clock, CheckCircle, AlertCircle, Brain, Activity } from 'lucide-react';

// Mock data for demo mode
const DEMO_PROJECTS = [
  { id: 'proj-1', name: 'Mindful Productivity', project_type: 'nonfiction_book', status: 'writing', updated_at: new Date().toISOString(), cost_usd: 1.24 },
  { id: 'proj-2', name: 'The Etsy Seller Playbook', project_type: 'nonfiction_book', status: 'outlining', updated_at: new Date().toISOString(), cost_usd: 0.87 },
  { id: 'proj-3', name: '60-Day Gratitude Journal', project_type: 'low_content_journal', status: 'formatting', updated_at: new Date().toISOString(), cost_usd: 0.42 },
];

const DEMO_APPROVALS = [
  { id: 'apr-1', title: 'Approve research opportunity: Mindful Productivity', approval_type: 'opportunity', risk_score: 0.2, project_id: 'proj-1' },
  { id: 'apr-2', title: 'Review Chapter 3 draft: The Etsy Seller Playbook', approval_type: 'chapter', risk_score: 0.1, project_id: 'proj-2' },
];

const DEMO_EVENTS = [
  { id: 'e1', agent: 'Research Analyst', action: 'Completed market analysis for Mindful Productivity', status: 'completed', cost: 0.43, time: '2m ago' },
  { id: 'e2', agent: 'Master Outliner', action: 'Generated 12-chapter outline for Etsy Seller Playbook', status: 'completed', cost: 0.31, time: '18m ago' },
  { id: 'e3', agent: 'Chapter Writer', action: 'Drafting Chapter 4: Deep Work Systems', status: 'running', cost: 0.00, time: 'Now' },
  { id: 'e4', agent: 'Compliance Guard', action: 'Audit queued for 60-Day Gratitude Journal', status: 'queued', cost: 0.00, time: 'Pending' },
];

const STATUS_STAGES = ['idea','researching','strategy','outlining','writing','editing','formatting','metadata','compliance','publishing','marketing','published'];
const STATUS_COLORS: Record<string,string> = {
  idea:'#64748b', researching:'#3b82f6', strategy:'#6366f1', outlining:'#8b5cf6',
  writing:'#a855f7', editing:'#d946ef', formatting:'#ec4899', metadata:'#f97316',
  compliance:'#eab308', publishing:'#22c55e', marketing:'#14b8a6', published:'#10b981'
};

function StatusBadge({status}:{status:string}) {
  const color = STATUS_COLORS[status] || '#64748b';
  return (
    <span className="px-2 py-0.5 rounded-full text-xs font-medium capitalize" style={{background:`${color}20`,color,border:`1px solid ${color}40`}}>{status}</span>
  );
}

function StageProgress({status}:{status:string}) {
  const idx = STATUS_STAGES.indexOf(status);
  const pct = idx < 0 ? 0 : Math.round((idx / (STATUS_STAGES.length - 1)) * 100);
  return (
    <div className="w-full h-1 rounded-full" style={{background:'rgba(255,255,255,0.06)'}}>
      <div className="h-full rounded-full transition-all" style={{width:`${pct}%`,background:'linear-gradient(90deg,#3b82f6,#8b5cf6)'}} />
    </div>
  );
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

export default function DashboardHome() {
  const { userId } = useAuth();
  const [projects, setProjects] = useState(DEMO_PROJECTS);
  const [approvals, setApprovals] = useState(DEMO_APPROVALS);
  const [loading, setLoading] = useState(false);

  const stats = [
    { label: 'Active Projects', value: projects.length, icon: FolderOpen, color: '#3b82f6' },
    { label: 'Pending Approvals', value: approvals.length, icon: CheckSquare, color: '#f59e0b' },
    { label: 'AI Cost (Month)', value: '$2.94', icon: DollarSign, color: '#10b981' },
    { label: 'Artifacts Created', value: 14, icon: FileText, color: '#8b5cf6' },
  ];

  const QUICK_ACTIONS = [
    { label: 'New Book Project', href: '/dashboard/projects/new', icon: Plus, color: '#3b82f6' },
    { label: 'Research a Niche', href: '/dashboard/research', icon: Search, color: '#6366f1' },
    { label: 'View All Projects', href: '/dashboard/projects', icon: FolderOpen, color: '#8b5cf6' },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold" style={{fontFamily:'Outfit,sans-serif'}}>{getGreeting()}, Publisher 📚</h1>
        <p className="text-sm mt-1" style={{color:'#64748b'}}>Here’s what’s happening across your publishing workspace.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
        {stats.map(stat => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="p-5 rounded-2xl" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{background:`${stat.color}15`}}>
                  <Icon size={16} style={{color:stat.color}} />
                </div>
                <span className="text-xs font-medium" style={{color:'#64748b'}}>{stat.label}</span>
              </div>
              <div className="text-2xl font-bold" style={{fontFamily:'Outfit,sans-serif'}}>{stat.value}</div>
            </div>
          );
        })}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Projects (2/3 width) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold" style={{fontFamily:'Outfit,sans-serif'}}>Recent Projects</h2>
            <Link href="/dashboard/projects" className="text-sm flex items-center gap-1 transition-colors hover:text-white" style={{color:'#64748b'}}>
              View all <ArrowRight size={14} />
            </Link>
          </div>
          <div className="space-y-3">
            {projects.map(project => (
              <Link key={project.id} href={`/dashboard/projects/${project.id}`} className="block p-4 rounded-2xl transition-all hover:-translate-y-0.5 hover:bg-white/5" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{background:'rgba(59,130,246,0.1)'}}>
                    <FolderOpen size={18} style={{color:'#3b82f6'}} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm truncate">{project.name}</span>
                      <StatusBadge status={project.status} />
                    </div>
                    <StageProgress status={project.status} />
                  </div>
                  <div className="text-xs flex-shrink-0" style={{color:'#475569'}}>${project.cost_usd.toFixed(2)}</div>
                </div>
              </Link>
            ))}
          </div>

          {/* Agent activity */}
          <div className="mt-6">
            <h2 className="font-semibold mb-4 flex items-center gap-2" style={{fontFamily:'Outfit,sans-serif'}}>
              <Activity size={16} style={{color:'#10b981'}} />
              Agent Activity
            </h2>
            <div className="rounded-2xl overflow-hidden" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
              {DEMO_EVENTS.map((event, idx) => (
                <div key={event.id} className="flex items-center gap-3 p-4" style={{borderBottom: idx < DEMO_EVENTS.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none'}}>
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{background:'rgba(139,92,246,0.1)'}}>
                    <Brain size={14} style={{color:'#8b5cf6'}} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium" style={{color:'#8b5cf6'}}>{event.agent}</div>
                    <div className="text-sm truncate" style={{color:'#cbd5e1'}}>{event.action}</div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {event.status === 'running' && <span className="w-2 h-2 rounded-full animate-pulse" style={{background:'#3b82f6'}} />}
                    {event.status === 'completed' && <CheckCircle size={12} style={{color:'#10b981'}} />}
                    {event.status === 'queued' && <Clock size={12} style={{color:'#64748b'}} />}
                    <span className="text-xs" style={{color:'#475569'}}>{event.time}</span>
                    {event.cost > 0 && <span className="text-xs" style={{color:'#10b981'}}>${event.cost.toFixed(2)}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column (1/3 width) */}
        <div className="space-y-4">
          {/* Quick Start */}
          <div className="p-5 rounded-2xl" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
            <h3 className="font-semibold mb-4" style={{fontFamily:'Outfit,sans-serif'}}>Quick Start</h3>
            <div className="space-y-2">
              {QUICK_ACTIONS.map(action => {
                const Icon = action.icon;
                return (
                  <Link key={action.label} href={action.href}
                    className="flex items-center gap-3 p-3 rounded-xl transition-all hover:bg-white/5"
                    style={{border:'1px solid rgba(255,255,255,0.04)'}}>
                    <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{background:`${action.color}15`}}>
                      <Icon size={14} style={{color:action.color}} />
                    </div>
                    <span className="text-sm font-medium">{action.label}</span>
                    <ArrowRight size={14} className="ml-auto" style={{color:'#374151'}} />
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Pending Approvals */}
          <div className="p-5 rounded-2xl" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold" style={{fontFamily:'Outfit,sans-serif'}}>Pending Approvals</h3>
              <span className="px-2 py-0.5 rounded-full text-xs font-bold" style={{background:'rgba(239,68,68,0.15)',color:'#f87171'}}>{approvals.length}</span>
            </div>
            {approvals.length === 0 ? (
              <p className="text-sm" style={{color:'#475569'}}>All clear! No approvals pending.</p>
            ) : (
              <div className="space-y-3">
                {approvals.slice(0, 3).map(apr => (
                  <div key={apr.id} className="p-3 rounded-xl" style={{background:'rgba(245,158,11,0.05)',border:'1px solid rgba(245,158,11,0.15)'}}>
                    <div className="text-xs font-medium mb-1 capitalize" style={{color:'#f59e0b'}}>{apr.approval_type}</div>
                    <div className="text-xs mb-3" style={{color:'#cbd5e1'}}>{apr.title}</div>
                    <div className="flex gap-2">
                      <button className="flex-1 py-1.5 rounded-lg text-xs font-semibold" style={{background:'rgba(16,185,129,0.15)',color:'#34d399'}}>Approve</button>
                      <button className="flex-1 py-1.5 rounded-lg text-xs font-semibold" style={{background:'rgba(239,68,68,0.08)',color:'#f87171'}}>Reject</button>
                    </div>
                  </div>
                ))}
                <Link href="/dashboard/approvals" className="text-xs flex items-center gap-1 transition-colors hover:text-white" style={{color:'#64748b'}}>
                  View all approvals <ArrowRight size={12} />
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
