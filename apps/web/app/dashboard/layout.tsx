'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { UserButton, useUser } from '@clerk/nextjs';
import {
  LayoutDashboard, FolderOpen, Search, PenTool, Package,
  Store, Megaphone, Users, CheckSquare, BarChart3, Settings,
  BookOpen, Menu, X, ChevronRight, Bell
} from 'lucide-react';
import { useState } from 'react';

const NAV_GROUPS = [
  {
    label: 'Workspace',
    items: [
      { href: '/dashboard', label: 'Command Center', icon: LayoutDashboard },
      { href: '/dashboard/projects', label: 'Projects', icon: FolderOpen },
      { href: '/dashboard/research', label: 'Research', icon: Search },
    ]
  },
  {
    label: 'Creation',
    items: [
      { href: '/dashboard/writing', label: 'Writing Studio', icon: PenTool },
      { href: '/dashboard/assets', label: 'Assets', icon: Package },
    ]
  },
  {
    label: 'Publishing',
    items: [
      { href: '/dashboard/marketplace', label: 'Marketplace Studio', icon: Store },
    ]
  },
  {
    label: 'Growth',
    items: [
      { href: '/dashboard/marketing', label: 'Marketing', icon: Megaphone },
      { href: '/dashboard/audience', label: 'AudienceOS', icon: Users, badge: 'Phase 2' },
    ]
  },
  {
    label: 'Operations',
    items: [
      { href: '/dashboard/approvals', label: 'Approvals', icon: CheckSquare, badge: '3' },
      { href: '/dashboard/analytics', label: 'Analytics', icon: BarChart3 },
      { href: '/dashboard/settings', label: 'Settings', icon: Settings },
    ]
  },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user } = useUser();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5" style={{borderBottom:'1px solid rgba(255,255,255,0.06)'}}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{background:'linear-gradient(135deg,#3b82f6,#8b5cf6)'}}>
          <BookOpen size={16} color="white" />
        </div>
        <div>
          <div className="font-bold text-sm" style={{fontFamily:'Outfit,sans-serif'}}>Kindlepreneur</div>
          <div className="text-[10px]" style={{color:'#475569'}}>v2.0 Publishing OS</div>
        </div>
      </div>

      {/* Nav Groups */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        {NAV_GROUPS.map(group => (
          <div key={group.label} className="mb-6">
            <div className="px-2 mb-2 text-[10px] font-semibold uppercase tracking-widest" style={{color:'#374151'}}>{group.label}</div>
            {group.items.map(item => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link key={item.href} href={item.href}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-xl mb-0.5 text-sm font-medium transition-all"
                  style={active ? {background:'rgba(59,130,246,0.12)',color:'#93c5fd',borderLeft:'2px solid #3b82f6'} : {color:'#64748b'}}
                  onClick={() => setMobileOpen(false)}
                >
                  <Icon size={16} style={{flexShrink:0}} />
                  <span className="flex-1">{item.label}</span>
                  {'badge' in item && item.badge && (
                    <span className="px-1.5 py-0.5 rounded-md text-[10px] font-bold" style={item.badge === 'Soon' ? {background:'rgba(139,92,246,0.15)',color:'#a78bfa'} : {background:'rgba(239,68,68,0.15)',color:'#f87171'}}>{item.badge}</span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="px-4 py-4" style={{borderTop:'1px solid rgba(255,255,255,0.06)'}}>
        <div className="flex items-center gap-3">
          <UserButton afterSignOutUrl="/" />
          <div className="min-w-0">
            <div className="text-sm font-medium truncate">{user?.firstName || 'Publisher'} {user?.lastName || ''}</div>
            <div className="text-[11px] px-1.5 py-0.5 rounded inline-block mt-0.5" style={{background:'rgba(59,130,246,0.1)',color:'#60a5fa'}}>Free Plan</div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen overflow-hidden" style={{background:'#020617'}}>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 flex-shrink-0" style={{background:'rgba(9,14,28,0.95)',borderRight:'1px solid rgba(255,255,255,0.06)'}}>
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0" style={{background:'rgba(0,0,0,0.7)'}} onClick={() => setMobileOpen(false)} />
          <aside className="relative flex flex-col w-64 h-full" style={{background:'rgba(9,14,28,0.98)',borderRight:'1px solid rgba(255,255,255,0.06)'}}>
            <button className="absolute top-4 right-4" onClick={() => setMobileOpen(false)}><X size={20} style={{color:'#64748b'}} /></button>
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="flex-shrink-0 h-14 flex items-center px-4 sm:px-6 gap-4" style={{borderBottom:'1px solid rgba(255,255,255,0.06)',background:'rgba(2,6,23,0.8)',backdropFilter:'blur(10px)'}}>
          <button className="lg:hidden" onClick={() => setMobileOpen(true)}><Menu size={20} style={{color:'#64748b'}} /></button>
          {/* Breadcrumb */}
          <div className="flex items-center gap-1 text-sm" style={{color:'#64748b'}}>
            <span>Dashboard</span>
            {pathname !== '/dashboard' && (
              <>
                <ChevronRight size={14} />
                <span style={{color:'#cbd5e1'}} className="capitalize">{pathname.split('/').filter(Boolean).slice(1).join(' / ')}</span>
              </>
            )}
          </div>
          <div className="flex-1" />
          <button className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-white/5" style={{color:'#64748b'}}>
            <Bell size={16} />
          </button>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}
