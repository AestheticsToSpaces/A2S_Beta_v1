import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Send, User, Sparkles, Loader2, Layout, Box, Palette, ArrowLeft, MessageSquare } from 'lucide-react';
import { geminiService } from '../services/geminiService';

const AI_WELCOME = `Namaste. I am your A2S Design Architect. 

I curate spaces that transcend the ordinary. How may I assist your vision today?

• **Spatial Curation** — Living, Private, or Culinary spaces.
• **Aesthetic Philosophy** — From Modern Minimalism to Heritage Luxury.
• **Sourcing Strategy** — Indian craftsmanship & boutique selections.
• **Vastu Geometry** — Harmonizing the flow of your sanctuary.`;

const SUGGESTION_CHIPS = [
    'Minimalist sanctuary for small spaces',
    'Heritage luxury living room',
    'Vastu-aligned bedroom geometry',
    'Boutique kitchen sourcing',
    'Defining my aesthetic philosophy',
];

const AIConsultant = () => {
    const isAvailable = geminiService.isAvailable();
    const [messages, setMessages] = useState([
        {
            id: '1',
            role: 'ai',
            text: isAvailable
                ? AI_WELCOME
                : "The Architect is currently unavailable. Please ensure your configuration is complete.",
            timestamp: new Date(),
        },
    ]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async (text) => {
        if (!text.trim()) return;
        const userMessage = { id: Date.now().toString(), role: 'user', text: text.trim(), timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsLoading(true);

        try {
            const context = 'User is consulting the A2S Design Architect. Frame responses with "Quiet Luxury" and "Editorial" tone. Reference Gallery and 3D Studio.';
            const aiResponseText = await geminiService.getDesignAdvice(userMessage.text, context);
            setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'ai', text: aiResponseText, timestamp: new Date() }]);
        } catch (err) {
            setMessages(prev => [...prev, { id: 'err', role: 'ai', text: "Forgive me, I encountered a brief disruption in my reflections. Shall we try again?", timestamp: new Date() }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-main pt-32 pb-16 px-4 flex flex-col items-center transition-all duration-1000">
            <header className="max-w-2xl w-full mb-12 text-center">
                <span className="section-tag animate-fade-in-up">The Dialogue</span>
                <h1 className="font-serif text-5xl font-black text-main italic mb-4 animate-reveal">Design <span className="text-gradient-gold">Architect</span></h1>
                <p className="text-muted font-light tracking-wide">Conversational curation powered by neural aesthetics.</p>
            </header>

            <div className="w-full max-w-3xl glass-premium rounded-[48px] border border-white overflow-hidden flex flex-col h-[75vh] shadow-premium animate-fade-in-up">
                {/* Status Bar */}
                <div className="px-8 py-5 border-b border-premium flex items-center justify-between bg-surface/40">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-main flex items-center justify-center text-accent shadow-lg border border-premium">
                            <Sparkles size={20} />
                        </div>
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-main">Neural Assistant</p>
                            <div className="flex items-center gap-1.5">
                                <span className={`w-1.5 h-1.5 rounded-full ${isAvailable ? 'bg-green-400 animate-pulse' : 'bg-gray-300'}`} />
                                <span className="text-[9px] font-bold text-gray-400 uppercase tracking-widest">{isAvailable ? 'System Active' : 'Offline'}</span>
                            </div>
                        </div>
                    </div>
                    <Link to="/gallery" className="text-[9px] font-black uppercase tracking-widest text-accent hover:text-main transition-colors flex items-center gap-2">
                        Browse Gallery <ArrowLeft size={12} className="rotate-180" />
                    </Link>
                </div>

                {/* Conversation Field */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-surface/20 custom-scrollbar">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
                            <div className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center border ${msg.role === 'user' ? 'bg-surface border-premium text-main' : 'bg-main border-premium text-accent'}`}>
                                    {msg.role === 'user' ? <User size={14} /> : <Sparkles size={14} />}
                                </div>
                                <div className={`p-6 rounded-3xl text-sm leading-relaxed ${msg.role === 'user' ? 'bg-main text-on-accent rounded-tr-none shadow-premium' : 'bg-surface text-main rounded-tl-none border border-premium shadow-premium'}`}>
                                    {msg.text.split('\n').map((line, i) => (
                                        <p key={i} className={line === '' ? 'h-4' : 'mb-2 last:mb-0'}>
                                            {line.replace(/\*\*(.*?)\*\*/g, '$1')}
                                        </p>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}

                    {messages.length === 1 && (
                        <div className="pt-4 flex flex-wrap gap-3 justify-center">
                            {SUGGESTION_CHIPS.map(chip => (
                                <button
                                    key={chip}
                                    onClick={() => sendMessage(chip)}
                                    className="px-5 py-2.5 rounded-full bg-surface border border-premium text-[10px] font-bold text-muted hover:text-accent hover:border-accent hover:shadow-lg transition-all"
                                >
                                    {chip}
                                </button>
                            ))}
                        </div>
                    )}

                    {isLoading && (
                        <div className="flex justify-start animate-pulse">
                            <div className="flex gap-4 items-center">
                                <div className="w-8 h-8 rounded-full bg-main flex items-center justify-center text-accent"><Sparkles size={14} /></div>
                                <div className="px-6 py-4 bg-surface rounded-3xl rounded-tl-none border border-premium flex items-center gap-3">
                                    <Loader2 size={16} className="animate-spin text-accent" />
                                    <span className="text-[10px] font-black uppercase tracking-widest text-muted">Reflecting...</span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Field */}
                <div className="p-8 bg-surface/60 border-t border-premium">
                    <div className="relative group">
                        <textarea
                            rows="1"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage(inputText))}
                            placeholder="Share your aesthetic vision..."
                            className="w-full bg-surface border border-premium rounded-3xl py-5 pl-8 pr-20 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent/50 transition-all resize-none shadow-inner text-main"
                        />
                        <button
                            onClick={() => sendMessage(inputText)}
                            disabled={!inputText.trim() || isLoading}
                            className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-2xl bg-main text-on-accent flex items-center justify-center hover:bg-accent hover:text-on-accent transition-all disabled:opacity-20"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </div>
            </div>

            <footer className="mt-8 flex gap-8">
                <Link to="/3d-space" className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-muted hover:text-accent transition-colors">
                    <Box size={14} /> 3D Studio
                </Link>
                <Link to="/onboarding" className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-muted hover:text-accent transition-colors">
                    <Palette size={14} /> Style Philosophy
                </Link>
            </footer>
        </div>
    );
};

export default AIConsultant;
