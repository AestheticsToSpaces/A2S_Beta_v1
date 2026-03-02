import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowRight,
    ArrowLeft,
    Check,
    Sofa,
    BedDouble,
    ChefHat,
    UtensilsCrossed,
    IndianRupee,
    Sparkles,
    Minus,
    Palette,
    Landmark,
    Factory,
    Gem,
} from 'lucide-react';
import { getOnboardingPreferences, setOnboardingPreferences } from '../utils/storage';

const ROOMS = [
    { id: 'Living Room', label: 'Living Room', tagline: 'Where you unwind & entertain', Icon: Sofa },
    { id: 'Bedroom', label: 'Bedroom', tagline: 'Your personal retreat', Icon: BedDouble },
    { id: 'Kitchen', label: 'Kitchen', tagline: 'Heart of the home', Icon: ChefHat },
    { id: 'Dining', label: 'Dining', tagline: 'Gather & celebrate', Icon: UtensilsCrossed },
];

const BUDGET_OPTIONS = [
    { value: 'low', label: 'Shoestring', sublabel: 'Under ₹50k' },
    { value: 'mid', label: 'Comfortable', sublabel: '₹50k – ₹1.5L' },
    { value: 'high', label: 'Premium', sublabel: '₹1.5L – ₹5L' },
    { value: 'ultra', label: 'Luxury', sublabel: '₹5L+' },
];

const STYLE_OPTIONS = [
    { id: 'Modern', tagline: 'Clean lines, smart & sleek', Icon: Sparkles },
    { id: 'Minimal', tagline: 'Less is more', Icon: Minus },
    { id: 'Boho', tagline: 'Relaxed, natural & layered', Icon: Palette },
    { id: 'Traditional', tagline: 'Classic & timeless', Icon: Landmark },
    { id: 'Industrial', tagline: 'Raw, bold & functional', Icon: Factory },
    { id: 'Luxury', tagline: 'Refined & opulent', Icon: Gem },
];

