'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Star, PenTool, CheckCircle, ArrowRight, ArrowLeft, Loader2, Sparkles } from 'lucide-react';

const PROJECT_TYPES = [
  { id: 'nonfiction_book', name: 'Non-Fiction Book', icon: BookOpen, desc: 'Expertise, guides, self-help, business.' },
  { id: 'fiction_book', name: 'Fiction Novel', icon: PenTool, desc: 'Story-driven, character arcs, world building.' },
  { id: 'low_content_journal', name: 'Low Content / Journal', icon: Star, desc: 'Planners, trackers, notebooks for Etsy/KDP.' },
];

export default function NewProjectWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    type: 'nonfiction_book',
    name: '',
    description: '',
    targetAudience: '',
    tone: 'professional'
  });

  const handleNext = () => setStep(s => Math.min(s + 1, 4));
  const handlePrev = () => setStep(s => Math.max(s - 1, 1));

  const handleCreate = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      router.push('/dashboard/projects/proj-new');
    }, 1500);
  };

  return (
    <div className="max-w-3xl mx-auto py-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2" style={{fontFamily:'Outfit,sans-serif'}}>Create New Project</h1>
        
        {/* Progress */}
        <div className="flex items-center gap-2 mt-6">
          {[1,2,3,4].map(s => (
            <div key={s} className="flex-1 h-1.5 rounded-full" style={{background: s <= step ? '#3b82f6' : 'rgba(255,255,255,0.06)'}} />
          ))}
        </div>
        <div className="flex justify-between text-xs mt-2" style={{color:'#64748b'}}>
          <span>Type</span>
          <span>Details</span>
          <span>Settings</span>
          <span>Review</span>
        </div>
      </div>

      <div className="p-6 md:p-8 rounded-2xl" style={{background:'rgba(15,23,42,0.6)',border:'1px solid rgba(255,255,255,0.06)'}}>
        {step === 1 && (
          <div className="space-y-6 animate-slide-in-right">
            <h2 className="text-xl font-semibold mb-4" style={{fontFamily:'Outfit,sans-serif'}}>What are you creating?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {PROJECT_TYPES.map(pt => {
                const Icon = pt.icon;
                const active = formData.type === pt.id;
                return (
                  <button key={pt.id} onClick={() => setFormData({...formData, type: pt.id})}
                    className="p-5 rounded-xl text-left transition-all hover:bg-white/5"
                    style={active ? {background:'rgba(59,130,246,0.1)',border:'1px solid #3b82f6'} : {background:'rgba(15,23,42,0.4)',border:'1px solid rgba(255,255,255,0.06)'}}>
                    <Icon size={24} className="mb-3" style={{color: active ? '#60a5fa' : '#64748b'}} />
                    <h3 className="font-semibold mb-1">{pt.name}</h3>
                    <p className="text-xs" style={{color:'#94a3b8'}}>{pt.desc}</p>
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6 animate-slide-in-right">
            <h2 className="text-xl font-semibold mb-4" style={{fontFamily:'Outfit,sans-serif'}}>Project Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Working Title</label>
                <input type="text" className="w-full px-4 py-2 rounded-lg text-sm" placeholder="e.g. Mindful Productivity" style={{background:'rgba(2,6,23,0.5)',border:'1px solid rgba(255,255,255,0.1)',color:'white'}} value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Core Idea / Premise</label>
                <textarea rows={4} className="w-full px-4 py-2 rounded-lg text-sm" placeholder="A brief description of what this book is about..." style={{background:'rgba(2,6,23,0.5)',border:'1px solid rgba(255,255,255,0.1)',color:'white'}} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6 animate-slide-in-right">
            <h2 className="text-xl font-semibold mb-4" style={{fontFamily:'Outfit,sans-serif'}}>Target Audience & Tone</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Target Market</label>
                <input type="text" className="w-full px-4 py-2 rounded-lg text-sm" placeholder="e.g. Young professionals struggling with burnout" style={{background:'rgba(2,6,23,0.5)',border:'1px solid rgba(255,255,255,0.1)',color:'white'}} value={formData.targetAudience} onChange={e => setFormData({...formData, targetAudience: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Writing Tone</label>
                <select className="w-full px-4 py-2 rounded-lg text-sm" style={{background:'rgba(2,6,23,0.5)',border:'1px solid rgba(255,255,255,0.1)',color:'white'}} value={formData.tone} onChange={e => setFormData({...formData, tone: e.target.value})}>
                  <option value="professional">Professional & Authoritative</option>
                  <option value="conversational">Conversational & Friendly</option>
                  <option value="academic">Academic & Data-Driven</option>
                  <option value="humorous">Humorous & Entertaining</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-6 animate-slide-in-right">
            <h2 className="text-xl font-semibold mb-4" style={{fontFamily:'Outfit,sans-serif'}}>Review & Launch</h2>
            <div className="p-4 rounded-xl space-y-4" style={{background:'rgba(2,6,23,0.5)',border:'1px solid rgba(255,255,255,0.06)'}}>
              <div>
                <div className="text-xs" style={{color:'#64748b'}}>Type</div>
                <div className="font-medium capitalize">{formData.type.replace('_', ' ')}</div>
              </div>
              <div>
                <div className="text-xs" style={{color:'#64748b'}}>Title</div>
                <div className="font-medium">{formData.name || 'Untitled'}</div>
              </div>
              <div>
                <div className="text-xs" style={{color:'#64748b'}}>Description</div>
                <div className="text-sm">{formData.description || 'No description provided.'}</div>
              </div>
            </div>
            
            <div className="p-4 rounded-xl flex items-start gap-3" style={{background:'rgba(59,130,246,0.1)',border:'1px solid rgba(59,130,246,0.2)'}}>
              <Sparkles className="mt-0.5 flex-shrink-0" size={16} style={{color:'#3b82f6'}} />
              <div className="text-sm">
                <span className="font-semibold text-blue-400">Next step:</span> Upon creation, the Research Analyst AI will automatically begin scanning market demand and compiling your initial opportunity report.
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-between mt-8 pt-6" style={{borderTop:'1px solid rgba(255,255,255,0.06)'}}>
          <button onClick={handlePrev} disabled={step === 1 || loading} className="px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-white/5 disabled:opacity-50">
            Back
          </button>
          
          {step < 4 ? (
            <button onClick={handleNext} className="flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:scale-105" style={{background:'#3b82f6'}}>
              Next Step <ArrowRight size={16} />
            </button>
          ) : (
            <button onClick={handleCreate} disabled={loading} className="flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:scale-105 disabled:opacity-70" style={{background:'linear-gradient(135deg,#3b82f6,#8b5cf6)'}}>
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
              {loading ? 'Creating...' : 'Create & Start Research'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
