import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Heart, IndianRupee, Eye, ArrowUpRight } from 'lucide-react';
import { isDesignSaved, toggleSavedDesign } from '../utils/storage';
import { saveDesign } from '../services/api';

const DesignCard = ({ design, onQuickPreview }) => {
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        setSaved(isDesignSaved(design.id));
    }, [design.id]);

    const handleSaveClick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        // Save to localStorage immediately (instant UI update)
        const isSaved = toggleSavedDesign(design.id);
        setSaved(isSaved);
        // Also persist to backend DB if user is logged in
        if (localStorage.getItem('token')) {
            try {
                await saveDesign(design.id);
            } catch (err) {
                console.warn('Could not sync save to server:', err);
            }
        }
    };

    return (
        <div className="group relative card-luxury overflow-hidden flex flex-col h-full bg-white animate-fade-in-up">
            {/* Image Container */}
            <div className="relative aspect-[4/5] overflow-hidden">
                <img
                    src={design.image}
                    alt={design.title}
                    className="w-full h-full object-cover transition-transform duration-1000 ease-out group-hover:scale-110"
                />

                {/* Immersive Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity duration-500" />

                {/* Floating Meta: Quick Preview and Save */}
                <div className="absolute top-6 right-6 flex flex-col gap-3 z-20">
                    <button
                        type="button"
                        onClick={handleSaveClick}
                        className={`p-3 rounded-full backdrop-blur-xl border border-white/20 transition-all duration-300 ${saved ? 'bg-red-500 text-white shadow-lg' : 'bg-white/10 text-white hover:bg-white hover:text-red-500'}`}
                        aria-label={saved ? 'Unsave design' : 'Save design'}
                    >
                        <Heart size={18} fill={saved ? 'currentColor' : 'none'} />
                    </button>
                    {onQuickPreview && (
                        <button
                            type="button"
                            onClick={(e) => { e.preventDefault(); e.stopPropagation(); onQuickPreview(design); }}
                            className="p-3 rounded-full backdrop-blur-xl bg-white/10 text-white border border-white/20 hover:bg-accent hover:border-accent transition-all duration-500 opacity-0 group-hover:opacity-100 translate-y-[-10px] group-hover:translate-y-0"
                            aria-label="Quick Narrative"
                        >
                            <Eye size={18} />
                        </button>
                    )}
                </div>

                {/* Bottom Overlay Details (revealed on hover) */}
                <div className="absolute bottom-0 left-0 right-0 p-8 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500 z-10">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="w-8 h-px bg-accent" />
                        <span className="text-[9px] font-black text-accent uppercase tracking-[0.4em]">
                            {design.style}
                        </span>
                    </div>

                    <h3 className="font-serif text-2xl md:text-3xl font-black text-white mb-6 leading-tight italic">
                        {design.title}
                    </h3>

                    <div className="flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all duration-500 delay-100">
                        <div className="flex items-center gap-2 text-white/80">
                            <IndianRupee size={14} className="text-accent" />
                            <span className="text-xs font-black uppercase tracking-widest">
                                {design.totalCost.toLocaleString('en-IN')}
                            </span>
                        </div>
                        <Link
                            to={`/design/${design.id}`}
                            className="flex items-center gap-2 text-[9px] font-black text-white uppercase tracking-[0.3em] border-b border-white/30 pb-1 hover:border-accent hover:text-accent transition-colors group/link"
                        >
                            <span>Explore Curation</span>
                            <ArrowUpRight size={12} className="group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
                        </Link>
                    </div>
                </div>
            </div>

            {/* Content for Non-Hover State (Subtle) */}
            <div className="p-6 bg-surface flex flex-col border-t border-gray-50 group-hover:bg-main group-hover:border-main transition-colors duration-500">
                <div className="flex justify-between items-center">
                    <span className="text-[10px] font-black uppercase tracking-widest text-gray-400 group-hover:text-accent transition-colors">
                        {design.roomType}
                    </span>
                    <span className="text-[10px] font-bold text-gray-300 group-hover:text-white/30">
                        {design.products?.length || 0} Pieces
                    </span>
                </div>
            </div>
        </div>
    );
};

export default DesignCard;
