import React from 'react';
import {
    Grid, Layout, FolderOpen, Save, Sparkles, RotateCw,
    EyeOff, Eye, Box
} from 'lucide-react';

const Toolbar = ({
    snapToGrid,
    setSnapToGrid,
    setIsSetupModalOpen,
    openLoadModal,
    saveProject,
    performVastuAudit,
    isAnalyzing,
    activeSurface,
    hideCeiling,
    setHideCeiling,
    invisibleWalls,
    setInvisibleWalls
}) => {
    return (
        <div className="glass-panel z-20 border-b border-gray-200 px-6 py-3 flex flex-wrap items-center justify-between gap-4 shadow-sm min-h-16 animate-fade-in">
            <div className="flex items-center gap-6 flex-wrap">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-a2s-charcoal rounded-lg flex items-center justify-center shadow-lg">
                        <Box size={20} className="text-a2s-gold" />
                    </div>
                    <h1 className="font-serif text-xl font-bold text-a2s-charcoal tracking-tight">3D Studio</h1>
                </div>

                <div className="h-6 w-px bg-gray-200 hidden md:block" />

                <label className="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-widest cursor-pointer hover:text-a2s-gold transition-colors">
                    <input
                        type="checkbox"
                        checked={snapToGrid}
                        onChange={(e) => setSnapToGrid(e.target.checked)}
                        className="rounded border-gray-300 text-a2s-gold focus:ring-a2s-gold/20 w-4 h-4"
                    />
                    <Grid size={16} /> Snap to Grid
                </label>
            </div>

            <div className="flex items-center gap-3">
                {activeSurface === '3d' && (
                    <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-full border border-gray-100 mr-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none">Live Scene</span>
                    </div>
                )}

                <div className="flex items-center gap-2 bg-gray-100/50 p-1 rounded-xl border border-gray-200 backdrop-blur-sm">
                    <button
                        onClick={() => setIsSetupModalOpen(true)}
                        className="flex items-center gap-1.5 px-3 py-2 bg-white text-a2s-charcoal rounded-lg hover:bg-a2s-gold hover:text-white border border-gray-200 text-xs font-bold transition-all shadow-sm active:scale-95"
                        title="Start a new room design"
                    >
                        <Layout size={14} /> New Room
                    </button>
                    <button onClick={openLoadModal} className="flex items-center gap-1.5 px-3 py-2 bg-white text-a2s-charcoal rounded-lg hover:bg-a2s-gold hover:text-white border border-gray-200 text-xs font-bold transition-all shadow-sm active:scale-95">
                        <FolderOpen size={14} /> Load
                    </button>
                    <button onClick={saveProject} className="flex items-center gap-1.5 px-3 py-2 bg-white text-a2s-charcoal rounded-lg hover:bg-a2s-gold hover:text-white border border-gray-200 text-xs font-bold transition-all shadow-sm active:scale-95">
                        <Save size={14} /> Save
                    </button>
                </div>

                <button
                    onClick={performVastuAudit}
                    disabled={isAnalyzing}
                    className="flex items-center gap-2 px-5 py-2.5 bg-a2s-charcoal text-white rounded-xl hover:bg-gray-800 text-xs font-bold transition-all shadow-lg hover:shadow-a2s-gold/20 active:scale-95 group"
                >
                    {isAnalyzing ? <RotateCw className="animate-spin" size={16} /> : <Sparkles size={16} className="text-a2s-gold group-hover:scale-110 transition" />}
                    Vastu Audit
                </button>
            </div>

            {/* Visibility Toggles (3D only) */}
            {activeSurface === '3d' && (
                <div className="flex items-center gap-4 border-l border-gray-200 pl-6 ml-2">
                    <button
                        onClick={() => setHideCeiling(!hideCeiling)}
                        className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold transition-all shadow-sm ${hideCeiling ? 'bg-amber-100 text-amber-700 border border-amber-200' : 'bg-gray-100 text-gray-500 border border-transparent hover:bg-gray-200'}`}
                        title="Toggle ceiling visibility"
                    >
                        {hideCeiling ? <EyeOff size={14} /> : <Eye size={14} />} Ceiling
                    </button>

                    <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mr-1 opacity-60">Walls</span>
                        <div className="flex items-center p-0.5 bg-gray-100 rounded-lg border border-gray-200">
                            {['N', 'S', 'E', 'W'].map(dir => {
                                const wallId = `wall-${dir.toLowerCase()}`;
                                const isHidden = invisibleWalls.includes(wallId);
                                return (
                                    <button
                                        key={dir}
                                        onClick={() => setInvisibleWalls(prev => isHidden ? prev.filter(w => w !== wallId) : [...prev, wallId])}
                                        className={`w-7 h-7 flex items-center justify-center rounded-md text-[10px] font-black transition-all ${isHidden ? 'bg-red-500 text-white shadow-inner' : 'text-gray-400 hover:text-a2s-charcoal hover:bg-white'}`}
                                    >
                                        {dir}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Toolbar;
