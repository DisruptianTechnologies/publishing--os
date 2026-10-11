'use client';
import { useState, use } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Settings, FileText, CheckSquare, Brain, Activity, Clock, CheckCircle } from 'lucide-react';

const STAGES = [
  { id: 'research', label: 'Research', icon: Search },
  { id: 'strategy', label: 'Strategy', icon: Target },
  { id: 'outline', label: 'Outline', icon: FileText },
  { id: 'writing', label: 'Writing', icon: PenTool },
  { id: 'editing', label: 'Editing', icon: CheckCircle },
];
import { Search, Target, PenTool } from 'lucide-react';

export default function ProjectDashboard({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/projects" className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-white/10" style={{color:'#94a3b8'}}>
          <ArrowLeft size={18} />
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold" style={{fontFamily:'Outfit,sans-serif'}}>Mindful Productivity</h1>
            <span className="px-2 py-0.5 rounded-full text-xs font-medium" style={{background:'rgba(168,85,247,0.2)',color:'#c084fc',border:'1px solid rgba(168,85,247,0.4)'}}>Writing</span>
          </div>
          <p className="text-sm" style={{color:'#64748b'}}>Non-Fiction Book • Created 3 days ago</p>
        </div>
        <div className="ml-auto flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all hover:bg-white/5" style={{border:'1px solid rgba(255,255,255,0.1)'}}>
            <Settings size={16} /> Configure
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:scale-105" style={{background:'linear-gradient(135deg,#a855f7,#d946ef)'}}>
            <Play size={16} /> Start Next Stage
          </button>
        </div>
      </div>

      {/* Pipeline Vis */}
      <div className="p-6 rounded-2xl overflow-x-auto" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
        <div className="flex items-center min-w-max">
          {STAGES.map((stage, idx) => {
            const Icon = stage.icon;
            const isCompleted = idx < 3;
            const isActive = idx === 3;
            return (
              <div key={stage.id} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all ${isActive ? 'animate-pulse-glow' : ''}`}
                    style={{
                      background: isCompleted ? 'rgba(16,185,129,0.1)' : isActive ? 'rgba(168,85,247,0.1)' : 'rgba(255,255,255,0.02)',
                      border: `1px solid ${isCompleted ? '#10b981' : isActive ? '#a855f7' : 'rgba(255,255,255,0.06)'}`,
                      color: isCompleted ? '#10b981' : isActive ? '#c084fc' : '#64748b'
                    }}>
                    <Icon size={20} />
                  </div>
                  <span className="text-xs font-medium mt-2" style={{color: isActive ? 'white' : '#64748b'}}>{stage.label}</span>
                </div>
                {idx < STAGES.length - 1 && (
                  <div className="w-16 h-1 mx-2 rounded-full" style={{background: isCompleted ? '#10b981' : 'rgba(255,255,255,0.06)'}} />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-6" style={{borderBottom:'1px solid rgba(255,255,255,0.06)'}}>
        {['overview','artifacts','approvals','activity'].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} className="pb-3 text-sm font-medium capitalize relative" style={{color: activeTab === tab ? 'white' : '#64748b'}}>
            {tab}
            {activeTab === tab && <div className="absolute bottom-0 left-0 right-0 h-0.5" style={{background:'#3b82f6'}} />}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'overview' && (
            <div className="p-6 rounded-2xl space-y-4" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
              <h2 className="font-semibold text-lg" style={{fontFamily:'Outfit,sans-serif'}}>Current Focus: Chapter Drafting</h2>
              <p className="text-sm" style={{color:'#94a3b8'}}>The Chapter Writer agent is currently drafting Chapter 4 based on the approved outline and research materials. Completion expected in ~5 mins.</p>
              
              <div className="p-4 rounded-xl mt-4" style={{background:'rgba(0,0,0,0.2)',border:'1px solid rgba(255,255,255,0.04)'}}>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-medium">Chapter 4: Deep Work Systems</div>
                  <div className="text-xs text-purple-400 animate-pulse">Drafting...</div>
                </div>
                <div className="w-full h-1.5 rounded-full" style={{background:'rgba(255,255,255,0.06)'}}>
                  <div className="h-full rounded-full" style={{width:'45%',background:'linear-gradient(90deg,#8b5cf6,#d946ef)'}} />
                </div>
              </div>
            </div>
          )}
          {activeTab === 'artifacts' && (
            <div className="space-y-3">
              {[
                { name: 'Market Research Report v1', type: 'PDF', date: '3 days ago' },
                { name: 'Book Outline Final', type: 'Markdown', date: 'Yesterday' },
                { name: 'Chapter 1-3 Drafts', type: 'Docx', date: '2 hours ago' },
              ].map(a => (
                <div key={a.name} className="flex items-center justify-between p-4 rounded-xl hover:bg-white/5 transition-colors cursor-pointer" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
                  <div className="flex items-center gap-3">
                    <FileText size={18} style={{color:'#3b82f6'}} />
                    <div>
                      <div className="text-sm font-medium">{a.name}</div>
                      <div className="text-xs" style={{color:'#64748b'}}>{a.type} • {a.date}</div>
                    </div>
                  </div>
                  <button className="text-xs font-medium px-3 py-1.5 rounded-lg" style={{background:'rgba(255,255,255,0.05)'}}>View</button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="p-5 rounded-2xl" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
            <h3 className="font-semibold mb-4 flex items-center gap-2" style={{fontFamily:'Outfit,sans-serif'}}>
              <Brain size={16} style={{color:'#8b5cf6'}} /> Agent Stream
            </h3>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="mt-1 w-2 h-2 rounded-full animate-pulse" style={{background:'#a855f7'}} />
                <div>
                  <div className="text-xs font-medium text-purple-400">Chapter Writer</div>
                  <div className="text-sm">Synthesizing research notes for Ch 4 section 2...</div>
                  <div className="text-xs mt-1" style={{color:'#64748b'}}>Just now</div>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="mt-1 w-2 h-2 rounded-full" style={{background:'#10b981'}} />
                <div>
                  <div className="text-xs font-medium text-emerald-400">Dev Editor</div>
                  <div className="text-sm">Approved Chapter 3 with minor prose tweaks.</div>
                  <div className="text-xs mt-1" style={{color:'#64748b'}}>2h ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
