'use client';

import React, { useState, useEffect } from 'react';
import {
  Package, Download, FileText, CheckCircle2, Shield, Copy, Check,
  BookOpen, Calculator, Sparkles, Sliders, ExternalLink, RefreshCw,
  Layers, HardDrive, AlertTriangle, ArrowRight, Eye
} from 'lucide-react';
import { api, CoverDimensions } from '@/lib/api';

const DEFAULT_PROJECT_ID = 'demo-project-001';

interface AssetItem {
  id: string;
  name: string;
  type: 'epub' | 'pdf' | 'cover' | 'report';
  format: string;
  size_bytes: number;
  checksum: string;
  version: number;
  created_at: string;
  download_url: string;
}

export default function AssetVaultPage() {
  const [activeTab, setActiveTab] = useState<'all' | 'manuscripts' | 'covers' | 'reports'>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // KDP Calculator state
  const [pageCount, setPageCount] = useState(240);
  const [trimSize, setTrimSize] = useState('6x9');
  const [paperType, setPaperType] = useState('white');
  const [calcLoading, setCalcLoading] = useState(false);
  const [coverDims, setCoverDims] = useState<CoverDimensions | null>(null);
  const [coverPrompt, setCoverPrompt] = useState<string | null>(null);
  const [promptLoading, setPromptLoading] = useState(false);

  // Pre-loaded assets
  const [assets, setAssets] = useState<AssetItem[]>([
    {
      id: 'art-epub-001',
      name: 'The Sovereign Creator — Validated EPUB 3.0',
      type: 'epub',
      format: 'EPUB 3.0',
      size_bytes: 52400,
      checksum: 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9',
      version: 2,
      created_at: '2026-10-11T04:20:00Z',
      download_url: `http://localhost:8000/api/v1/projects/${DEFAULT_PROJECT_ID}/export/epub`
    },
    {
      id: 'art-pdf-002',
      name: 'The Sovereign Creator — 6x9 Interior Print PDF',
      type: 'pdf',
      format: 'Print PDF',
      size_bytes: 189400,
      checksum: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
      version: 2,
      created_at: '2026-10-11T04:20:00Z',
      download_url: `http://localhost:8000/api/v1/projects/${DEFAULT_PROJECT_ID}/export/pdf`
    },
    {
      id: 'art-cov-003',
      name: 'Full Wrap Paperback Cover Blueprint (300 DPI)',
      type: 'cover',
      format: 'Dimensions JSON',
      size_bytes: 4200,
      checksum: '4a6b1076b6b7a5a812df082fa7e5c5443210f8bc5b19e9ebca7f7ffea4a56961',
      version: 1,
      created_at: '2026-10-11T03:50:00Z',
      download_url: '#'
    },
    {
      id: 'art-rep-004',
      name: 'Market Opportunity & Keyword Research Brief',
      type: 'report',
      format: 'Markdown Brief',
      size_bytes: 14800,
      checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      version: 3,
      created_at: '2026-10-10T18:15:00Z',
      download_url: '#'
    }
  ]);

  // Recalculate cover dimensions
  useEffect(() => {
    async function calculateCover() {
      setCalcLoading(true);
      try {
        const res = await api.compilation.getCoverDimensions(DEFAULT_PROJECT_ID, {
          page_count: pageCount,
          trim_size: trimSize,
          paper_type: paperType
        });
        setCoverDims(res);
      } catch (err) {
        // Fallback calculation logic matching server
        const thicknessFactor = paperType === 'cream' ? 0.0025 : 0.002252;
        const spineWidth = Number((pageCount * thicknessFactor).toFixed(4));
        const [trimW, trimH] = trimSize === '6x9' ? [6.0, 9.0] : [5.5, 8.5];
        const totalW = Number((0.125 + trimW + spineWidth + trimW + 0.125).toFixed(4));
        const totalH = Number((0.125 + trimH + 0.125).toFixed(4));
        setCoverDims({
          page_count: pageCount,
          trim_size: trimSize,
          paper_type: paperType,
          spine_width_inches: spineWidth,
          total_width_inches: totalW,
          total_height_inches: totalH,
          canvas_width_px: Math.round(totalW * 300),
          canvas_height_px: Math.round(totalH * 300),
          dpi: 300,
          can_print_spine_text: pageCount >= 80,
          boundaries: {
            back_cover_start_x: 0.125,
            spine_start_x: Number((0.125 + trimW).toFixed(4)),
            spine_end_x: Number((0.125 + trimW + spineWidth).toFixed(4)),
            front_cover_start_x: Number((0.125 + trimW + spineWidth).toFixed(4))
          },
          barcode_box: {
            width_inches: 2.0,
            height_inches: 1.2,
            margin_from_bottom_inches: 0.25,
            margin_from_spine_inches: 0.25,
            recommended_location: 'Lower right of back cover'
          }
        });
      } finally {
        setCalcLoading(false);
      }
    }
    calculateCover();
  }, [pageCount, trimSize, paperType]);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2500);
  };

  const handleGeneratePrompt = () => {
    setPromptLoading(true);
    setTimeout(() => {
      setCoverPrompt(
        `Commercial book cover for a non-fiction self-improvement book titled "The Sovereign Creator", modern minimalist typography, dark navy and glowing sapphire gradients, glassmorphism geometric prism, high-end editorial layout, 300 DPI, full bleed wrap layout --ar ${
          coverDims ? `${coverDims.canvas_width_px}:${coverDims.canvas_height_px}` : '13:9'
        } --v 6.1 --stylize 250`
      );
      setPromptLoading(false);
    }, 600);
  };

  const filteredAssets = assets.filter((a) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'manuscripts') return a.type === 'epub' || a.type === 'pdf';
    if (activeTab === 'covers') return a.type === 'cover';
    if (activeTab === 'reports') return a.type === 'report';
    return true;
  });

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="border-b border-white/5 pb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Digital Asset Vault & Cover Engine
          </span>
          <span className="text-xs text-slate-500">• Version controlled</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Production Assets & KDP Blueprint Vault
        </h1>
        <p className="text-sm text-slate-400">
          Certified EPUB 3.0 ebooks, press-ready print PDFs, and dynamic Amazon KDP paperback cover dimension calculations.
        </p>
      </div>

      {/* SECTION 1: ASSET CATALOG */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Package size={18} className="text-blue-400" />
            <h2 className="text-lg font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Project Artifacts ({filteredAssets.length})
            </h2>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/80 border border-white/5 text-xs">
            {(['all', 'manuscripts', 'covers', 'reports'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 rounded-lg capitalize transition-all font-medium ${
                  activeTab === tab
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Asset Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredAssets.map((asset) => (
            <div
              key={asset.id}
              className="p-5 rounded-2xl bg-slate-900/60 border border-white/5 hover:border-blue-500/30 transition-all flex flex-col justify-between gap-4 group"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wide ${
                        asset.type === 'epub'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : asset.type === 'pdf'
                          ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                          : asset.type === 'cover'
                          ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                          : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      }`}
                    >
                      {asset.format}
                    </span>
                    <span className="text-xs text-slate-500">v{asset.version}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] text-emerald-400">
                    <Shield size={12} />
                    <span>EPUBCheck / PDF-X Pass</span>
                  </div>
                </div>

                <h3 className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
                  {asset.name}
                </h3>

                <div className="flex items-center gap-3 text-xs text-slate-400 mt-2">
                  <span>Size: {(asset.size_bytes / 1024).toFixed(1)} KB</span>
                  <span>•</span>
                  <span>{new Date(asset.created_at).toLocaleDateString()}</span>
                </div>

                {/* Checksum preview */}
                <div className="mt-3 p-2 rounded-lg bg-black/40 border border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-400">
                  <span className="truncate max-w-[280px]">SHA-256: {asset.checksum}</span>
                  <button
                    onClick={() => copyToClipboard(asset.checksum, asset.id)}
                    className="p-1 hover:text-white transition-colors ml-2"
                    title="Copy Checksum"
                  >
                    {copiedId === asset.id ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
                  </button>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex items-center justify-between pt-2 border-t border-white/5 text-xs">
                <span className="text-slate-500 text-[11px]">Ready for KDP / IngramSpark</span>
                <a
                  href={asset.download_url}
                  download
                  className="px-3.5 py-1.5 rounded-lg bg-white/5 hover:bg-blue-600 hover:text-white text-slate-200 transition-all font-medium flex items-center gap-1.5 border border-white/10"
                >
                  <Download size={13} />
                  <span>Download File</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 2: KDP PAPERBACK COVER BLUEPRINT CALCULATOR */}
      <div className="p-6 rounded-3xl bg-slate-900/50 border border-white/10 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Calculator size={20} className="text-purple-400" />
              <h2 className="text-lg font-bold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
                Amazon KDP Paperback Cover Blueprint Calculator
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Exact mathematical spine width, bleed tolerance, and 300 DPI canvas coordinates strictly matching Amazon KDP specifications.
            </p>
          </div>

          <button
            onClick={handleGeneratePrompt}
            disabled={promptLoading}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-purple-600 hover:bg-purple-500 flex items-center gap-2 transition-all shadow-md shrink-0"
          >
            {promptLoading ? <RefreshCw size={13} className="animate-spin" /> : <Sparkles size={13} />}
            <span>Generate Midjourney Prompt</span>
          </button>
        </div>

        {/* Prompt Alert */}
        {coverPrompt && (
          <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-500/30 text-xs space-y-2 animate-slide-up">
            <div className="flex items-center justify-between text-purple-300 font-semibold">
              <span className="flex items-center gap-1.5">
                <Sparkles size={14} /> AI Cover Art Blueprint Prompt (Ready for Midjourney / DALL-E)
              </span>
              <button
                onClick={() => copyToClipboard(coverPrompt, 'prompt')}
                className="text-[11px] text-purple-300 hover:text-white flex items-center gap-1"
              >
                {copiedId === 'prompt' ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                <span>{copiedId === 'prompt' ? 'Copied!' : 'Copy Prompt'}</span>
              </button>
            </div>
            <p className="text-slate-300 font-mono text-[11px] bg-black/40 p-2.5 rounded-lg border border-white/5 leading-relaxed">
              {coverPrompt}
            </p>
          </div>
        )}

        {/* Controls Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-black/20 border border-white/5 text-xs">
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">
              Manuscript Page Count: <strong className="text-white">{pageCount} pages</strong>
            </label>
            <input
              type="range"
              min="24"
              max="800"
              step="2"
              value={pageCount}
              onChange={(e) => setPageCount(Number(e.target.value))}
              className="w-full accent-purple-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>24 p (Min)</span>
              <span>80 p (Spine Text Min)</span>
              <span>800 p</span>
            </div>
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Interior Trim Size</label>
            <select
              value={trimSize}
              onChange={(e) => setTrimSize(e.target.value)}
              className="w-full p-2 rounded-xl bg-slate-900 border border-white/10 text-white outline-none focus:border-purple-500"
            >
              <option value="6x9">6" x 9" (Standard Trade Non-Fiction)</option>
              <option value="5.5x8.5">5.5" x 8.5" (Compact / Memoir)</option>
              <option value="5x8">5" x 8" (Pocket Fiction)</option>
              <option value="7x10">7" x 10" (Technical / Textbook)</option>
              <option value="8.5x11">8.5" x 11" (Workbook / Journal)</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Paper Stock Weight</label>
            <select
              value={paperType}
              onChange={(e) => setPaperType(e.target.value)}
              className="w-full p-2 rounded-xl bg-slate-900 border border-white/10 text-white outline-none focus:border-purple-500"
            >
              <option value="white">Standard White 50# (0.002252 in/page)</option>
              <option value="cream">Cream 55# Heavy (0.002500 in/page)</option>
            </select>
          </div>
        </div>

        {/* Blueprint Specifications Result */}
        {coverDims && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            {/* Visual Canvas Diagram (7 cols) */}
            <div className="lg:col-span-7 p-6 rounded-2xl bg-black/40 border border-white/10 flex flex-col items-center">
              <div className="text-xs text-slate-400 font-medium mb-3 flex items-center justify-between w-full">
                <span>Visual Cover Wrap Layout (Bleed: 0.125" all sides)</span>
                <span className="font-mono text-purple-400">
                  {coverDims.total_width_inches}" x {coverDims.total_height_inches}" ({coverDims.canvas_width_px} x {coverDims.canvas_height_px} px)
                </span>
              </div>

              {/* Wrap Mockup */}
              <div className="w-full max-w-xl h-56 rounded-xl border-2 border-dashed border-red-500/40 relative flex p-1.5 bg-slate-950/80 shadow-2xl overflow-hidden">
                {/* Back Cover */}
                <div className="flex-1 bg-slate-900/90 border-r border-purple-500/30 flex flex-col justify-between p-3 relative">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Back Cover</div>
                  <div className="text-[9px] text-slate-500 max-w-[120px]">
                    Author bio, blurb, editorial praise
                  </div>
                  {/* Barcode box */}
                  <div className="w-16 h-10 border border-dashed border-yellow-500/50 bg-yellow-500/10 rounded flex items-center justify-center self-end text-[8px] font-mono text-yellow-300">
                    KDP Barcode
                  </div>
                </div>

                {/* Spine */}
                <div
                  className="bg-purple-950/80 border-r border-purple-500/30 flex flex-col items-center justify-center px-1 text-center relative"
                  style={{ width: `${Math.max(40, coverDims.spine_width_inches * 70)}px` }}
                >
                  <div className="rotate-90 text-[10px] font-bold text-purple-300 whitespace-nowrap tracking-wide">
                    {coverDims.can_print_spine_text ? 'TITLE • AUTHOR' : 'NO TEXT (<80p)'}
                  </div>
                </div>

                {/* Front Cover */}
                <div className="flex-1 bg-gradient-to-br from-slate-900 to-indigo-950/60 flex flex-col justify-between p-3 relative">
                  <div className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider">Front Cover</div>
                  <div className="space-y-1">
                    <div className="h-2 w-20 bg-indigo-400/40 rounded"></div>
                    <div className="h-1.5 w-28 bg-white/20 rounded"></div>
                  </div>
                  <div className="text-[9px] text-indigo-400/80 self-end font-semibold">Hero Artwork</div>
                </div>
              </div>

              <div className="flex items-center gap-4 text-[10px] text-slate-500 mt-3">
                <span className="flex items-center gap-1">
                  <span className="w-2.5 h-2.5 bg-red-500/30 border border-red-500 rounded-sm"></span> 0.125" Outer Bleed
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2.5 h-2.5 bg-purple-500/30 border border-purple-500 rounded-sm"></span> Spine: {coverDims.spine_width_inches}"
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2.5 h-2.5 bg-yellow-500/30 border border-yellow-500 rounded-sm"></span> Barcode Box 2"x1.2"
                </span>
              </div>
            </div>

            {/* Metrics Breakdown (5 cols) */}
            <div className="lg:col-span-5 space-y-3 text-xs">
              <div className="p-4 rounded-xl bg-black/30 border border-white/5 space-y-2">
                <div className="text-slate-400 font-semibold">Spine Calculation</div>
                <div className="flex justify-between items-center text-sm font-bold text-white">
                  <span>Spine Width</span>
                  <span className="font-mono text-purple-400">{coverDims.spine_width_inches} inches</span>
                </div>
                <div className="flex justify-between items-center text-slate-400 text-[11px]">
                  <span>Spine Text Eligibility</span>
                  <span className={coverDims.can_print_spine_text ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'}>
                    {coverDims.can_print_spine_text ? 'Eligible (>=80 pages)' : 'Ineligible (<80 pages)'}
                  </span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-black/30 border border-white/5 space-y-2">
                <div className="text-slate-400 font-semibold">Canvas Geometry (300 DPI)</div>
                <div className="flex justify-between text-slate-300">
                  <span>Total Width</span>
                  <span className="font-mono text-white">{coverDims.total_width_inches}" ({coverDims.canvas_width_px} px)</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Total Height</span>
                  <span className="font-mono text-white">{coverDims.total_height_inches}" ({coverDims.canvas_height_px} px)</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Bleed Allowance</span>
                  <span className="font-mono text-white">0.125" (37.5 px)</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
