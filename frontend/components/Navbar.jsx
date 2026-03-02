import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Heart, User, Search, Box, X, LogOut, Palette, ChevronDown } from 'lucide-react';
import { getSavedDesignIds, getUser, clearUser } from '../utils/storage';
import { getUserProfile } from '../services/api';

const NAV_LINKS = [
    { to: '/gallery', label: 'Gallery' },
    { to: '/3d-space', label: '3D Space', icon: Box },
    { to: '/consultant', label: 'AI Consultant' },
    { to: '/dashboard', label: 'Dashboard' },
];

const Navbar = () => {
    const location = useLocation();
    const [savedCount, setSavedCount] = useState(0);
    const [mobileOpen, setMobileOpen] = useState(false);
    // Read synchronously first so Sign In button renders immediately
    const [user, setUser] = useState(() => {
        try {
            const raw = localStorage.getItem('user');
            if (!raw || raw === 'null') return null;
            return JSON.parse(raw);
        } catch { return null; }
    });
    const [accountOpen, setAccountOpen] = useState(false);
    const [atmosOpen, setAtmosOpen] = useState(false);
    const [atmosphere, setAtmosphere] = useState(localStorage.getItem('a2s-atmosphere') || 'parchment');

    // Atmosphere effect
    useEffect(() => {
        document.body.setAttribute('data-atmosphere', atmosphere);
        localStorage.setItem('a2s-atmosphere', atmosphere);
    }, [atmosphere]);

    const ATMOSPHERES = [
        { id: 'parchment', label: 'Classic Parchment', color: '#F5F1E9' },
        { id: 'noir', label: 'Midnight Noir', color: '#121212' },
        { id: 'emerald', label: 'Forest Emerald', color: '#0B1A14' },
        { id: 'indigo', label: 'Royal Indigo', color: '#0D1117' },
    ];

    // Load user: try localStorage first, fallback to backend API if token exists
    useEffect(() => {
        const loadUser = async () => {
            // Try localStorage first
            const localUser = await getUser();
            if (localUser) { setUser(localUser); return; }
            // If token exists but no local user, fetch from backend and cache it
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const profile = await getUserProfile();
                    if (profile) {
                        // Cache to localStorage so Navbar can read it next time
                        localStorage.setItem('user', JSON.stringify(profile));
                        setUser(profile);
                    }
                } catch (e) {
                    console.warn('Could not load user profile:', e);
                }
            }
        };
        loadUser();
    }, []);

    useEffect(() => {
        setSavedCount(getSavedDesignIds().length);
    }, [location.pathname]);

    useEffect(() => {
        const handler = () => setSavedCount(getSavedDesignIds().length);
        window.addEventListener('a2s-saved-update', handler);
        return () => window.removeEventListener('a2s-saved-update', handler);
    }, []);

    useEffect(() => {
        const handler = () => getUser().then(setUser);
        window.addEventListener('a2s-auth-change', handler);
        return () => window.removeEventListener('a2s-auth-change', handler);
    }, []);

    useEffect(() => {
        setMobileOpen(false);
        setAccountOpen(false);
    }, [location.pathname]);

    const isActive = (path) => location.pathname === path;

    const handleLogout = async () => {
        await clearUser();
        setAccountOpen(false);
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass-premium border-b border-white/20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16 md:h-18">
                    <Link to="/" className="font-serif text-2xl md:text-3xl font-black tracking-tight text-main flex items-center gap-2 group">
                        <span className="text-gradient-gold">A2S</span>
                        <span className="hidden md:block w-px h-6 bg-gray-200 mx-1" />
                        <span className="text-gray-400 font-medium text-xs uppercase tracking-[0.3em] hidden md:block group-hover:text-accent transition-colors">Aesthetics To Spaces</span>
                    </Link>

                    <div className="hidden md:flex items-center gap-2">
                        {NAV_LINKS.map(({ to, label, icon: Icon }) => (
                            <Link
                                key={to}
                                to={to}
                                className={`relative px-5 py-2 rounded-full text-[11px] font-black uppercase tracking-widest transition-all ${isActive(to)
                                    ? 'text-main bg-accent/10'
                                    : 'text-gray-500 hover:text-main hover:bg-gray-50'
                                    }`}
                            >
                                {Icon ? <span className="flex items-center gap-2"><Icon size={14} /> {label}</span> : label}
                                {isActive(to) && (
                                    <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-accent rounded-full" />
                                )}
                            </Link>
                        ))}
                    </div>

                    <div className="flex items-center gap-1">
                        {/* Atmosphere Selector */}
                        <div className="relative">
                            <button
                                onClick={() => setAtmosOpen(!atmosOpen)}
                                className="p-2.5 text-gray-500 hover:text-accent hover:bg-gray-100 rounded-lg transition-all duration-500 flex items-center gap-1 group"
                                aria-label="Switch Atmosphere"
                            >
                                <Palette size={20} className="group-hover:rotate-12 transition-transform" />
                                <ChevronDown size={12} className={`transition-transform duration-500 ${atmosOpen ? 'rotate-180' : ''}`} />
                            </button>

                            {atmosOpen && (
                                <>
                                    <div className="fixed inset-0 z-40" onClick={() => setAtmosOpen(false)} />
                                    <div className="absolute right-0 top-full mt-3 w-64 glass-premium rounded-3xl shadow-2xl z-50 py-3 animate-fade-in border border-white/20">
                                        <div className="px-5 py-2 border-b border-gray-100/10 mb-2">
                                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Architectural Atmosphere</p>
                                        </div>
                                        {ATMOSPHERES.map((at) => (
                                            <button
                                                key={at.id}
                                                onClick={() => { setAtmosphere(at.id); setAtmosOpen(false); }}
                                                className={`w-full flex items-center gap-4 px-5 py-3 text-[11px] font-bold transition-all hover:bg-white/5 ${atmosphere === at.id ? 'text-accent bg-accent/5' : 'text-gray-500 hover:text-accent'}`}
                                            >
                                                <div className="w-4 h-4 rounded-full border border-white/20 shadow-sm" style={{ backgroundColor: at.color }} />
                                                <span className="uppercase tracking-widest">{at.label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>

                        <button type="button" className="p-2.5 text-gray-500 hover:text-accent hover:bg-gray-100 rounded-lg transition" aria-label="Search">
                            <Search size={20} />
                        </button>
                        <Link to="/dashboard" className="p-2.5 text-gray-500 hover:text-accent rounded-lg transition relative" aria-label="Saved designs">
                            <Heart size={20} />
                            {savedCount > 0 && (
                                <span className="absolute top-1.5 right-1.5 min-w-[18px] h-[18px] flex items-center justify-center bg-red-500 text-white text-[10px] font-bold rounded-full px-1">
                                    {savedCount > 99 ? '99+' : savedCount}
                                </span>
                            )}
                        </Link>
                        {user ? (
                            <div className="relative hidden sm:block group">
                                <button
                                    type="button"
                                    className="px-4 py-2 rounded-full bg-white border border-black text-black text-[11px] font-black uppercase tracking-widest transition group-hover:bg-black group-hover:text-white flex items-center gap-2"
                                    aria-label="Account"
                                >
                                    <User size={14} />
                                    <span>{user?.name?.split(' ')[0] || user?.email?.split('@')[0] || 'Account'}</span>
                                </button>
                                {/* Hover dropdown */}
                                <div className="absolute right-0 top-full pt-2 w-56 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                                    <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 py-2">
                                        <div className="px-5 py-3 border-b border-gray-100">
                                            <p className="text-xs font-black text-gray-900 uppercase tracking-widest">{user?.name || 'User'}</p>
                                            <p className="text-[10px] text-gray-500 mt-0.5">{user?.email}</p>
                                        </div>
                                        <Link
                                            to="/dashboard"
                                            className="block px-5 py-3 text-[11px] font-bold text-gray-700 hover:text-black hover:bg-gray-50 transition"
                                        >
                                            My Dashboard
                                        </Link>
                                        <button
                                            type="button"
                                            onClick={handleLogout}
                                            className="w-full flex items-center gap-2 px-5 py-3 text-[11px] font-bold text-red-500 hover:bg-red-50 transition text-left"
                                        >
                                            <LogOut size={14} /> Log out
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <Link
                                to="/login"
                                className="hidden sm:flex items-center gap-2 px-5 py-2.5 rounded-full text-[11px] font-black uppercase tracking-widest bg-white border border-black text-black hover:bg-black hover:text-white transition-all duration-300 shadow-sm"
                            >
                                <User size={14} />
                                Sign In
                            </Link>
                        )}
                        <button
                            type="button"
                            onClick={() => setMobileOpen(!mobileOpen)}
                            className="md:hidden p-2.5 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                            aria-label="Menu"
                        >
                            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>

                {/* Mobile menu */}
                {mobileOpen && (
                    <div className="md:hidden animate-slide-down py-4 border-t border-gray-200/80 bg-main/95 backdrop-blur-sm -mx-4 px-4 rounded-b-2xl shadow-lg">
                        <div className="flex flex-col gap-1">
                            {NAV_LINKS.map(({ to, label, icon: Icon }) => (
                                <Link
                                    key={to}
                                    to={to}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors ${isActive(to) ? 'bg-accent/20 text-main font-semibold' : 'text-gray-700 hover:bg-accent/10 hover:text-main'
                                        }`}
                                >
                                    {Icon && <Icon size={18} />}
                                    {label}
                                </Link>
                            ))}
                            <div className="mt-4 pt-4 border-t border-gray-100/10 space-y-2">
                                <p className="px-4 text-[10px] font-black uppercase tracking-widest text-gray-400">Atmosphere</p>
                                <div className="grid grid-cols-2 gap-2 px-2">
                                    {ATMOSPHERES.map((at) => (
                                        <button
                                            key={at.id}
                                            onClick={() => { setAtmosphere(at.id); setMobileOpen(false); }}
                                            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${atmosphere === at.id ? 'bg-accent/10 text-accent' : 'bg-white/5 text-gray-500'}`}
                                        >
                                            <div className="w-3 h-3 rounded-full border border-white/20" style={{ backgroundColor: at.color }} />
                                            {at.id}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            {user ? (
                                <div className="mt-2 pt-2 border-t border-gray-200">
                                    <p className="px-4 py-1 text-xs text-gray-500 truncate">{user.name}</p>
                                    <Link to="/dashboard" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-gray-700 hover:bg-accent/10" onClick={() => setMobileOpen(false)}>
                                        Dashboard
                                    </Link>
                                    <button type="button" onClick={() => { handleLogout(); setMobileOpen(false); }} className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 w-full text-left">
                                        <LogOut size={18} /> Log out
                                    </button>
                                </div>
                            ) : (
                                <Link to="/login" className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold text-accent mt-2 border-t border-gray-200 pt-2" onClick={() => setMobileOpen(false)}>
                                    Sign in
                                </Link>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
