'use client';
import { useState } from 'react';
import Link from 'next/link';
import { FolderOpen, Search, Plus, Filter, MoreVertical, BookOpen, Star, PenTool } from 'lucide-react';

const DEMO_PROJECTS = [
  { id: 'proj-1', name: 'Mindful Productivity', project_type: 'nonfiction_book', status: 'writing', updated_at: '2024-04-10T10:00:00Z', cost_usd: 1.24, icon: BookOpen },
  { id: 'proj-2', name: 'The Etsy Seller Playbook', project_type: 'nonfiction_book', status: 'outlining', updated_at: '2024-04-09T14:30:00Z', cost_usd: 0.87, icon: BookOpen },
  { id: 'proj-3', name: '60-Day Gratitude Journal', project_type: 'low_content_journal', status: 'formatting', updated_at: '2024-04-08T09:15:00Z', cost_usd: 0.42, icon: Star },
  { id: 'proj-4', name: 'Sci-Fi Epic: Nebula', project_type: 'fiction_book', status: 'idea', updated_at: '2024-04-07T16:45:00Z', cost_usd: 0.00, icon: PenTool },
];

const STATUS_COLORS: Record<string,string> = {
  idea:'#64748b', researching:'#3b82f6', strategy:'#6366f1', outlining:'#8b5cf6',
  writing:'#a855f7', editing:'#d946ef', formatting:'#ec4899', metadata:'#f97316',
  compliance:'#eab308', publishing:'#22c55e', marketing:'#14b8a6', published:'#10b981'
};

function StatusBadge({status}:{status:string}) {
  const color = STATUS_COLORS[status] || '#64748b';
  return (
    <span className="px-2 py-0.5 rounded-full text-xs font-medium capitalize inline-block" style={{background:`${color}20`,color,border:`1px solid ${color}40`}}>{status}</span>
  );
}

export default function ProjectsPage() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filtered = DEMO_PROJECTS.filter(p => 
    p.name.toLowerCase().includes(search.toLowerCase()) &&
    (filter === 'all' || p.status === filter || p.project_type === filter)
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{fontFamily:'Outfit,sans-serif'}}>Projects</h1>
          <p className="text-sm" style={{color:'#64748b'}}>Manage your publishing catalog</p>
        </div>
        <Link href="/dashboard/projects/new" className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:scale-105" style={{background:'linear-gradient(135deg,#3b82f6,#6366f1)'}}>
          <Plus size={16} /> New Project
        </Link>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{color:'#64748b'}} />
          <input 
            type="text" 
            placeholder="Search projects..." 
            className="w-full pl-9 pr-4 py-2 rounded-lg text-sm"
            style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)',color:'#f8fafc'}}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          {['all', 'idea', 'writing', 'formatting', 'published'].map(f => (
            <button key={f} onClick={() => setFilter(f)} className="px-3 py-1.5 rounded-lg text-sm font-medium capitalize whitespace-nowrap transition-colors" style={filter === f ? {background:'rgba(59,130,246,0.15)',color:'#93c5fd',border:'1px solid rgba(59,130,246,0.3)'} : {background:'rgba(15,23,42,0.6)',color:'#94a3b8',border:'1px solid rgba(255,255,255,0.06)'}}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20 rounded-2xl" style={{background:'rgba(15,23,42,0.3)',border:'1px dashed rgba(255,255,255,0.1)'}}>
          <FolderOpen size={48} className="mx-auto mb-4" style={{color:'#475569'}} />
          <h3 className="text-lg font-semibold mb-2" style={{color:'#cbd5e1'}}>No projects found</h3>
          <p className="text-sm mb-6" style={{color:'#64748b'}}>Adjust your filters or create a new project.</p>
          <Link href="/dashboard/projects/new" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold" style={{background:'rgba(59,130,246,0.1)',color:'#93c5fd'}}>
            <Plus size={16} /> Create Project
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 stagger-children">
          {filtered.map(project => {
            const Icon = project.icon;
            return (
              <Link key={project.id} href={`/dashboard/projects/${project.id}`} className="group p-5 rounded-2xl transition-all hover:-translate-y-1 hover:bg-white/5 block" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
                <div className="flex items-start justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{background:'rgba(59,130,246,0.1)'}}>
                    <Icon size={18} style={{color:'#3b82f6'}} />
                  </div>
                  <button className="w-8 h-8 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/10" style={{color:'#64748b'}}>
                    <MoreVertical size={16} />
                  </button>
                </div>
                <h3 className="font-semibold text-lg mb-1 truncate" style={{fontFamily:'Outfit,sans-serif'}}>{project.name}</h3>
                <div className="text-xs mb-4 capitalize" style={{color:'#64748b'}}>{project.project_type.replace('_', ' ')}</div>
                <div className="flex items-center justify-between mt-auto">
                  <StatusBadge status={project.status} />
                  <span className="text-xs font-medium" style={{color:'#475569'}}>${project.cost_usd.toFixed(2)} AI Cost</span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
