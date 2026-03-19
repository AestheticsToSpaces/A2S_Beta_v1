import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Share2, Heart, IndianRupee, ShoppingBag, Sparkles, ExternalLink, ArrowRight } from 'lucide-react';
import ImageGallery from '../components/ImageGallery';
import { isDesignSaved } from '../utils/storage';
import { getProductShopUrl, openProductInNewTab } from '../utils/productLinks';
import { getDesignById, saveDesign, getUserProfile } from '../services/api';

const DesignDetail = () => {
    const { id } = useParams();
    const [design, setDesign] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaved, setIsSaved] = useState(false);
    const [shareFeedback, setShareFeedback] = useState('idle');

    useEffect(() => {
        const fetchDesignAndStatus = async () => {
            if (!id) return;
            setIsLoading(true);
            try {
                const found = await getDesignById(id);
                setDesign(found);
                if (localStorage.getItem('token')) {
                    try {
                        const profile = await getUserProfile();
                        if (profile && profile.savedDesigns) {
                            setIsSaved(profile.savedDesigns.includes(id));
                        }
                    } catch (authErr) {
                        setIsSaved(isDesignSaved(id));
                    }
                } else {
                    setIsSaved(isDesignSaved(id));
                }
            } catch (err) {
                console.error(err);
                setDesign(null);
            } finally {
                setIsLoading(false);
            }
        };
        fetchDesignAndStatus();
    }, [id]);

    const toggleSave = async () => {
        if (!id) return;
        try {
            const updatedSavedDesigns = await saveDesign(id);
            setIsSaved(updatedSavedDesigns.includes(id));
        } catch (e) {
            console.error('Error toggling save:', e);
        }
    };

    const handleShare = async () => {
        const url = window.location.href;
        try {
            if (navigator.share && design) {
                await navigator.share({
                    title: design.title,
                    text: design.description,
                    url,
                });
            } else {
                await navigator.clipboard.writeText(url);
                setShareFeedback('copied');
            }
        } catch (e) {
            await navigator.clipboard.writeText(url);
            setShareFeedback('copied');
        }
        setTimeout(() => setShareFeedback('idle'), 2000);
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-main pt-24 flex items-center justify-center transition-all duration-1000">
                <div className="flex flex-col items-center gap-6">
                    <div className="w-16 h-16 border-4 border-accent/20 border-t-accent rounded-full animate-spin" />
                    <p className="text-[10px] font-black uppercase tracking-[0.4em] text-accent animate-pulse">Entering Reflection</p>
                </div>
            </div>
        );
    }

    if (!design) return null;

    return (
        <div className="min-h-screen bg-main transition-all duration-1000">
            <div className="flex flex-col lg:flex-row min-h-screen">

                {/* Visual Panel (Sticky) */}
                <div className="w-full lg:w-[55%] lg:h-screen lg:sticky lg:top-0 relative overflow-hidden bg-neutral-100 flex items-center justify-center p-8 lg:p-12">
                    <div className="w-full h-full max-w-4xl">
                        <ImageGallery
                            mainImage={design.image}
                            gallery={design.gallery}
                            title={design.title}
                        />
                    </div>

                    {/* Floating Navigation */}
                    <div className="absolute top-12 left-12 z-20 flex gap-4">
                        <Link
                            to="/gallery"
                            className="p-4 bg-white/10 backdrop-blur-2xl border border-white/20 rounded-full text-white hover:bg-accent hover:border-accent transition-all duration-500 group"
                        >
                            <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
                        </Link>
                        <button
                            onClick={handleShare}
                            className="px-6 py-4 bg-white/10 backdrop-blur-2xl border border-white/20 rounded-full text-white text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-main transition-all duration-500"
                        >
                            {shareFeedback === 'copied' ? 'Copied' : 'Share Narrative'}
                        </button>
                    </div>

                    {/* Bottom Metadata */}
                    <div className="absolute bottom-12 left-12 right-12 z-20 hidden lg:block animate-fade-in-up">
                        <div className="flex items-center gap-3 mb-4">
                            <Sparkles className="text-accent" size={16} />
                            <span className="text-[10px] font-black text-accent uppercase tracking-[0.4em]">Expert Curation</span>
                        </div>
                        <h1 className="font-serif text-6xl font-black text-white italic tracking-tighter mb-4 leading-[0.9]">
                            {design.title}
                        </h1>
                    </div>
                </div>

                {/* Editorial Content Panel */}
                <div className="w-full lg:w-[45%] bg-white p-8 md:p-16 lg:p-24 overflow-y-auto transition-all duration-1000">
                    <header className="mb-16">
                        <div className="flex justify-between items-start mb-8">
                            <div>
                                <span className="section-tag mb-4">{design.style} Perspective</span>
                                <h1 className="font-serif text-5xl font-black text-main lg:hidden mb-8 tracking-tighter leading-none">{design.title}</h1>
                                <p className="text-xl text-neutral-500 font-light italic leading-relaxed max-w-lg">
                                    "{design.description}"
                                </p>
                            </div>
                            <button
                                onClick={toggleSave}
                                className={`p-4 rounded-full transition-all duration-500 ${isSaved ? 'bg-accent text-white shadow-xl shadow-accent/20 scale-110' : 'bg-neutral-50 text-neutral-300 hover:text-accent'}`}
                            >
                                <Heart size={20} fill={isSaved ? 'currentColor' : 'none'} />
                            </button>
                        </div>

                        <div className="grid grid-cols-2 gap-8 border-t border-premium pt-8">
                            <div>
                                <span className="text-[9px] font-black uppercase tracking-widest text-gray-300 block mb-2">Investment Estimation</span>
                                <div className="flex items-center gap-2 text-2xl font-black text-main tracking-tighter">
                                    <IndianRupee size={18} className="text-accent" />
                                    <span>{design.totalCost.toLocaleString('en-IN')}</span>
                                </div>
                            </div>
                            <div>
                                <span className="text-[9px] font-black uppercase tracking-widest text-gray-300 block mb-2">Composition</span>
                                <div className="text-2xl font-black text-main tracking-tighter">
                                    {design.products?.length || 0} <span className="text-sm font-bold text-gray-300">Elements</span>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Sourcing Section */}
                    <section className="space-y-16">
                        <div className="flex justify-between items-end border-b border-premium pb-8">
                            <h2 className="font-serif text-3xl font-black italic text-main">The Elements</h2>
                            <button onClick={() => window.scrollTo({ top: 1000, behavior: 'smooth' })} className="text-[10px] font-black uppercase tracking-widest text-accent hover:text-main transition-colors">
                                View Specification
                            </button>
                        </div>

                        {/* Categorized Products */}
                        {Object.entries(
                            design.products.reduce((acc, p) => {
                                const cat = p.category || 'Essential';
                                if (!acc[cat]) acc[cat] = [];
                                acc[cat].push(p);
                                return acc;
                            }, {})
                        ).map(([category, products]) => (
                            <div key={category} className="space-y-8">
                                <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-gray-300 flex items-center gap-4">
                                    <span className="w-12 h-px bg-gray-100" />
                                    {category}
                                </h3>
                                <div className="space-y-6">
                                    {products.map(product => (
                                        <div key={product.id} className="group flex gap-8 items-center py-4 hover:px-4 hover:bg-accent/5 rounded-3xl transition-all duration-500">
                                            <div className="w-24 h-24 bg-surface rounded-2xl overflow-hidden border border-premium p-2 flex-shrink-0 group-hover:shadow-premium transition-all">
                                                <img src={product.image} className="w-full h-full object-contain" alt="" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div>
                                                        <h4 className="font-serif text-lg font-black italic text-main">{product.name}</h4>
                                                        <p className="text-[9px] font-black uppercase tracking-widest text-gray-400">{product.brand}</p>
                                                    </div>
                                                    <div className="flex items-center gap-1.5 text-main font-black">
                                                        <IndianRupee size={12} className="text-accent" />
                                                        <span className="text-sm tracking-tighter">{product.price.toLocaleString('en-IN')}</span>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => openProductInNewTab(product)}
                                                    className="inline-flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-accent border-b border-accent/20 pb-1 hover:border-accent transition-all"
                                                >
                                                    <span>View Acquisition</span>
                                                    <ExternalLink size={10} />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </section>

                    {/* Global Sourcing Action */}
                    <footer className="mt-24 pt-16 border-t border-premium">
                        <button
                            className="w-full py-6 rounded-full bg-main text-on-accent text-[10px] font-black uppercase tracking-[0.4em] hover:bg-accent hover:text-on-accent transition-all duration-700 shadow-premium flex items-center justify-center gap-4 group"
                        >
                            <span>Acquire Full Collection</span>
                            <ArrowRight size={18} className="group-hover:translate-x-2 transition-transform" />
                        </button>
                    </footer>
                </div>
            </div>
        </div>
    );
};

export default DesignDetail;
