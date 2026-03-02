import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
    Sparkles, Search, X, IndianRupee, Eye, ArrowUp, SlidersHorizontal,
    ArrowUpRight, Home, Sofa, ChevronDown, Grid3X3, Rows3, TrendingUp
} from 'lucide-react';
import DesignCard from '../components/DesignCard';
import ProductCard from '../components/ProductCard';
import RelatedProducts from '../components/RelatedProducts';
import ImageGallery from '../components/ImageGallery';
import FilterSidebar from '../components/FilterSidebar';
import { INITIAL_FILTER_STATE } from '../constants';
import { getInitialFiltersFromOnboarding } from '../utils/storage';
import { getDesigns, getProducts } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { openProductInNewTab } from '../utils/productLinks';

// Animated counter hook
function useCountUp(target, duration = 1200) {
    const [count, setCount] = useState(0);
    useEffect(() => {
        if (!target) return;
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) { setCount(target); clearInterval(timer); }
            else setCount(Math.floor(start));
        }, 16);
        return () => clearInterval(timer);
    }, [target, duration]);
    return count;
}

const CATEGORIES = [
    { id: 'all', label: 'All', icon: Grid3X3 },
    { id: 'living', label: 'Living', icon: Sofa, filter: 'Living Room' },
    { id: 'bedroom', label: 'Bedroom', icon: Home, filter: 'Bedroom' },
    { id: 'dining', label: 'Dining', icon: Rows3, filter: 'Dining' },
    { id: 'kitchen', label: 'Kitchen', icon: Sparkles, filter: 'Kitchen' },
    { id: 'luxury', label: 'Luxury', icon: TrendingUp, filter: 'Luxury' },
];

