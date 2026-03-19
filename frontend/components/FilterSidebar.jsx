import React from 'react';
import { X, SlidersHorizontal, IndianRupee } from 'lucide-react';
import { INITIAL_FILTER_STATE } from '../constants';

const FilterSidebar = ({ filters, setFilters, viewType = 'rooms', onClose }) => {
    const roomTypesList = ['LIVING', 'BEDROOM', 'KITCHEN', 'DINING'];
    const furnitureCategoriesList = ['BED', 'SOFA', 'TABLE', 'CHAIR', 'LIGHT', 'RUG', 'PAINT'];

    const activeFilterCount =
        (filters.roomTypes?.length || 0) +
        (filters.maxPrice < 200000 ? 1 : 0);

    const toggleRoom = (room) => {
        setFilters(prev => ({
            ...prev,
            roomTypes: prev.roomTypes.includes(room)
                ? prev.roomTypes.filter(r => r !== room)
                : [...prev.roomTypes, room]
        }));
    };

    return (
        <div className="bg-white p-10 rounded-[64px] border border-premium shadow-2xl h-full flex flex-col overflow-hidden animate-fade-in-left transition-all duration-700">
            <div className="flex justify-between items-start mb-12">
                <div className="space-y-1">
                    <span className="text-[11px] font-black uppercase tracking-[0.4em] text-accent mb-2 block">Personalize</span>
                    <h3 className="font-serif text-5xl font-black text-main italic leading-none">
                        Curate
                    </h3>
                </div>
                {onClose && (
                    <button
                        type="button"
                        onClick={onClose}
                        className="p-4 rounded-full hover:bg-gray-100 transition-all duration-500 group"
                    >
                        <X size={24} className="text-gray-300 group-hover:text-main group-hover:rotate-90 transition-all duration-500" />
                    </button>
                )}
            </div>

            {/* Price Filter Section */}
            <div className="mb-16 group">
                <div className="flex justify-between items-center mb-8">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400">Investment Limit</h4>
                    <div className="flex items-center gap-2 text-accent font-black italic">
                        <IndianRupee size={16} />
                        <span className="text-3xl tracking-tighter">{(filters.maxPrice / 1000).toFixed(0)}k</span>
                    </div>
                </div>
                <div className="relative px-2">
                    <input
                        type="range"
                        min="10000"
                        max="200000"
                        step="5000"
                        value={filters.maxPrice}
                        onChange={(e) => setFilters(prev => ({ ...prev, maxPrice: parseInt(e.target.value) }))}
                        className="w-full h-2 bg-gray-100 rounded-full appearance-none cursor-pointer accent-accent transition-all"
                    />
                    <div className="flex justify-between mt-6 text-[10px] font-black text-gray-300 uppercase tracking-[0.2em]">
                        <span>Min 10k</span>
                        <span>Max 200k</span>
                    </div>
                </div>
            </div>

            {/* Category/Space Filter Section */}
            <div className="mb-12">
                <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-8">
                    {viewType === 'rooms' ? 'By Space' : 'By Category'}
                </h4>
                <div className="flex flex-wrap gap-4">
                    {(viewType === 'rooms' ? roomTypesList : furnitureCategoriesList).map(item => (
                        <button
                            key={item}
                            onClick={() => toggleRoom(item)}
                            className={`px-8 py-5 rounded-[24px] text-[11px] font-black uppercase tracking-widest transition-all duration-500 border-2 ${filters.roomTypes.includes(item) ? 'bg-accent text-on-accent border-accent shadow-lg shadow-accent/20' : 'bg-[#FDFDFD] text-main border-transparent hover:border-accent/10'}`}
                        >
                            {item}
                        </button>
                    ))}
                </div>
            </div>

            {/* Clear All Global Action */}
            <button
                type="button"
                onClick={() => setFilters({ ...INITIAL_FILTER_STATE })}
                className="w-full py-5 rounded-3xl border border-premium text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 hover:text-accent hover:border-accent hover:bg-accent/5 transition-all duration-500 mt-4 group"
            >
                <span className="flex items-center justify-center gap-2">
                    <SlidersHorizontal size={14} className="group-hover:rotate-180 transition-transform duration-700" />
                    Reset Curation
                </span>
            </button>
        </div>
    );
};

export default FilterSidebar;
