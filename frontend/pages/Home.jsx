import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, Video, Smartphone, Sparkles, Layout } from 'lucide-react';
import { DESIGNS_DATA } from '../constants';

const Home = () => {
    return (
        <main className="w-full bg-main min-h-screen transition-all duration-1000" role="main">
            {/* Hero Section */}
            <section
                className="relative min-h-[95vh] flex flex-col items-center justify-center overflow-hidden"
                aria-label="Hero"
            >
                <div className="absolute inset-0 z-0">
                    <img
                        src="https://images.unsplash.com/photo-1616486338812-3dadae4b4f9d?q=80&w=2500&auto=format&fit=crop"
                        alt="Luxury Interior"
                        className="w-full h-full object-cover scale-105 animate-float"
                        style={{ animationDuration: '20s' }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-var(--a2s-cream)" />
                </div>

                <div className="relative z-10 max-w-7xl mx-auto px-4 text-center mt-12">
                    <div className="inline-flex items-center gap-3 px-6 py-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-full text-[10px] font-black text-white uppercase tracking-[0.4em] mb-8 animate-fade-in-up shadow-2xl">
                        <Sparkles size={14} className="text-accent" /> The Future of Curation
                    </div>

                    <h1 className="font-serif text-5xl sm:text-6xl md:text-8xl font-black text-white mb-8 leading-[0.9] tracking-tighter animate-reveal">
                        Aesthetics <br />
                        <span className="text-gradient-gold italic font-serif py-2">To Spaces</span>
                    </h1>

                    <p className="text-lg md:text-2xl text-white/80 mb-12 max-w-2xl mx-auto font-light leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                        Transcending traditional design with AI-curated elegance. Discover, visualize, and source masterpieces for your home.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-6 justify-center items-center animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
                        <Link
                            to="/gallery"
                            className="btn-premium btn-premium-gold group"
                        >
                            <span>Explore the Gallery</span>
                            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <Link
                            to="/consultant"
                            className="btn-premium btn-premium-outline hover:bg-white/10"
                        >
                            <Sparkles size={18} />
                            <span>AI Stylist</span>
                        </Link>
                    </div>
                </div>

                {/* Floating Elements */}
               
            </section>

            {/* Trending Now Section */}
            <section
                className="py-16 md:py-24 bg-gradient-to-b from-surface to-main/50 transition-all duration-1000"
                aria-labelledby="trending-heading"
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <header className="flex flex-col md:flex-row md:justify-between md:items-end gap-6 mb-16 px-2">
                        <div className="max-w-xl">
                            <span className="section-tag animate-fade-in-up">Editorial Curation</span>
                            <h2 id="trending-heading" className="font-serif text-4xl md:text-6xl font-black text-main mb-4 leading-tight">
                                Trending <span className="text-gradient-gold italic">Aesthetics</span>
                            </h2>
                            <p className="text-gray-500 font-medium">Handpicked design movements that are defining the modern Indian home.</p>
                        </div>
                        <Link
                            to="/gallery"
                            className="btn-premium btn-premium-outline group"
                        >
                            <span>Browse All</span>
                            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                        </Link>
                    </header>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                        {DESIGNS_DATA.slice(0, 4).map((design, index) => (
                            <Link
                                to={`/design/${design.id}`}
                                key={design.id}
                                className="group block h-full animate-fade-in-up"
                                style={{ animationDelay: `${index * 0.1}s` }}
                            >
                                <article className="relative bg-surface rounded-[32px] overflow-hidden shadow-premium group-hover:shadow-premium-hover transition-all duration-500 h-full border border-premium">
                                    <div className="aspect-[4/5] overflow-hidden">
                                        <img
                                            src={design.image}
                                            alt=""
                                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
                                        />
                                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity" />
                                    </div>

                                    <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
                                        <div className="flex items-center gap-3 mb-3">
                                            <span className="w-8 h-px bg-accent" />
                                            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-accent">
                                                {design.style}
                                            </p>
                                        </div>
                                        <h3 className="font-serif text-2xl font-black mb-2 leading-tight group-hover:text-accent transition-colors italic">{design.title}</h3>
                                        <p className="text-[10px] text-white/60 uppercase tracking-widest font-bold">Explore Collection</p>
                                    </div>
                                </article>
                            </Link>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feature Section */}
            <section
                className="py-24 md:py-32 bg-main text-main overflow-hidden relative transition-all duration-1000"
                aria-labelledby="feature-heading"
            >
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(212,175,55,0.15),transparent)]" aria-hidden="true" />
                <div className="max-w-7xl mx-auto px-8 relative z-10">
                    <div className="flex flex-col lg:flex-row lg:items-center gap-20 md:gap-24">
                        <div className="flex-1">
                            <span className="section-tag mb-4">Experimental Research</span>
                            <h2 id="feature-heading" className="font-serif text-5xl md:text-7xl font-black mb-8 leading-[0.9] tracking-tighter italic">
                                Video to <br />
                                <span className="text-gradient-gold">3D Staging</span>
                            </h2>
                            <p className="text-muted mb-12 leading-relaxed text-lg md:text-xl font-light">
                                Transmute reality into inspiration. Our upcoming AI engine converts smartphone captures into infinite 3D layouts, allowing you to stage your future home in real-time.
                            </p>
                            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-8 mb-12">
                                <li className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-accent hover:scale-110 transition-transform">
                                        <Video size={24} />
                                    </div>
                                    <div>
                                        <h4 className="text-xs font-black uppercase tracking-widest text-main/90 mb-1">Instant Scan</h4>
                                        <p className="text-[11px] text-muted leading-relaxed">Spatial reconstruction from 4K video feeds.</p>
                                    </div>
                                </li>
                                <li className="flex flex-col gap-4">
                                    <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-accent hover:scale-110 transition-transform">
                                        <Sparkles size={24} />
                                    </div>
                                    <div>
                                        <h4 className="text-xs font-black uppercase tracking-widest text-main/90 mb-1">Neural Staging</h4>
                                        <p className="text-[11px] text-muted leading-relaxed">Auto-suggest furniture that fits your geometry.</p>
                                    </div>
                                </li>
                            </ul>
                            <div className="inline-flex flex-col sm:flex-row items-center gap-6">
                                <button
                                    type="button"
                                    className="btn-premium btn-premium-gold w-full sm:w-auto"
                                >
                                    Access the Beta
                                </button>
                                <span className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em]">Limited Slots Available Q4 2026</span>
                            </div>
                        </div>
                        <div className="flex-1 flex justify-center lg:justify-end">
                            <div className="relative group max-w-lg">
                                <div className="absolute -inset-4 bg-a2s-gold/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
                                <figure className="relative aspect-[4/5] w-full md:w-[460px] rounded-[48px] overflow-hidden border border-white/10 shadow-2xl bg-black">
                                    <img
                                        src="https://images.unsplash.com/photo-1631679706909-1844bbd07221?q=80&w=1000&auto=format&fit=crop"
                                        alt="3D Staging Demo"
                                        className="w-full h-full object-cover opacity-50 group-hover:scale-105 transition-transform duration-1000"
                                    />
                                    <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center">
                                        <div className="w-24 h-24 rounded-full bg-white/10 backdrop-blur-3xl flex items-center justify-center border border-white/20 mb-6 group-hover:scale-110 transition-transform">
                                            <Video className="text-accent" size={40} />
                                        </div>
                                        <p className="text-[10px] font-black text-white/40 uppercase tracking-[0.5em]">Spatial Intelligence</p>
                                    </div>
                                </figure>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    );
};

export default Home;