const Gallery = () => {
    const [filters, setFilters] = useState(() => getInitialFiltersFromOnboarding());
    const [designs, setDesigns] = useState([]);
    const [standaloneProducts, setStandaloneProducts] = useState([]);
    const [sortBy, setSortBy] = useState('recommended');
    const [searchQuery, setSearchQuery] = useState('');
    const [viewType, setViewType] = useState('rooms');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [previewItem, setPreviewItem] = useState(null);
    const [showBackToTop, setShowBackToTop] = useState(false);
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [activeCategory, setActiveCategory] = useState('all');
    const [isSortOpen, setIsSortOpen] = useState(false);
    const heroRef = useRef(null);
    const [heroScrolled, setHeroScrolled] = useState(false);

    const designCount = useCountUp(designs.length);
    const productCount = useCountUp(standaloneProducts.length);

    useEffect(() => {
        const handleScroll = () => {
            setShowBackToTop(window.scrollY > 400);
            if (heroRef.current) {
                setHeroScrolled(window.scrollY > heroRef.current.offsetHeight * 0.5);
            }
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToTop = useCallback(() => window.scrollTo({ top: 0, behavior: 'smooth' }), []);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const [designsData, productsData] = await Promise.all([getDesigns(), getProducts()]);
                setDesigns(designsData);
                setStandaloneProducts(productsData);
            } catch (err) {
                console.error('Failed to fetch gallery data:', err);
                setError('Unable to load curation. Please check your connection.');
            } finally {
                setIsLoading(false);
            }
        };
        fetchData();
    }, []);

    const furnitureItems = useMemo(() => {
        const products = [...standaloneProducts];
        const seenIds = new Set(standaloneProducts.map(p => p.id));
        designs.forEach(design => {
            (design.products || []).forEach(product => {
                if (!seenIds.has(product.id)) { seenIds.add(product.id); products.push(product); }
            });
        });
        return products;
    }, [designs, standaloneProducts]);

    const filteredItems = useMemo(() => {
        const query = searchQuery.trim().toLowerCase();
        if (viewType === 'rooms') {
            const results = designs.filter(design => {
                const matchesPrice = design.totalCost >= (filters.minPrice || 0) && design.totalCost <= (filters.maxPrice || 1000000);
                const matchesStyle = !filters.styles?.length || filters.styles.map(s => s.toLowerCase()).includes(design.style?.toLowerCase());
                const matchesRoom = !filters.roomTypes?.length || filters.roomTypes.map(r => r.toLowerCase()).includes(design.roomType?.toLowerCase());
                const matchesSearch = !query || (design.title || '').toLowerCase().includes(query) || (design.style || '').toLowerCase().includes(query) || (design.roomType || '').toLowerCase().includes(query);
                const matchesCategory = activeCategory === 'all' || (design.roomType?.toLowerCase().includes(CATEGORIES.find(c => c.id === activeCategory)?.filter?.toLowerCase() || '') || design.style?.toLowerCase().includes(activeCategory));
                return matchesPrice && matchesStyle && matchesRoom && matchesSearch && matchesCategory;
            });
            return [...results].sort((a, b) => sortBy === 'price-low' ? a.totalCost - b.totalCost : sortBy === 'price-high' ? b.totalCost - a.totalCost : 0);
        } else {
            const results = furnitureItems.filter(product => {
                const matchesPrice = product.price >= (filters.minPrice || 0) && product.price <= (filters.maxPrice || 1000000);
                const matchesCategory = !filters.roomTypes?.length || filters.roomTypes.some(cat => (product.category || '').toLowerCase().includes(cat.toLowerCase()) || (product.name || '').toLowerCase().includes(cat.toLowerCase()));
                const matchesSearch = !query || (product.name || '').toLowerCase().includes(query);
                return matchesPrice && matchesCategory && matchesSearch;
            });
            return [...results].sort((a, b) => sortBy === 'price-low' ? a.price - b.price : sortBy === 'price-high' ? b.price - a.price : 0);
        }
    }, [designs, furnitureItems, filters, sortBy, searchQuery, viewType, activeCategory]);

    const activeFilterCount = (filters.roomTypes?.length || 0) + (filters.styles?.length || 0);

    return (
        <div className="min-h-screen bg-main pb-24 transition-all duration-1000">

            {/* ── CINEMATIC HERO ─────────────────────────────────────────── */}
            <header ref={heroRef} className="relative overflow-hidden bg-surface pt-32 pb-20 px-8 border-b border-premium">
                {/* Textured background layers */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-0 left-0 w-1/2 h-full bg-gradient-to-r from-accent/3 to-transparent" />
                    <div className="absolute bottom-0 right-0 w-2/3 h-2/3 bg-gradient-to-tl from-accent/5 to-transparent" />
                    <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(circle at 80% 20%, rgba(201,166,79,0.04) 0%, transparent 50%)', }} />
                </div>

                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-12">
                        <div className="max-w-3xl">
                            <div className="flex items-center gap-4 mb-8 animate-fade-in-up">
                                <div className="w-10 h-px bg-accent" />
                                <span className="text-[11px] font-black text-accent uppercase tracking-[0.5em]">The Curation</span>
                            </div>
                            <h1 className="font-serif text-6xl md:text-8xl font-black text-main leading-[0.9] tracking-tighter mb-8 animate-reveal">
                                A Private<br /><span className="text-gradient-gold italic">Gallery</span>
                            </h1>
                            <p className="text-lg text-neutral-500 font-light leading-relaxed max-w-xl animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
                                {viewType === 'rooms'
                                    ? 'Six hand-curated perspectives on the Indian home, from compact urban sanctuaries to opulent estates.'
                                    : 'Museum-grade pieces sourced from India\'s finest artisans and vendors, exclusively for your home.'}
                            </p>
                        </div>

                        {/* Live Stats */}
                        <div className="flex gap-12 lg:gap-16 shrink-0 animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
                            <div className="text-center">
                                <div className="font-serif text-5xl font-black text-main tracking-tighter">{designCount}</div>
                                <div className="text-[9px] font-black text-accent uppercase tracking-[0.4em] mt-2">Curated<br />Realms</div>
                            </div>
                            <div className="w-px bg-premium self-stretch" />
                            <div className="text-center">
                                <div className="font-serif text-5xl font-black text-main tracking-tighter">{productCount}</div>
                                <div className="text-[9px] font-black text-accent uppercase tracking-[0.4em] mt-2">Premium<br />Pieces</div>
                            </div>
                            <div className="w-px bg-premium self-stretch" />
                            <div className="text-center">
                                <div className="font-serif text-5xl font-black text-main tracking-tighter">6+</div>
                                <div className="text-[9px] font-black text-accent uppercase tracking-[0.4em] mt-2">Design<br />Styles</div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-[1600px] mx-auto px-8 py-16">

                {/* ── VIEW TOGGLE ─────────────────────────────────────────── */}
                <div className="flex flex-col sm:flex-row items-center gap-6 mb-12 animate-fade-in-up">
                    <div className="p-1.5 glass-premium rounded-[32px] flex gap-2 border border-premium shadow-lg">
                        <button
                            onClick={() => { setViewType('rooms'); setActiveCategory('all'); }}
                            className={`px-8 py-4 rounded-[24px] text-[10px] font-black uppercase tracking-[0.2em] transition-all duration-500 flex items-center gap-3 ${viewType === 'rooms' ? 'bg-accent text-on-accent shadow-lg' : 'text-muted hover:text-main'}`}
                        >
                            <Home size={14} />
                            Complete Realms
                        </button>
                        <button
                            onClick={() => { setViewType('furniture'); setActiveCategory('all'); }}
                            className={`px-8 py-4 rounded-[24px] text-[10px] font-black uppercase tracking-[0.2em] transition-all duration-500 flex items-center gap-3 ${viewType === 'furniture' ? 'bg-accent text-on-accent shadow-lg' : 'text-muted hover:text-main'}`}
                        >
                            <Sofa size={14} />
                            The Elements
                        </button>
                    </div>

                    {/* Result count pill */}
                    <div className="px-6 py-3 rounded-full bg-offset border border-premium text-[10px] font-black uppercase tracking-widest text-muted">
                        {filteredItems.length} {filteredItems.length === 1 ? 'Discovery' : 'Discoveries'}
                    </div>
                </div>

                {/* ── CATEGORY QUICK-FILTERS (rooms only) ─────────────────── */}
                {viewType === 'rooms' && (
                    <div className="flex gap-3 overflow-x-auto pb-2 mb-12 scrollbar-none animate-fade-in-up">
                        {CATEGORIES.map(cat => {
                            const Icon = cat.icon;
                            return (
                                <button
                                    key={cat.id}
                                    onClick={() => setActiveCategory(cat.id)}
                                    className={`flex items-center gap-2.5 px-6 py-3 rounded-full border text-[10px] font-black uppercase tracking-widest whitespace-nowrap transition-all duration-300 hover:scale-102 active:scale-98 ${activeCategory === cat.id
                                            ? 'bg-main text-white border-main shadow-xl shadow-main/20 scale-105'
                                            : 'bg-white border-premium text-muted hover:border-main hover:text-main'
                                        }`}
                                >
                                    <Icon size={12} />
                                    {cat.label}
                                </button>
                            );
                        })}
                    </div>
                )}

                <div className="relative">
                    {/* ── FILTER DRAWER ──────────────────────────────────────── */}
                    <button
                        onClick={() => setIsFilterOpen(!isFilterOpen)}
                        className={`fixed left-8 bottom-8 z-[60] glass-premium px-7 py-5 rounded-[32px] border shadow-premium flex items-center gap-4 group transition-all duration-500 hover:scale-105 active:scale-95 ${isFilterOpen ? 'bg-accent text-on-accent border-accent' : 'border-premium text-main hover:border-accent'}`}
                    >
                        <SlidersHorizontal size={18} className={`${isFilterOpen ? 'rotate-180' : ''} transition-transform duration-500`} />
                        <span className="text-[11px] font-black uppercase tracking-[0.3em]">
                            {isFilterOpen ? 'Close' : 'Curate'}
                        </span>
                        {!isFilterOpen && activeFilterCount > 0 && (
                            <span className="w-5 h-5 rounded-full bg-accent text-white text-[10px] flex items-center justify-center font-black animate-bounce">
                                {activeFilterCount}
                            </span>
                        )}
                    </button>

                    {isFilterOpen && (
                        <div className="fixed inset-0 z-[70] animate-fade-in">
                            <div className="absolute inset-0 bg-main/40 backdrop-blur-md" onClick={() => setIsFilterOpen(false)} />
                            <aside className="absolute left-8 top-32 bottom-32 w-[420px] z-10 animate-fade-in-left">
                                <FilterSidebar
                                    filters={filters}
                                    setFilters={setFilters}
                                    viewType={viewType}
                                    onClose={() => setIsFilterOpen(false)}
                                />
                            </aside>
                        </div>
                    )}

                    {/* ── CONTROL BAR ────────────────────────────────────────── */}
                    <div className="mb-10 flex flex-col md:flex-row justify-between items-center gap-6 glass-premium p-5 rounded-[48px] border border-premium animate-fade-in-up shadow-sm">
                        {/* Search */}
                        <div className="relative w-full md:w-96 group">
                            <Search size={15} className="absolute left-6 top-1/2 -translate-y-1/2 text-neutral-300 group-focus-within:text-accent transition-colors duration-300" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder={viewType === 'rooms' ? 'Search rooms & styles...' : 'Search furniture & decor...'}
                                className="w-full pl-14 pr-12 py-4 rounded-full bg-offset/50 border border-transparent text-[11px] font-bold uppercase tracking-widest focus:outline-none focus:border-accent/30 focus:ring-2 focus:ring-accent/10 transition-all placeholder:text-neutral-300"
                            />
                            {searchQuery && (
                                <button
                                    onClick={() => setSearchQuery('')}
                                    className="absolute right-5 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-neutral-100 transition-colors"
                                >
                                    <X size={12} className="text-neutral-400" />
                                </button>
                            )}
                        </div>

                        {/* Sort */}
                        <div className="relative">
                            <button
                                onClick={() => setIsSortOpen(!isSortOpen)}
                                className="flex items-center gap-3 px-6 py-4 rounded-full hover:bg-neutral-50 transition-colors text-[11px] font-black uppercase tracking-widest text-main"
                            >
                                <span className="text-neutral-400 font-bold">Sort</span>
                                <span className="italic text-accent">
                                    {sortBy === 'recommended' ? 'Best Matches' : sortBy === 'price-low' ? 'Price ↑' : 'Price ↓'}
                                </span>
                                <ChevronDown size={14} className={`text-neutral-400 transition-transform ${isSortOpen ? 'rotate-180' : ''}`} />
                            </button>
                            {isSortOpen && (
                                <div className="absolute right-0 top-full mt-2 w-48 glass-premium rounded-[20px] border border-premium shadow-premium overflow-hidden z-30 animate-fade-in-up">
                                    {[
                                        { value: 'recommended', label: 'Best Matches' },
                                        { value: 'price-low', label: 'Price: Low to High' },
                                        { value: 'price-high', label: 'Price: High to Low' },
                                    ].map(opt => (
                                        <button
                                            key={opt.value}
                                            onClick={() => { setSortBy(opt.value); setIsSortOpen(false); }}
                                            className={`w-full text-left px-6 py-4 text-[10px] font-black uppercase tracking-widest transition-colors hover:bg-accent hover:text-white ${sortBy === opt.value ? 'text-accent' : 'text-muted'}`}
                                        >
                                            {opt.label}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Active filter tags */}
                        {activeFilterCount > 0 && (
                            <button
                                onClick={() => setFilters({ ...INITIAL_FILTER_STATE })}
                                className="flex items-center gap-2 px-5 py-3 rounded-full bg-red-50 border border-red-100 text-red-400 text-[10px] font-black uppercase tracking-widest hover:bg-red-100 transition-colors"
                            >
                                <X size={12} />
                                Clear {activeFilterCount} Filter{activeFilterCount > 1 ? 's' : ''}
                            </button>
                        )}
                    </div>

                    {/* ── RESULTS GRID ───────────────────────────────────────── */}
                    {isLoading ? (
                        <div className="py-48 flex flex-col items-center justify-center gap-8">
                            <LoadingSpinner />
                            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-accent animate-pulse">Composing your curation</p>
                        </div>
                    ) : error ? (
                        <div className="py-48 text-center glass-premium rounded-[64px] border-2 border-dashed border-red-100">
                            <h2 className="font-serif text-3xl font-black text-red-400 italic mb-4">Discovery Interrupted</h2>
                            <p className="text-neutral-400 mb-8 text-sm">{error}</p>
                            <button onClick={() => window.location.reload()} className="btn-premium btn-premium-outline">Try Again</button>
                        </div>
                    ) : filteredItems.length > 0 ? (
                        <div className={`grid gap-8 ${viewType === 'rooms'
                            ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'
                            : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'}`}
                        >
                            {filteredItems.map((item, index) =>
                                viewType === 'rooms'
                                    ? <div key={item.id} style={{ animationDelay: `${index * 0.05}s` }} className="animate-fade-in-up"><DesignCard design={item} onQuickPreview={setPreviewItem} /></div>
                                    : <div key={item.id} style={{ animationDelay: `${index * 0.04}s` }} className="animate-fade-in-up"><ProductCard product={item} onPreview={setPreviewItem} /></div>
                            )}
                        </div>
                    ) : (
                        <div className="py-48 text-center glass-premium rounded-[64px] border-2 border-dashed border-neutral-100">
                            <div className="text-6xl mb-6">🔍</div>
                            <h2 className="font-serif text-3xl font-black text-neutral-300 italic mb-4">No Discoveries Made</h2>
                            <p className="text-neutral-400 text-sm mb-8">Try adjusting your filters or search query.</p>
                            <button onClick={() => { setFilters({ ...INITIAL_FILTER_STATE }); setSearchQuery(''); setActiveCategory('all'); }} className="btn-premium btn-premium-outline">Reset All Filters</button>
                        </div>
                    )}
                </div>
            </div>

            {/* ── PREVIEW MODAL ───────────────────────────────────────────── */}
            {previewItem && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 lg:p-10 animate-fade-in" onClick={() => setPreviewItem(null)}>
                    <div className="absolute inset-0 bg-black/70 backdrop-blur-3xl transition-all duration-700" />
                    <div
                        className="relative w-full max-w-6xl bg-white rounded-[48px] overflow-hidden shadow-2xl flex flex-col md:flex-row max-h-[90vh] animate-fade-in-up border border-white/10"
                        onClick={e => e.stopPropagation()}
                    >
                        {/* Close */}
                        <button
                            onClick={() => setPreviewItem(null)}
                            className="absolute top-8 right-8 z-30 p-3 bg-black/5 hover:bg-black/10 rounded-full text-main transition-all duration-300 hover:rotate-90"
                        >
                            <X size={20} />
                        </button>

                        {/* Image Panel */}
                        <div className="flex-1 min-h-[300px] relative bg-neutral-50 flex items-center justify-center p-8 overflow-hidden">
                            <ImageGallery
                                mainImage={previewItem.image}
                                gallery={previewItem.gallery}
                                title={previewItem.name || previewItem.title}
                            />
                        </div>

                        {/* Details Panel */}
                        <div className="w-full md:w-[440px] shrink-0 flex flex-col bg-white overflow-y-auto">
                            <div className="p-10 flex-1">
                                {/* Badge */}
                                <span className="inline-block text-[10px] font-black uppercase tracking-[0.4em] text-accent mb-6 px-4 py-2 bg-accent/5 rounded-full border border-accent/10">
                                    {previewItem.vendor ? `${previewItem.brand} — ${previewItem.category}` : `${previewItem.style} Perspective`}
                                </span>

                                <h2 className="font-serif text-[38px] font-black text-main italic leading-[1.1] mb-6 tracking-tight">
                                    {previewItem.name || previewItem.title}
                                </h2>

                                <p className="text-sm text-neutral-400 font-medium leading-[1.9] mb-8">
                                    {previewItem.description || "Museum-grade curation sourced exclusively for this collection. Every detail reflects a commitment to architectural integrity and modern comfort."}
                                </p>

                                {/* Specs Grid */}
                                {previewItem.vendor && (
                                    <div className="grid grid-cols-2 gap-4 p-6 bg-neutral-50 rounded-[24px] border border-neutral-100 mb-8">
                                        {[
                                            { label: 'Material', value: previewItem.material || 'Premium Finish' },
                                            { label: 'Dimensions', value: previewItem.dimensions || 'Hand-measured' },
                                            { label: 'Finish', value: previewItem.color || 'Artisanal' },
                                            { label: 'Heritage', value: previewItem.brand },
                                        ].map(spec => (
                                            <div key={spec.label} className="flex flex-col gap-1">
                                                <span className="text-[9px] font-black text-neutral-300 uppercase tracking-widest">{spec.label}</span>
                                                <span className="text-xs font-black text-main">{spec.value}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Price */}
                                <div className="flex flex-col gap-1 mb-8">
                                    <span className="text-[9px] font-black text-neutral-300 uppercase tracking-widest">Acquisition Value</span>
                                    <div className="flex items-center gap-2 text-main font-black">
                                        <IndianRupee size={24} className="text-accent" />
                                        <span className="text-4xl tracking-tighter">
                                            {(previewItem.price || previewItem.totalCost || 0).toLocaleString('en-IN')}
                                        </span>
                                    </div>
                                </div>

                                {/* CTA */}
                                {previewItem.vendor ? (
                                    <button
                                        onClick={() => openProductInNewTab(previewItem)}
                                        className="btn-premium btn-premium-gold w-full text-center py-5 rounded-[20px] flex items-center justify-center gap-3 shadow-lg group mb-4"
                                    >
                                        View on {previewItem.vendor}
                                        <ArrowUpRight size={18} className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                                    </button>
                                ) : (
                                    <Link
                                        to={`/design/${previewItem.id}`}
                                        className="btn-premium btn-premium-gold w-full text-center py-5 rounded-[20px] block shadow-lg"
                                    >
                                        Enter Reflection
                                    </Link>
                                )}
                            </div>

                            {/* Related Products */}
                            {previewItem.vendor && (
                                <div className="px-10 pb-10 border-t border-neutral-50 pt-8">
                                    <RelatedProducts
                                        currentProduct={previewItem}
                                        allProducts={furnitureItems}
                                        designs={designs}
                                        onProductClick={setPreviewItem}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* ── BACK TO TOP ─────────────────────────────────────────────── */}
            {showBackToTop && (
                <button
                    onClick={scrollToTop}
                    className="fixed right-8 bottom-8 z-50 p-4 rounded-full bg-main text-white shadow-premium hover:bg-accent transition-all duration-500 hover:scale-110 animate-fade-in-up"
                >
                    <ArrowUp size={20} />
                </button>
            )}

            {/* Close sort dropdown on outside click */}
            {isSortOpen && <div className="fixed inset-0 z-20" onClick={() => setIsSortOpen(false)} />}
        </div>
    );
};

export default Gallery;
