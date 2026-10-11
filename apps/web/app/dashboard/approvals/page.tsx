'use client';
import { useState } from 'react';
import { CheckSquare, AlertTriangle, ArrowRight, ExternalLink } from 'lucide-react';

const DEMO_APPROVALS = [
  { id: 'apr-1', project: 'Mindful Productivity', type: 'Opportunity Report', title: 'Market Validation Check', desc: 'Agent scored this niche 8.5/10. High demand, medium competition. Proceed to Outline?', risk: 'low', date: '2h ago' },
  { id: 'apr-2', project: 'Etsy Planners 2024', type: 'Metadata', title: 'Review KDP Keywords', desc: '7 backend keywords generated. Review for trademark compliance before final export.', risk: 'medium', date: '5h ago' },
];

export default function ApprovalsPage() {
  const [filter, setFilter] = useState('pending');

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold" style={{fontFamily:'Outfit,sans-serif'}}>Approvals Inbox</h1>
        <p className="text-sm" style={{color:'#64748b'}}>Review and unblock AI agents waiting on your decision.</p>
      </div>

      <div className="flex gap-4 border-b border-white/10 pb-2">
        <button className="pb-2 text-sm font-medium border-b-2 border-blue-500 text-white">Pending (2)</button>
        <button className="pb-2 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white">History</button>
      </div>

      <div className="space-y-4">
        {DEMO_APPROVALS.map(apr => (
          <div key={apr.id} className="p-5 rounded-2xl flex flex-col md:flex-row gap-6 items-start" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{background:'rgba(59,130,246,0.1)',color:'#93c5fd'}}>{apr.project}</span>
                <span className="text-xs" style={{color:'#64748b'}}>• {apr.date}</span>
              </div>
              <h3 className="text-lg font-bold mb-1" style={{fontFamily:'Outfit,sans-serif'}}>{apr.title}</h3>
              <p className="text-sm mb-4" style={{color:'#94a3b8'}}>{apr.desc}</p>
              <button className="text-sm flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors">
                View Artifact <ExternalLink size={14} />
              </button>
            </div>
            
            <div className="w-full md:w-64 flex flex-col gap-2 p-4 rounded-xl" style={{background:'rgba(0,0,0,0.2)'}}>
              <div className="flex items-center gap-2 text-xs mb-2">
                <AlertTriangle size={14} style={{color: apr.risk === 'low' ? '#10b981' : '#f59e0b'}} />
                <span style={{color: apr.risk === 'low' ? '#10b981' : '#f59e0b'}}>Risk Level: {apr.risk.toUpperCase()}</span>
              </div>
              <button className="w-full py-2 rounded-lg text-sm font-semibold transition-colors hover:bg-emerald-600" style={{background:'#10b981',color:'white'}}>
                Approve & Continue
              </button>
              <button className="w-full py-2 rounded-lg text-sm font-semibold transition-colors hover:bg-white/10" style={{border:'1px solid rgba(255,255,255,0.1)',color:'#f87171'}}>
                Reject / Revise
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
