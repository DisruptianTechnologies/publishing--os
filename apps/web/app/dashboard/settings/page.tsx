'use client';
import { useState } from 'react';
import { Settings, Zap, CreditCard, Puzzle } from 'lucide-react';

export default function SettingsPage() {
  const [tab, setTab] = useState('autonomy');

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold" style={{fontFamily:'Outfit,sans-serif'}}>Settings</h1>
        <p className="text-sm" style={{color:'#64748b'}}>Manage your workspace and AI preferences.</p>
      </div>

      <div className="flex gap-2 p-1 rounded-lg w-max" style={{background:'rgba(15,23,42,0.8)'}}>
        {[
          { id: 'general', icon: Settings, label: 'General' },
          { id: 'autonomy', icon: Zap, label: 'Autonomy' },
          { id: 'integrations', icon: Puzzle, label: 'Integrations' },
          { id: 'billing', icon: CreditCard, label: 'Billing' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all" style={tab === t.id ? {background:'rgba(255,255,255,0.1)',color:'white'} : {color:'#64748b'}}>
            <t.icon size={14} /> {t.label}
          </button>
        ))}
      </div>

      {tab === 'autonomy' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
            <h2 className="text-lg font-semibold mb-2">Agent Autonomy Level</h2>
            <p className="text-sm text-slate-400 mb-6">Control how much manual approval is required during the publishing pipeline.</p>
            
            <div className="space-y-3">
              {[
                { level: 'Level 1: Co-Pilot', desc: 'Require approval for EVERY action and content generation.', active: false },
                { level: 'Level 3: Guided', desc: 'Agents run autonomously within a stage, but require approval to move to the next stage.', active: true },
                { level: 'Level 5: Full Auto', desc: 'Agents run end-to-end. Only alerts on high-risk compliance issues.', active: false },
              ].map((lvl, i) => (
                <div key={i} className="p-4 rounded-xl border-2 cursor-pointer transition-all hover:bg-white/5" style={{borderColor: lvl.active ? '#3b82f6' : 'rgba(255,255,255,0.05)', background: lvl.active ? 'rgba(59,130,246,0.05)' : 'transparent'}}>
                  <div className="font-semibold text-sm mb-1">{lvl.level}</div>
                  <div className="text-xs text-slate-400">{lvl.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {tab === 'integrations' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            { name: 'Amazon KDP', desc: 'Direct publishing & metadata sync', status: 'Connected', color: '#f59e0b' },
            { name: 'Etsy API', desc: 'Auto-list printables & journals', status: 'Connect', color: '#f97316' },
            { name: 'Midjourney', desc: 'AI Cover generation (BYO API key)', status: 'Connect', color: '#8b5cf6' },
          ].map(int => (
            <div key={int.name} className="p-5 rounded-xl flex items-center justify-between" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
              <div>
                <div className="font-semibold text-sm">{int.name}</div>
                <div className="text-xs text-slate-400 mt-1">{int.desc}</div>
              </div>
              <button className="px-3 py-1.5 rounded-lg text-xs font-semibold" style={{background: int.status === 'Connected' ? 'rgba(16,185,129,0.1)' : 'rgba(255,255,255,0.05)', color: int.status === 'Connected' ? '#10b981' : 'white'}}>
                {int.status}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
