import { Link, useNavigate } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
import {
    Heart,
    Box,
    User,
    Plus,
    ShoppingBag,
    Lock,
    Copy,
    Layout,
    Palette,
    LogOut,
} from 'lucide-react';
import { DESIGNS_DATA } from '../constants';
import { STORAGE_KEYS, clearUser, getOnboardingPreferences, getSavedDesignIds } from '../utils/storage';
import { getUserProfile, getDesigns } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorDisplay from '../components/ErrorDisplay';

const Dashboard = () => {
    const navigate = useNavigate();
    // const user = getUser(); // Deprecated local user
    const [user, setUserProfile] = useState(null); // Use backend user
    const [projects, setProjects] = useState([]);
    const [savedDesigns, setSavedDesigns] = useState([]);
    const [waitlistCode, setWaitlistCode] = useState('A2S-PHASE2-99');
    const [copied, setCopied] = useState(false);
    const [preferences, setPreferences] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Merges localStorage saves (heart icon) + backend DB saves, then loads full design objects
    const loadSavedDesigns = async (profileSavedIds = []) => {
        try {
            const localIds = getSavedDesignIds().map(String);
            const mergedIds = Array.from(new Set([...localIds, ...profileSavedIds.map(String)]));
            if (mergedIds.length === 0) { setSavedDesigns([]); return; }
            const allDesigns = await getDesigns();
            setSavedDesigns(allDesigns.filter((d) => mergedIds.includes(String(d.id))));
        } catch (e) {
            console.error('Failed to load saved designs:', e);
        }
    };

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                setIsLoading(true);
                setError(null);
                if (!localStorage.getItem('token')) {
                    await loadSavedDesigns([]);
                    setIsLoading(false);
                    return;
                }
                const profile = await getUserProfile();
                setUserProfile(profile);
                await loadSavedDesigns(profile.savedDesigns || []);
            } catch (e) {
                console.error('Failed to fetch profile:', e);
                setError('Unable to load your profile. Please check your connection and try again.');
                setUserProfile(null);
                await loadSavedDesigns([]);
            } finally {
                setIsLoading(false);
            }
        };
        fetchProfile();

        // Refresh saved designs whenever heart icon is toggled in gallery
        const handleSavedUpdate = () => loadSavedDesigns([]);
        window.addEventListener('a2s-saved-update', handleSavedUpdate);
        return () => window.removeEventListener('a2s-saved-update', handleSavedUpdate);
    }, []);

    useEffect(() => {
        try {
            const raw = localStorage.getItem(STORAGE_KEYS.SAVED_PRESETS);
            if (raw) {
                const parsed = JSON.parse(raw);
                setProjects(Array.isArray(parsed) ? parsed : []);
            }
        } catch (e) {
            console.error(e);
        }

        // Load onboarding preferences
        const prefs = getOnboardingPreferences();
        setPreferences(prefs);
    }, []);


    const handleLogout = async () => {
        try {
            await clearUser();
            navigate('/');
        } catch (error) {
            console.error('Logout error:', error);
            navigate('/');
        }
    };

    const copyCode = () => {
        navigator.clipboard.writeText(waitlistCode).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-a2s-cream/50 to-white pt-24 pb-16 flex items-center justify-center px-4">
                <LoadingSpinner message="Loading your design hub..." size="lg" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-a2s-cream/50 to-white pt-24 pb-16 flex items-center justify-center px-4">
                <ErrorDisplay
                    message="Couldn't load your dashboard"
                    details={error}
                    onRetry={() => window.location.reload()}
                />
            </div>
        );
    }

    if (!user) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-a2s-cream/50 to-white pt-24 pb-16 flex items-center justify-center px-4">
                <div className="max-w-md w-full text-center">
                    <div className="bg-white rounded-2xl luxury-shadow border border-gray-100 p-10">
                        <div className="w-16 h-16 rounded-2xl bg-a2s-gold/15 flex items-center justify-center mx-auto mb-6">
                            <User size={32} className="text-a2s-gold" />
                        </div>
                        <h1 className="font-serif text-2xl font-bold text-a2s-charcoal mb-2">Your design hub</h1>
                        <span className="section-underline block mb-4" aria-hidden="true" />
                        <p className="text-gray-600 mb-8">
                            Sign in to see your saved designs, 3D projects, and a personalized dashboard.
                        </p>
                        <Link to="/login" className="btn-primary inline-flex items-center gap-2">
                            Sign in to continue
                        </Link>
                    </div>
                    <p className="mt-6 text-sm text-gray-500">
                        You can still <Link to="/gallery" className="text-a2s-gold font-semibold hover:underline">browse the gallery</Link> without signing in.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-a2s-cream/50 to-white pt-24 pb-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <header className="mb-10">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4">
                        <div>
                            <h1 className="font-serif text-3xl md:text-4xl font-bold text-a2s-charcoal">
                                Namaste, {user.name.split(' ')[0]}
                            </h1>
                            <span className="section-underline" aria-hidden="true" />
                            <p className="text-gray-600 mt-3 max-w-xl">
                                Your design hub — saved gallery looks and 3D room projects in one place.
                            </p>
                        </div>
                        <div className="flex flex-wrap items-center gap-2">
                            <button
                                type="button"
                                onClick={handleLogout}
                                className="inline-flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-red-600 transition px-4 py-2.5 rounded-xl hover:bg-red-50 border border-gray-200 w-fit"
                            >
                                <LogOut size={16} /> Log out
                            </button>
                        </div>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                    {/* Main content */}
                    <div className="lg:col-span-8 space-y-10">
                        {/* Stats */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div className="bg-white p-5 rounded-2xl border border-gray-100 luxury-shadow card-hover flex items-center gap-4">
                                <div className="w-12 h-12 bg-a2s-charcoal text-a2s-gold rounded-xl flex items-center justify-center flex-shrink-0">
                                    <User size={22} />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-sm font-bold text-a2s-charcoal truncate">{user.name}</p>
                                    <p className="text-xs text-gray-500">{user.location || '—'}</p>
                                </div>
                            </div>
                            <div className="bg-white p-5 rounded-2xl border border-gray-100 luxury-shadow card-hover flex items-center gap-4">
                                <div className="w-12 h-12 bg-a2s-gold/15 text-a2s-gold rounded-xl flex items-center justify-center flex-shrink-0">
                                    <Heart size={22} />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold text-a2s-charcoal">{savedDesigns.length}</p>
                                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Saved Designs</p>
                                </div>
                            </div>
                            <div className="bg-white p-5 rounded-2xl border border-gray-100 luxury-shadow card-hover flex items-center gap-4">
                                <div className="w-12 h-12 bg-a2s-charcoal/10 text-a2s-charcoal rounded-xl flex items-center justify-center flex-shrink-0">
                                    <Box size={22} />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold text-a2s-charcoal">{projects.length}</p>
                                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">3D Projects</p>
                                </div>
                            </div>
                        </div>

                        {/* 3D Projects */}
                        <section className="bg-white rounded-2xl border border-gray-100 luxury-shadow overflow-hidden" aria-labelledby="projects-heading">
                            <div className="p-5 md:p-6 border-b border-gray-100 flex flex-wrap justify-between items-center gap-3">
                                <div>
                                    <h2 id="projects-heading" className="font-serif text-xl font-bold text-a2s-charcoal">
                                        My 3D Projects
                                    </h2>
                                    <span className="section-underline" />
                                </div>
                                <Link
                                    to="/3d-space"
                                    className="btn-primary inline-flex items-center gap-2"
                                >
                                    <Plus size={16} /> New project
                                </Link>
                            </div>
                            <div className="p-5 md:p-6">
                                {projects.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {projects.map((proj) => (
                                            <Link
                                                to="/3d-space"
                                                key={proj.id}
                                                className="group bg-a2s-cream/40 p-5 rounded-2xl border border-gray-100 hover:border-a2s-gold/40 hover:shadow-a2s-gold/20 transition flex flex-col justify-between min-h-[120px]"
                                            >
                                                <div className="flex justify-between items-start">
                                                    <div className="bg-white p-2.5 rounded-xl shadow-sm w-fit">
                                                        <Box size={20} className="text-a2s-gold" />
                                                    </div>
                                                    <span className="text-[10px] font-medium text-gray-500 bg-white px-2 py-1 rounded-lg border border-gray-100">
                                                        {proj.date}
                                                    </span>
                                                </div>
                                                <div>
                                                    <h3 className="font-serif font-bold text-a2s-charcoal group-hover:text-a2s-gold transition">
                                                        {proj.name}
                                                    </h3>
                                                    <p className="text-xs text-gray-500 mt-0.5">
                                                        {proj.roomType} · {proj.itemCount} items
                                                    </p>
                                                </div>
                                            </Link>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-12 px-4">
                                        <div className="w-14 h-14 rounded-2xl bg-a2s-gold/10 flex items-center justify-center mx-auto mb-4">
                                            <Box size={28} className="text-a2s-gold" />
                                        </div>
                                        <p className="text-gray-600 mb-2">No 3D projects yet.</p>
                                        <p className="text-sm text-gray-500 mb-4">Create a room layout in 3D Studio and save it here.</p>
                                        <Link to="/3d-space" className="btn-primary inline-flex items-center gap-2">
                                            <Layout size={16} /> Open 3D Studio
                                        </Link>
                                    </div>
                                )}
                            </div>
                        </section>

                        {/* Saved Collections */}
                        <section aria-labelledby="saved-heading">
                            <div className="mb-5">
                                <h2 id="saved-heading" className="font-serif text-xl font-bold text-a2s-charcoal">
                                    Saved Collections
                                </h2>
                                <span className="section-underline" />
                                <p className="text-sm text-gray-500 mt-2">Gallery designs you’ve saved — open to shop the look.</p>
                            </div>
                            {savedDesigns.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {savedDesigns.map((design) => (
                                        <article
                                            key={design.id}
                                            className="bg-white rounded-2xl luxury-shadow overflow-hidden border border-gray-100 card-hover group"
                                        >
                                            <Link to={`/design/${design.id}`} className="block">
                                                <div className="relative aspect-[4/3] overflow-hidden">
                                                    <img
                                                        src={design.image}
                                                        alt=""
                                                        className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                                                    />
                                                    <div className="absolute top-3 right-3 bg-white/95 p-2 rounded-xl shadow-sm text-red-500">
                                                        <Heart size={14} fill="currentColor" />
                                                    </div>
                                                </div>
                                                <div className="p-4 flex justify-between items-end gap-3">
                                                    <div className="min-w-0">
                                                        <h3 className="font-serif font-bold text-a2s-charcoal truncate group-hover:text-a2s-gold transition">
                                                            {design.title}
                                                        </h3>
                                                        <p className="text-xs text-gray-500">{design.style}</p>
                                                    </div>
                                                    <span className="flex-shrink-0 p-2.5 rounded-xl bg-a2s-cream/80 text-a2s-charcoal hover:bg-a2s-charcoal hover:text-white transition">
                                                        <ShoppingBag size={16} />
                                                    </span>
                                                </div>
                                            </Link>
                                        </article>
                                    ))}
                                </div>
                            ) : (
                                <div className="bg-white rounded-2xl border-2 border-dashed border-gray-200 p-12 text-center">
                                    <div className="w-16 h-16 rounded-2xl bg-a2s-gold/10 flex items-center justify-center mx-auto mb-4">
                                        <Heart size={32} className="text-a2s-gold" />
                                    </div>
                                    <p className="text-gray-600 font-medium mb-1">No saved designs yet.</p>
                                    <p className="text-sm text-gray-500 mb-6">Save looks from the Gallery to see them here.</p>
                                    <Link to="/gallery" className="btn-primary inline-flex items-center gap-2">
                                        <Layout size={16} /> Browse Gallery
                                    </Link>
                                </div>
                            )}
                        </section>

                        {/* Style Profile Section */}
                        <section className="bg-white rounded-2xl border border-gray-100 luxury-shadow p-6 md:p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="font-serif text-xl font-bold text-a2s-charcoal">Design DNA</h2>
                                    <span className="section-underline" />
                                    <p className="text-sm text-gray-500 mt-2">Your aesthetic preferences used for personalized recommendations.</p>
                                </div>
                                <Link to="/onboarding" className="text-xs font-bold text-a2s-gold uppercase tracking-widest hover:text-a2s-charcoal transition">
                                    Refine Profile
                                </Link>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                                <div className="space-y-4">
                                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Preferred Aesthetics</h3>
                                    {preferences && preferences.styles.length > 0 ? (
                                        <div className="flex flex-wrap gap-2">
                                            {preferences.styles.map(style => (
                                                <span key={style} className="px-3 py-1.5 rounded-lg bg-a2s-cream text-a2s-charcoal text-sm font-semibold border border-gray-100">
                                                    {style}
                                                </span>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-400 italic">No preferences set yet</p>
                                    )}
                                </div>
                                <div className="space-y-4">
                                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Focus Area</h3>
                                    {preferences && preferences.room ? (
                                        <div className="flex items-center gap-3 p-4 rounded-xl bg-a2s-charcoal text-white">
                                            <Palette className="text-a2s-gold" size={20} />
                                            <div>
                                                <p className="font-serif font-bold leading-none">{preferences.room}</p>
                                                <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-wider">Primary Interest</p>
                                            </div>
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-400 italic">No focus area set yet</p>
                                    )}
                                </div>
                            </div>
                        </section>
                    </div>

                    {/* Sidebar — Early Access */}
                    <aside className="lg:col-span-4" aria-label="Early access">
                        <div className="bg-a2s-charcoal rounded-2xl text-white p-6 shadow-xl relative overflow-hidden sticky top-24">
                            <div className="absolute top-0 right-0 w-48 h-48 bg-a2s-gold/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
                            <div className="absolute bottom-0 left-0 w-32 h-32 bg-a2s-gold/5 rounded-full blur-2xl translate-y-1/2 -translate-x-1/2 pointer-events-none" />

                            <div className="relative z-10">
                                <div className="flex items-center gap-2 mb-6">
                                    <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                                        <Lock size={20} className="text-a2s-gold" />
                                    </div>
                                    <h3 className="font-serif text-xl font-bold">Early Access</h3>
                                </div>

                                <h2 className="font-serif text-2xl font-bold mb-2">Join the Phase 2 Waitlist</h2>
                                <p className="text-sm text-gray-400 mb-6 leading-relaxed">
                                    Unlock the next wave of AI-driven home design for Indian homes.
                                </p>

                                <ul className="space-y-4 mb-6">
                                    <li className="flex gap-3">
                                        <span className="w-9 h-9 rounded-lg bg-a2s-gold/20 flex items-center justify-center flex-shrink-0">
                                            <Box size={16} className="text-a2s-gold" />
                                        </span>
                                        <div>
                                            <h4 className="text-sm font-bold text-white">Video-to-3D Room Staging</h4>
                                            <p className="text-xs text-gray-400">Scan your room to create interactive layouts.</p>
                                        </div>
                                    </li>
                                    <li className="flex gap-3">
                                        <span className="w-9 h-9 rounded-lg bg-a2s-gold/20 flex items-center justify-center flex-shrink-0">
                                            <ShoppingBag size={16} className="text-a2s-gold" />
                                        </span>
                                        <div>
                                            <h4 className="text-sm font-bold text-white">Artisan Marketplace</h4>
                                            <p className="text-xs text-gray-400">Shop curated home decor from local artisans.</p>
                                        </div>
                                    </li>
                                </ul>

                                <div className="bg-black/30 rounded-xl p-4 mb-4">
                                    <div className="flex justify-between items-center text-xs text-gray-400 mb-2">
                                        <span>Waitlist progress</span>
                                        <span className="text-white font-bold">#1,240 in line</span>
                                    </div>
                                    <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-a2s-gold to-a2s-gold-light rounded-full transition-all"
                                            style={{ width: '75%' }}
                                        />
                                    </div>
                                </div>

                                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                                    <p className="text-center text-xs text-gray-400 mb-2">
                                        Share your code to move up + get 5 free AI queries
                                    </p>
                                    <div className="bg-black/50 rounded-lg px-4 py-3 flex justify-between items-center gap-2">
                                        <span className="font-mono text-sm font-bold text-white truncate">{waitlistCode}</span>
                                        <button
                                            type="button"
                                            onClick={copyCode}
                                            className="flex-shrink-0 flex items-center gap-1.5 text-xs text-gray-400 hover:text-a2s-gold transition"
                                        >
                                            <Copy size={14} /> {copied ? 'Copied!' : 'Copy'}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
