import React from 'react';
import {
    Layers, Trash2, Compass, Eye, RotateCcw, RotateCw,
    Box, ChevronRight
} from 'lucide-react';

const Sidebar = ({
    items,
    setItems,
    selectedId,
    setSelectedId,
    CATALOG,
    activeSurface,
    setActiveSurface,
    rotateItem,
    rotateItemCcw,
    deleteItem
}) => {
    return (
        <div className="w-64 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col z-10 overflow-hidden shadow-sm animate-fade-in">
            {/* Header */}
            <div className="p-4 border-b border-gray-100 bg-gray-50/50">
                <div className="flex items-center justify-between mb-1">
                    <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] flex items-center gap-2">
                        <Layers size={12} className="text-a2s-charcoal" /> Scene Hierarchy
                    </h3>
                    <span className="text-[10px] font-bold bg-a2s-charcoal text-white px-2 py-0.5 rounded-full">
                        {items.length}
                    </span>
                </div>
            </div>

            {/* Object List */}
            <div className="flex-grow min-h-0 overflow-y-auto p-3 custom-scrollbar space-y-1">
                {items.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 px-4 text-center opacity-40">
                        <Box size={32} className="mb-2 text-gray-300" />
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Workspace Empty</p>
                        <p className="text-[9px] text-gray-400 mt-1 leading-relaxed">Add items from the library to start designing.</p>
                    </div>
                ) : (
                    items.map(item => {
                        const cat = CATALOG.find(c => c.id === item.catalogId);
                        const name = cat?.name ?? item.catalogId;
                        const isSelected = selectedId === item.id;
                        return (
                            <div
                                key={item.id}
                                onClick={() => setSelectedId(item.id)}
                                className={`group flex items-center justify-between gap-2 px-3 py-2.5 rounded-xl text-xs cursor-pointer transition-all duration-200 ${isSelected ? 'bg-a2s-charcoal text-white shadow-md' : 'hover:bg-gray-100 text-gray-600 border border-transparent hover:border-gray-200'}`}
                            >
                                <div className="flex items-center gap-2 overflow-hidden">
                                    <div className={`p-1.5 rounded-lg transition-colors ${isSelected ? 'bg-white/10' : 'bg-gray-100 group-hover:bg-white'}`}>
                                        {cat?.icon ? React.cloneElement(cat.icon, { size: 12, className: isSelected ? 'text-a2s-gold' : 'text-gray-500' }) : <Box size={12} />}
                                    </div>
                                    <span className="truncate font-medium">{name}</span>
                                </div>
                                <div className="flex items-center">
                                    <button
                                        type="button"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setItems(prev => prev.filter(i => i.id !== item.id));
                                            if (selectedId === item.id) setSelectedId(null);
                                        }}
                                        className={`p-1 rounded-lg transition-all ${isSelected ? 'text-white/40 hover:text-white hover:bg-white/10' : 'text-gray-300 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100'}`}
                                        title="Remove item"
                                    >
                                        <Trash2 size={12} />
                                    </button>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Room Navigation */}
            <div className="p-4 border-t border-gray-100 bg-gray-50/50">
                <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                    <Compass size={12} className="text-a2s-charcoal" /> Perspective
                </h4>
                <div className="grid grid-cols-2 gap-1.5">
                    <button
                        onClick={() => setActiveSurface('3d')}
                        className={`col-span-2 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all ${activeSurface === '3d' ? 'bg-a2s-charcoal text-white shadow-md' : 'bg-white text-gray-500 border border-gray-200 hover:border-a2s-gold/50 hover:text-a2s-charcoal shadow-sm'}`}
                    >
                        <Eye size={14} /> Full 3D View
                    </button>
                    <button
                        onClick={() => setActiveSurface('floor')}
                        className={`py-2 rounded-xl text-xs font-bold transition-all ${activeSurface === 'floor' ? 'bg-a2s-charcoal text-white shadow-md' : 'bg-white text-gray-500 border border-gray-200 hover:border-gray-300 shadow-sm'}`}
                    >
                        Floor
                    </button>
                    <div className="grid grid-cols-2 gap-1 col-span-1">
                        {['n', 's', 'e', 'w'].map(s => (
                            <button
                                key={s}
                                onClick={() => setActiveSurface(`wall-${s}`)}
                                className={`py-2 rounded-lg text-[10px] font-black transition-all ${activeSurface === `wall-${s}` ? 'bg-a2s-charcoal text-white shadow-md' : 'bg-white text-gray-400 border border-gray-200 hover:border-gray-300 shadow-sm'}`}
                            >
                                {s.toUpperCase()}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Transformation Controls */}
            {selectedId && (
                <div className="p-4 border-t border-gray-100 bg-white animate-slide-up">
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-3">Object Controls</p>
                    <div className="flex gap-2">
                        <button type="button" onClick={rotateItemCcw} className="flex-1 py-3 bg-gray-50 border border-gray-200 rounded-xl flex items-center justify-center hover:bg-a2s-gold/5 hover:border-a2s-gold hover:text-a2s-gold transition-all active:scale-95 shadow-sm" title="Rotate Left">
                            <RotateCcw size={18} />
                        </button>
                        <button type="button" onClick={rotateItem} className="flex-1 py-3 bg-gray-50 border border-gray-200 rounded-xl flex items-center justify-center hover:bg-a2s-gold/5 hover:border-a2s-gold hover:text-a2s-gold transition-all active:scale-95 shadow-sm" title="Rotate Right">
                            <RotateCw size={18} />
                        </button>
                        <button type="button" onClick={deleteItem} className="flex-1 py-3 bg-red-50 border border-red-100 text-red-400 rounded-xl flex items-center justify-center hover:bg-red-500 hover:text-white transition-all active:scale-95 shadow-sm" title="Delete">
                            <Trash2 size={18} />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Sidebar;
