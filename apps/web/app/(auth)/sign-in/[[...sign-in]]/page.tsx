import { SignIn } from '@clerk/nextjs';
import { BookOpen } from 'lucide-react';

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center" style={{background:'#020617'}}>
      <div className="absolute inset-0" style={{backgroundImage:'radial-gradient(circle at 50% 30%, rgba(59,130,246,0.08) 0%, transparent 60%)'}} />
      <div className="relative z-10 w-full max-w-md px-6">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <BookOpen size={24} style={{color:'#3b82f6'}} />
            <span className="font-bold text-xl" style={{fontFamily:'Outfit,sans-serif'}}>Kindlepreneur 2.0</span>
          </div>
          <p style={{color:'#64748b'}} className="text-sm">Sign in to your publishing command center</p>
        </div>
        <SignIn afterSignInUrl="/dashboard" />
      </div>
    </div>
  );
}
