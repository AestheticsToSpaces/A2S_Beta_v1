import React, { useState } from 'react';
import { Sparkles, X, Send, User, Loader2 } from 'lucide-react';
import { geminiService } from '../services/geminiService';

const AIStylistWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { id: '1', role: 'ai', text: "Welcome to A2S. I am your personal design architect. How can I refine your space today?" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;
        const userMsg = { id: Date.now().toString(), role: 'user', text: input.trim() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const aiText = await geminiService.getDesignAdvice(userMsg.text, "Mini stylist widget. Keep it brief and elegant.");
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'ai', text: aiText }]);
        } catch (e) {
            setMessages(prev => [...prev, { id: 'err', role: 'ai', text: "Forgive me, the inspiration is momentarily blocked." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-8 right-8 z-[100] flex flex-col items-end gap-4 pointer-events-none">
            {/* Chat Window */}
            {isOpen && (
                <div className="w-[380px] h-[500px] glass-premium rounded-[40px] border border-premium shadow-premium flex flex-col overflow-hidden animate-fade-in-up pointer-events-auto origin-bottom-right transition-all duration-1000">
                    <header className="px-8 py-5 border-b border-premium flex items-center justify-between bg-surface/40">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-main flex items-center justify-center text-accent shadow-lg border border-premium">
                                <Sparkles size={14} />
                            </div>
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-main">Design Stylist</span>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-gray-300 hover:text-main transition-colors">
                            <X size={18} />
                        </button>
                    </header>

                    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-surface/20 custom-scrollbar">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`p-4 rounded-2xl text-xs leading-relaxed ${msg.role === 'user' ? 'bg-main text-on-accent rounded-tr-none shadow-premium' : 'bg-surface text-main rounded-tl-none border border-premium shadow-sm'}`}>
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start animate-pulse">
                                <div className="px-5 py-3 bg-surface rounded-2xl border border-premium flex items-center gap-2">
                                    <Loader2 size={12} className="animate-spin text-accent" />
                                    <span className="text-[9px] font-black uppercase tracking-widest text-muted">...</span>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="p-6 bg-surface/60 border-t border-premium">
                        <div className="relative">
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Refine your vision..."
                                className="w-full bg-offset/50 border border-premium rounded-2xl py-4 pl-6 pr-14 text-xs font-medium focus:ring-1 focus:ring-accent/30 transition-all text-main"
                            />
                            <button onClick={handleSend} className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-xl bg-main text-on-accent flex items-center justify-center hover:bg-accent hover:text-on-accent transition-all">
                                <Send size={14} />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`w-16 h-16 rounded-full bg-main text-on-accent flex items-center justify-center shadow-premium hover:shadow-premium-hover transition-all duration-1000 pointer-events-auto group border border-premium ${isOpen ? 'rotate-90 bg-surface !text-main' : 'hover:scale-110'}`}
                aria-label="Toggle AI Stylist"
            >
                {isOpen ? <X size={24} /> : (
                    <div className="relative">
                        <Sparkles size={28} className="text-accent group-hover:animate-pulse" />
                        {!isOpen && <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-main" />}
                    </div>
                )}
            </button>
        </div>
    );
};

export default AIStylistWidget;