const Onboarding = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [preferences, setPreferences] = useState({
        room: '',
        budget: '',
        styles: [],
    });

    useEffect(() => {
        const saved = getOnboardingPreferences();
        if (saved) setPreferences(saved);
    }, []);

    const nextStep = () => {
        if (step < 3) setStep(step + 1);
        else {
            setOnboardingPreferences(preferences);
            navigate('/gallery');
        }
    };

    const prevStep = () => {
        if (step > 1) setStep(step - 1);
    };

    const toggleStyle = (style) => {
        const current = preferences.styles;
        if (current.includes(style)) {
            setPreferences({ ...preferences, styles: current.filter((s) => s !== style) });
        } else {
            setPreferences({ ...preferences, styles: [...current, style] });
        }
    };

    const canProceed =
        (step === 1 && preferences.room) ||
        (step === 2 && preferences.budget) ||
        (step === 3 && preferences.styles.length > 0);

    return (
        <div className="min-h-screen bg-main text-main flex items-center justify-center p-4 pt-24 pb-16 transition-all duration-1000">
            <div className="w-full max-w-2xl">
                {/* Progress */}
                <div className="flex items-center justify-between mb-10">
                    <div className="flex gap-1.5 flex-1 max-w-xs">
                        {[1, 2, 3].map((s) => (
                            <div
                                key={s}
                                className={`h-2 flex-1 rounded-full transition-all duration-300 ${step >= s ? 'bg-accent' : 'bg-surface/15'
                                    } ${step === s ? 'ring-2 ring-accent/50 ring-offset-2 ring-offset-main' : ''}`}
                            />
                        ))}
                    </div>
                    <span className="text-xs font-bold text-white/50 uppercase tracking-wider ml-4">
                        Step {step} of 3
                    </span>
                </div>

                {/* Step 1: Room */}
                {step === 1 && (
                    <div className="animate-fade-in">
                        <h2 className="font-serif text-3xl md:text-4xl font-bold mb-2">
                            Which space are you designing?
                        </h2>
                        <p className="text-white/60 mb-8">We’ll tailor ideas to this room.</p>
                        <div className="grid grid-cols-2 gap-4">
                            {ROOMS.map(({ id, label, tagline, Icon }) => (
                                <button
                                    key={id}
                                    onClick={() => setPreferences({ ...preferences, room: id })}
                                    className={`relative p-6 rounded-2xl text-left border-2 transition-all duration-200 flex flex-col gap-3 ${preferences.room === id
                                        ? 'border-accent bg-accent/20 text-main shadow-lg shadow-accent/25'
                                        : 'border-premium bg-surface/5 hover:border-accent/20 hover:bg-surface/10 text-main/90'
                                        }`}
                                >
                                    <Icon
                                        size={32}
                                        className={preferences.room === id ? 'text-accent' : 'text-main/50'}
                                    />
                                    <span className="text-lg font-serif font-semibold">{label}</span>
                                    <span className="text-sm text-white/60">{tagline}</span>
                                    {preferences.room === id && (
                                        <span className="absolute top-4 right-4">
                                            <Check size={20} className="text-accent" />
                                        </span>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 2: Budget */}
                {step === 2 && (
                    <div className="animate-fade-in">
                        <h2 className="font-serif text-3xl md:text-4xl font-bold mb-2">
                            What’s your budget range?
                        </h2>
                        <p className="text-white/60 mb-8">
                            We’ll show designs and products that fit.
                        </p>
                        <div className="space-y-3">
                            {BUDGET_OPTIONS.map((opt) => (
                                <button
                                    key={opt.value}
                                    onClick={() => setPreferences({ ...preferences, budget: opt.value })}
                                    className={`w-full p-5 rounded-2xl border-2 text-left flex items-center justify-between gap-4 transition-all duration-200 ${preferences.budget === opt.value
                                        ? 'border-accent bg-accent/20 text-main'
                                        : 'border-premium bg-surface/5 hover:border-accent/20 hover:bg-surface/10 text-main/90'
                                        }`}
                                >
                                    <div className="flex items-center gap-4">
                                        <span className="flex items-center justify-center w-10 h-10 rounded-xl bg-surface/10">
                                            <IndianRupee size={20} className={preferences.budget === opt.value ? 'text-accent' : 'text-main/60'} />
                                        </span>
                                        <div>
                                            <span className="text-lg font-semibold block">{opt.label}</span>
                                            <span className="text-sm text-white/60">{opt.sublabel}</span>
                                        </div>
                                    </div>
                                    {preferences.budget === opt.value && (
                                        <Check size={22} className="text-accent flex-shrink-0" />
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 3: Style */}
                {step === 3 && (
                    <div className="animate-fade-in">
                        <h2 className="font-serif text-3xl md:text-4xl font-bold mb-2">
                            Pick your vibe
                        </h2>
                        <p className="text-white/60 mb-8">
                            Select all that resonate — we’ll mix inspiration.
                        </p>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            {STYLE_OPTIONS.map(({ id, tagline, Icon }) => {
                                const selected = preferences.styles.includes(id);
                                return (
                                    <button
                                        key={id}
                                        onClick={() => toggleStyle(id)}
                                        className={`relative p-5 rounded-2xl border-2 text-center transition-all duration-200 flex flex-col items-center gap-2 min-h-[120px] justify-center ${selected
                                            ? 'border-accent bg-accent/20 text-main'
                                            : 'border-premium bg-surface/5 hover:border-accent/20 hover:bg-surface/10 text-main/90'
                                            }`}
                                    >
                                        {selected && (
                                            <span className="absolute top-3 right-3">
                                                <Check size={18} className="text-accent" />
                                            </span>
                                        )}
                                        <Icon
                                            size={28}
                                            className={selected ? 'text-accent' : 'text-main/50'}
                                        />
                                        <span className="font-semibold text-sm">{id}</span>
                                        <span className="text-xs text-white/55 leading-tight">{tagline}</span>
                                    </button>
                                );
                            })}
                        </div>
                        {preferences.styles.length > 0 && (
                            <p className="mt-4 text-sm text-white/50">
                                {preferences.styles.length} style{preferences.styles.length !== 1 ? 's' : ''} selected
                            </p>
                        )}
                    </div>
                )}

                {/* Navigation */}
                <div className="mt-12 flex items-center justify-between gap-4">
                    <button
                        onClick={prevStep}
                        className={`flex items-center gap-2 px-5 py-3 rounded-full font-semibold text-sm transition-all ${step === 1
                            ? 'invisible'
                            : 'text-white/70 hover:text-white hover:bg-white/10'
                            }`}
                    >
                        <ArrowLeft size={18} /> Back
                    </button>
                    <button
                        onClick={nextStep}
                        disabled={!canProceed}
                        className="flex items-center gap-2 bg-accent text-on-accent px-8 py-4 rounded-full font-bold uppercase tracking-wider hover:bg-accent/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-accent/30 focus-ring"
                    >
                        {step === 3 ? 'See my picks' : 'Next'} <ArrowRight size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Onboarding;
