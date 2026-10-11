'use client';
import { Search, TrendingUp, BarChart, FileText } from 'lucide-react';

export default function ResearchPage() {
  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold" style={{fontFamily:'Outfit,sans-serif'}}>Market Research</h1>
        <p className="text-sm" style={{color:'#64748b'}}>AI-powered market intelligence and opportunity scoring.</p>
      </div>

      {/* Search Bar */}
      <div className="p-1 rounded-xl flex items-center" style={{background:'rgba(15,23,42,0.8)',border:'1px solid rgba(255,255,255,0.1)'}}>
        <div className="pl-4 pr-2"><Search size={18} style={{color:'#64748b'}} /></div>
        <input type="text" placeholder="Enter a niche or topic (e.g. 'Stoicism for teens')" className="flex-1 bg-transparent border-none outline-none py-3 text-sm" />
        <button className="px-6 py-2 rounded-lg text-sm font-semibold mr-1 transition-all hover:scale-105" style={{background:'linear-gradient(135deg,#3b82f6,#8b5cf6)',color:'white'}}>
          Run Analysis
        </button>
      </div>

      {/* Demo Report */}
      <div className="mt-8 space-y-6">
        <h2 className="text-lg font-semibold flex items-center gap-2"><TrendingUp size={18} className="text-blue-500" /> Recent Reports</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Card */}
          <div className="lg:col-span-2 p-6 rounded-2xl" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-xl font-bold mb-1" style={{fontFamily:'Outfit,sans-serif'}}>ADHD Organization Strategies</h3>
                <div className="text-sm text-slate-400">Analyzed 1,420 Amazon listings • 3 hours ago</div>
              </div>
              <div className="w-16 h-16 rounded-full border-4 flex items-center justify-center font-bold text-lg" style={{borderColor:'#10b981',color:'#10b981'}}>
                8.2
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="p-4 rounded-xl bg-black/20">
                <div className="text-xs text-slate-400 mb-1">Search Volume</div>
                <div className="font-bold text-lg text-blue-400">High</div>
              </div>
              <div className="p-4 rounded-xl bg-black/20">
                <div className="text-xs text-slate-400 mb-1">Competition</div>
                <div className="font-bold text-lg text-orange-400">Medium</div>
              </div>
              <div className="p-4 rounded-xl bg-black/20">
                <div className="text-xs text-slate-400 mb-1">Est. Royalty/mo</div>
                <div className="font-bold text-lg text-emerald-400">$800-1.2k</div>
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed mb-4">
              <strong>AI Insight:</strong> Strong demand for actionable, visual-heavy organization systems. Most competitors have poor formatting or read like medical textbooks. High opportunity for a workbook/interactive format.
            </p>
            
            <button className="text-sm font-medium text-blue-400 hover:text-blue-300">View Full 12-Page Report →</button>
          </div>
          
          {/* Side Cards */}
          <div className="space-y-4">
            <div className="p-4 rounded-xl flex items-center gap-4" style={{background:'rgba(15,23,42,0.4)',border:'1px solid rgba(255,255,255,0.04)'}}>
              <div className="p-3 rounded-lg bg-blue-500/10 text-blue-400"><FileText size={20} /></div>
              <div>
                <div className="font-semibold text-sm">Vegan Keto Recipes</div>
                <div className="text-xs text-slate-400">Score: 4.5 • High Comp</div>
              </div>
            </div>
            <div className="p-4 rounded-xl flex items-center gap-4" style={{background:'rgba(15,23,42,0.4)',border:'1px solid rgba(255,255,255,0.04)'}}>
              <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400"><FileText size={20} /></div>
              <div>
                <div className="font-semibold text-sm">Prompt Engineering 101</div>
                <div className="text-xs text-slate-400">Score: 9.1 • Trending</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
