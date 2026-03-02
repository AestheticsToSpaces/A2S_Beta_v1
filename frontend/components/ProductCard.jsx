import React from 'react';
import { ShoppingBag, IndianRupee, ArrowUpRight, Eye } from 'lucide-react';
import { openProductInNewTab } from '../utils/productLinks';

const ProductCard = ({ product, onPreview }) => {
    return (
        <div className="group relative card-luxury overflow-hidden flex flex-col h-full bg-white animate-fade-in-up">
            {/* Image Container - Premium Frame */}
            <div className="relative aspect-[4/5] overflow-hidden bg-neutral-50 flex items-center justify-center group/image">
                <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-contain p-12 transition-transform duration-1000 ease-out group-hover:scale-110"
                />

                {/* Immersive Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-0 group-hover:opacity-90 transition-opacity duration-500" />

                {/* Top Action Badge */}
                <div className="absolute top-6 right-6 z-20 opacity-0 group-hover:opacity-100 translate-y-[-10px] group-hover:translate-y-0 transition-all duration-500">
                    <button
                        onClick={(e) => { e.stopPropagation(); onPreview && onPreview(product); }}
                        className="p-3 rounded-full backdrop-blur-xl bg-white/10 text-white border border-white/20 hover:bg-accent hover:border-accent transition-all duration-300 shadow-xl"
                        aria-label="Quick View"
                    >
                        <Eye size={18} />
                    </button>
                </div>

                {/* Bottom Overlay Details (Revealed on Hover) */}
                <div className="absolute bottom-0 left-0 right-0 p-8 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500 z-10">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="w-8 h-px bg-accent" />
                        <span className="text-[9px] font-black text-accent uppercase tracking-[0.4em]">
                            {product.brand}
                        </span>
                    </div>

                    <h3 className="font-serif text-2xl font-black text-white mb-6 leading-tight italic">
                        {product.name}
                    </h3>

                    <div className="flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all duration-500 delay-100">
                        <div className="flex items-center gap-2 text-white/80">
                            <IndianRupee size={14} className="text-accent" />
                            <span className="text-xs font-black uppercase tracking-widest leading-none">
                                {(product.price || 0).toLocaleString('en-IN')}
                            </span>
                        </div>

                        <button
                            onClick={(e) => { e.stopPropagation(); openProductInNewTab(product); }}
                            className="flex items-center gap-2 text-[9px] font-black text-white uppercase tracking-[0.3em] border-b border-white/30 pb-1 hover:border-accent hover:text-accent transition-colors group/link"
                        >
                            <span>Shop Collection</span>
                            <ArrowUpRight size={12} className="group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Content for Non-Hover State (Subtle Footer) */}
            <div className="p-6 bg-surface flex flex-col border-t border-gray-50 group-hover:bg-main group-hover:border-main transition-colors duration-500">
                <div className="flex justify-between items-center">
                    <span className="text-[10px] font-black uppercase tracking-widest text-gray-400 group-hover:text-accent transition-colors">
                        {product.category}
                    </span>
                    <span className="text-[10px] font-bold text-gray-300 group-hover:text-white/30">
                        Sourced by A2S
                    </span>
                </div>
            </div>

            {/* Full card click for preview */}
            <button
                onClick={() => onPreview && onPreview(product)}
                className="absolute inset-0 z-[5]"
            />
        </div>
    );
};

export default ProductCard;
