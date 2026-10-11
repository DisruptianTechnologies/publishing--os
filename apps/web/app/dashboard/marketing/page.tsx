'use client';

import React, { useState } from 'react';
import {
  Megaphone, Calendar, Users, DollarSign, CheckCircle2, Clock,
  ArrowRight, ShieldCheck, Sparkles, Send, TrendingUp, AlertCircle,
  HelpCircle, BarChart3, Star, Mail, Check
} from 'lucide-react';

interface ArcReader {
  id: string;
  name: string;
  email: string;
  format: 'EPUB' | 'PDF' | 'MOBI';
  status: 'sent' | 'opened' | 'reviewed';
  rating?: number;
  review_url?: string;
}

export default function MarketingLaunchpadPage() {
  const [selectedStrategy, setSelectedStrategy] = useState<'exclusive' | 'wide'>('exclusive');
  const [bookPrice, setBookPrice] = useState(4.99);
  const [estimatedMonthlySales, setEstimatedMonthlySales] = useState(350);
  const [estimatedKenpPages, setEstimatedKenpPages] = useState(85000);

  // ARC Reader team
  const [arcReaders, setArcReaders] = useState<ArcReader[]>([
    {
      id: 'arc-1',
      name: 'Sarah Jenkins',
      email: 's.jenkins@example.com',
      format: 'EPUB',
      status: 'reviewed',
      rating: 5,
      review_url: 'https://amazon.com/review/R392019'
    },
    {
      id: 'arc-2',
      name: 'Marcus Vance',
      email: 'marcus.v@example.com',
      format: 'PDF',
      status: 'reviewed',
      rating: 5,
      review_url: 'https://amazon.com/review/R491023'
    },
    {
      id: 'arc-3',
      name: 'Elena Rostova',
      email: 'elena.rostova@example.com',
      format: 'EPUB',
      status: 'opened'
    },
    {
      id: 'arc-4',
      name: 'David K.',
      email: 'david.tech@example.com',
      format: 'EPUB',
      status: 'sent'
    }
  ]);

  // Royalty Calculations
  // KDP Select: 70% royalty on sales ($4.99 - $0.15 delivery = $3.34) + KENP at $0.0044/page
  const kdpSaleRoyalty = Number((bookPrice * 0.70 - 0.15).toFixed(2));
  const kdpSalesRevenue = Math.round(estimatedMonthlySales * kdpSaleRoyalty);
  const kenpRevenue = Math.round(estimatedKenpPages * 0.0044);
  const totalKdpSelectRevenue = kdpSalesRevenue + kenpRevenue;

  // Wide: 70% on Amazon + 70% on Apple/Kobo/Google (no KENP, but additional platforms +25% volume)
  const wideSalesVolume = Math.round(estimatedMonthlySales * 1.35);
  const wideRevenue = Math.round(wideSalesVolume * (bookPrice * 0.70));

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="border-b border-white/5 pb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Marketing Launchpad & Distribution
          </span>
          <span className="text-xs text-slate-500">• Launch Day - 14 Days</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Strategic Book Launchpad
        </h1>
        <p className="text-sm text-slate-400">
          Coordinate your 6-week launch roadmap, track Advance Reader Copies (ARC), and optimize KDP Select vs. Wide distribution economics.
        </p>
      </div>

      {/* SECTION 1: 6-WEEK LAUNCH TIMELINE */}
      <div className="p-6 rounded-3xl bg-slate-900/60 border border-white/5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar size={18} className="text-blue-400" />
            <h2 className="text-base font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
              6-Week Launch Roadmap Phase Flow
            </h2>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-300 font-medium">
            Active Phase: Week -2 Pre-Order
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-6 gap-3 pt-2">
          {/* Week -4 */}
          <div className="p-3.5 rounded-2xl bg-black/30 border border-white/5 space-y-2 opacity-80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center justify-between">
              <span>Week -4</span>
              <CheckCircle2 size={13} />
            </div>
            <div className="text-xs font-bold text-white">ARC Recruitment</div>
            <div className="text-[11px] text-slate-400 leading-tight">
              Recruit 50 targeted reviewers & finalize beta manuscript.
            </div>
          </div>

          {/* Week -2 */}
          <div className="p-3.5 rounded-2xl bg-blue-600/20 border border-blue-500/40 space-y-2 relative">
            <div className="text-[10px] font-bold uppercase tracking-wider text-blue-300 flex items-center justify-between">
              <span>Week -2</span>
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
            </div>
            <div className="text-xs font-bold text-white">Pre-Order & Teaser</div>
            <div className="text-[11px] text-slate-300 leading-tight">
              KDP pre-order live, drop chapter 1 to email list.
            </div>
          </div>

          {/* Week -1 */}
          <div className="p-3.5 rounded-2xl bg-black/30 border border-white/5 space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Week -1
            </div>
            <div className="text-xs font-bold text-white">Reviewer Follow-Up</div>
            <div className="text-[11px] text-slate-400 leading-tight">
              Deliver final EPUB copies to ARC team with review reminders.
            </div>
          </div>

          {/* Launch Day */}
          <div className="p-3.5 rounded-2xl bg-black/30 border border-white/5 space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-purple-400">
              Launch Day
            </div>
            <div className="text-xs font-bold text-white">Price Promotion</div>
            <div className="text-[11px] text-slate-400 leading-tight">
              $0.99 launch promo, full newsletter broadcast, social push.
            </div>
          </div>

          {/* Week +1 */}
          <div className="p-3.5 rounded-2xl bg-black/30 border border-white/5 space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Week +1
            </div>
            <div className="text-xs font-bold text-white">Amazon Ads Push</div>
            <div className="text-[11px] text-slate-400 leading-tight">
              Launch exact match sponsored product ads on 10 competitor ASINs.
            </div>
          </div>

          {/* Week +2 */}
          <div className="p-3.5 rounded-2xl bg-black/30 border border-white/5 space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Week +2
            </div>
            <div className="text-xs font-bold text-white">Price Normalization</div>
            <div className="text-[11px] text-slate-400 leading-tight">
              Raise price to $4.99 and audit category bestseller rankings.
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 2 & 3: GRID (ARC TEAM + ROYALTY SIMULATOR) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: ARC Reader Command Center (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="p-5 rounded-3xl bg-slate-900/60 border border-white/5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-white/5">
              <div className="flex items-center gap-2">
                <Users size={18} className="text-emerald-400" />
                <h2 className="text-base font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
                  ARC Review Team Tracker
                </h2>
              </div>
              <span className="text-xs text-slate-400">
                Goal: <strong className="text-white">25 Reviews</strong> (Current: 2)
              </span>
            </div>

            {/* ARC progress meter */}
            <div className="p-3.5 rounded-xl bg-black/30 border border-white/5 space-y-2 text-xs">
              <div className="flex justify-between text-slate-300">
                <span>Reviews Verified</span>
                <span className="text-emerald-400 font-bold">2 / 25 on Day 1</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '8%' }} />
              </div>
            </div>

            {/* Readers Table */}
            <div className="space-y-2">
              {arcReaders.map((reader) => (
                <div
                  key={reader.id}
                  className="p-3 rounded-xl bg-black/20 border border-white/5 flex items-center justify-between gap-3 text-xs"
                >
                  <div>
                    <div className="font-semibold text-white flex items-center gap-2">
                      <span>{reader.name}</span>
                      <span className="px-1.5 py-0.2 rounded bg-white/5 text-[10px] text-slate-400">
                        {reader.format}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500">{reader.email}</div>
                  </div>

                  <div className="flex items-center gap-2">
                    {reader.status === 'reviewed' ? (
                      <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 font-medium flex items-center gap-1 text-[11px]">
                        <Star size={11} className="fill-emerald-400 text-emerald-400" />
                        <span>5★ Verified</span>
                      </span>
                    ) : reader.status === 'opened' ? (
                      <span className="px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 font-medium text-[11px]">
                        Reading (EPUB)
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-md bg-white/5 text-slate-400 text-[11px]">
                        Copy Sent
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 font-semibold text-xs flex items-center justify-center gap-2 transition-all">
              <Mail size={14} />
              <span>Broadcast Reminder to Unread ARC Members</span>
            </button>
          </div>
        </div>

        {/* Right Column: KDP Select vs. Wide Economics Simulator (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="p-5 rounded-3xl bg-slate-900/60 border border-white/5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-white/5">
              <div className="flex items-center gap-2">
                <DollarSign size={18} className="text-yellow-400" />
                <h2 className="text-base font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
                  Distribution Economics Simulator
                </h2>
              </div>
              <div className="flex items-center gap-1 p-0.5 rounded-lg bg-black/40 text-xs">
                <button
                  onClick={() => setSelectedStrategy('exclusive')}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    selectedStrategy === 'exclusive' ? 'bg-yellow-500/20 text-yellow-300 font-bold' : 'text-slate-400'
                  }`}
                >
                  KDP Select
                </button>
                <button
                  onClick={() => setSelectedStrategy('wide')}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    selectedStrategy === 'wide' ? 'bg-blue-500/20 text-blue-300 font-bold' : 'text-slate-400'
                  }`}
                >
                  Go Wide
                </button>
              </div>
            </div>

            {/* Slider Controls */}
            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>List Price: <strong className="text-white">${bookPrice.toFixed(2)}</strong></span>
                  <span className="text-slate-500">70% Royalty Tier</span>
                </div>
                <div className="flex gap-2">
                  {[2.99, 4.99, 9.99].map((p) => (
                    <button
                      key={p}
                      onClick={() => setBookPrice(p)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                        bookPrice === p
                          ? 'bg-yellow-500/20 border-yellow-500/40 text-white font-bold'
                          : 'bg-black/20 border-white/5 text-slate-400 hover:text-white'
                      }`}
                    >
                      ${p.toFixed(2)}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>Est. Monthly Sales: <strong className="text-white">{estimatedMonthlySales} copies</strong></span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="2000"
                  step="50"
                  value={estimatedMonthlySales}
                  onChange={(e) => setEstimatedMonthlySales(Number(e.target.value))}
                  className="w-full accent-yellow-500"
                />
              </div>

              {selectedStrategy === 'exclusive' && (
                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Est. KENP Page Reads: <strong className="text-white">{estimatedKenpPages.toLocaleString()} pages</strong></span>
                    <span className="text-yellow-400/90 font-mono">~$0.0044/page</span>
                  </div>
                  <input
                    type="range"
                    min="10000"
                    max="500000"
                    step="10000"
                    value={estimatedKenpPages}
                    onChange={(e) => setEstimatedKenpPages(Number(e.target.value))}
                    className="w-full accent-yellow-500"
                  />
                </div>
              )}
            </div>

            {/* Projections Card */}
            <div className="p-4 rounded-2xl bg-black/40 border border-white/10 space-y-3">
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                Monthly Revenue Projection
              </div>

              <div className="flex items-baseline justify-between">
                <span className="text-2xl font-bold text-white tracking-tight" style={{ fontFamily: 'Outfit, sans-serif' }}>
                  ${(selectedStrategy === 'exclusive' ? totalKdpSelectRevenue : wideRevenue).toLocaleString()}
                </span>
                <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                  <TrendingUp size={13} />
                  <span>Est. Net Royalty / Month</span>
                </span>
              </div>

              <div className="pt-2 border-t border-white/5 text-[11px] text-slate-400 space-y-1">
                {selectedStrategy === 'exclusive' ? (
                  <>
                    <div className="flex justify-between">
                      <span>Direct KDP Sales ({estimatedMonthlySales} @ ${kdpSaleRoyalty})</span>
                      <span className="text-white font-mono">${kdpSalesRevenue.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Kindle Unlimited KENP ({estimatedKenpPages.toLocaleString()} pages)</span>
                      <span className="text-white font-mono">${kenpRevenue.toLocaleString()}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex justify-between">
                      <span>Amazon Retail (70%)</span>
                      <span className="text-white font-mono">${Math.round(wideRevenue * 0.65).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Apple, Kobo, Barnes & Noble, Google Play (70%)</span>
                      <span className="text-white font-mono">${Math.round(wideRevenue * 0.35).toLocaleString()}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-200">
              💡 <strong>Strategy Recommendation:</strong> For non-fiction with workbook potential, launch 90 days exclusive in KDP Select to maximize KENP page reads and algorithm velocity, then transition wide.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
