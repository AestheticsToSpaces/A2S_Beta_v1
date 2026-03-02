import React from 'react';
import { Box, Search, Filter } from 'lucide-react';
import { AVAILABLE_CATEGORIES } from './constants';

const AssetLibrary = ({
    activeCategory,
    setActiveCategory,
    activeSurface,
    addItem,
    filteredCatalog
}) => {
    return (
        <div className="w-72 flex-shrink-0 bg-white border-l border-gray-200 flex flex-col z-10 overflow-hidden shadow-sm animate-fade-in">
            {/* Header */}
            <div className="p-4 border-b border-gray-100 bg-gray-50/50">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] flex items-center gap-2">
                        <Box size={12} className="text-a2s-charcoal" /> Asset Library
                    </h3>
                </div>
                {/* Category Pills */}
                <div className="flex flex-wrap gap-1.5">
                    {AVAILABLE_CATEGORIES.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setActiveCategory(cat)}
                            className={`text-[10px] px-2.5 py-1.5 rounded-lg font-bold transition-all duration-200 ${activeCategory === cat ? 'bg-a2s-charcoal text-white shadow-md' : 'bg-white text-gray-500 border border-gray-200 hover:border-a2s-gold hover:text-a2s-charcoal'}`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            </div>

            {/* Hint Box */}
            {activeSurface === '3d' && (
                <div className="mx-4 mt-4 p-3 bg-blue-50/50 border border-blue-100 rounded-xl">
                    <p className="text-[10px] text-blue-600 font-medium leading-relaxed italic">
                        Tip: Adding an item will switch the view to its placement surface (Floor or Wall).
                    </p>
                </div>
            )}

            {/* Grid */}
            <div className="flex-grow min-h-0 overflow-y-auto p-4 grid grid-cols-2 gap-3 content-start custom-scrollbar">
                {filteredCatalog.map(item => (
                    <button
                        key={item.id}
                        onClick={() => addItem(item)}
                        className="group flex flex-col items-center justify-center p-4 rounded-2xl border border-gray-100 hover:border-a2s-gold hover:bg-a2s-gold/5 transition-all duration-300 bg-white shadow-sm hover:shadow-luxury relative overflow-hidden active:scale-95"
                    >
                        {/* Selected Indicator Background */}
                        <div className="absolute inset-0 bg-gradient-to-br from-a2s-gold/0 to-a2s-gold/10 opacity-0 group-hover:opacity-100 transition-opacity" />

                        <div className="mb-3 p-3 bg-gray-50 rounded-xl group-hover:bg-white group-hover:shadow-sm transition-all relative z-10">
                            {item.icon ? React.cloneElement(item.icon, { size: 24, className: 'text-gray-700 group-hover:text-a2s-gold transition-colors' }) : <Box size={24} />}
                        </div>

                        <span className="text-[10px] font-bold text-a2s-charcoal text-center leading-tight mb-1 relative z-10">{item.name}</span>
                        <div className="flex items-center gap-1 opacity-40 group-hover:opacity-100 transition-opacity relative z-10">
                            <span className="text-[8px] font-black uppercase tracking-tighter text-gray-500">{item.width} × {item.depth || item.height || '0'} cm</span>
                        </div>
                    </button>
                ))}

                {filteredCatalog.length === 0 && (
                    <div className="col-span-2 flex flex-col items-center justify-center py-20 px-6 text-center opacity-40">
                        <Filter size={32} className="mb-2 text-gray-300" />
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">No matches found</p>
                        <p className="text-[9px] text-gray-400 mt-1">Try switching category or surface context.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AssetLibrary;
