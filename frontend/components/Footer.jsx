import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Linkedin } from 'lucide-react';

const Footer = () => {
    return (
        <footer className="bg-main text-main pt-16 pb-10 mt-24 border-t border-premium transition-all duration-1000">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
                    <div className="md:col-span-1">
                        <h3 className="font-serif text-2xl font-bold text-accent mb-4">A2S</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            Democratizing interior design for every Indian home. Inspiration, budgeting, and sourcing in one workflow.
                        </p>
                    </div>

                    <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-5">Features</h4>
                        <ul className="space-y-3 text-sm text-muted">
                            <li><Link to="/gallery" className="hover:text-accent transition-colors">Smart Room Gallery</Link></li>
                            <li><Link to="/consultant" className="hover:text-accent transition-colors">AI Consultant</Link></li>
                            <li><Link to="/3d-space" className="hover:text-accent transition-colors inline-flex items-center gap-1.5">3D Visualization <span className="text-[10px] bg-accent/20 text-accent px-1.5 py-0.5 rounded">Beta</span></Link></li>
                            <li><Link to="/3d-space" className="hover:text-accent transition-colors">Vastu Audit</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-5">Company</h4>
                        <ul className="space-y-3 text-sm text-gray-300">
                            <li><Link to="/dashboard" className="hover:text-accent transition-colors">About Us</Link></li>
                            <li><Link to="/dashboard" className="hover:text-accent transition-colors">Careers</Link></li>
                            <li><Link to="/dashboard" className="hover:text-accent transition-colors">Privacy Policy</Link></li>
                            <li><Link to="/dashboard" className="hover:text-accent transition-colors">Terms of Service</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-5">Connect</h4>
                        <div className="flex gap-4">
                            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className="p-2.5 rounded-xl bg-white/5 text-muted hover:text-accent hover:bg-white/10 transition" aria-label="Facebook"><Facebook size={20} /></a>
                            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className="p-2.5 rounded-xl bg-white/5 text-muted hover:text-accent hover:bg-white/10 transition" aria-label="Instagram"><Instagram size={20} /></a>
                            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="p-2.5 rounded-xl bg-white/5 text-muted hover:text-accent hover:bg-white/10 transition" aria-label="Twitter"><Twitter size={20} /></a>
                            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="p-2.5 rounded-xl bg-white/5 text-muted hover:text-accent hover:bg-white/10 transition" aria-label="LinkedIn"><Linkedin size={20} /></a>
                        </div>
                        <div className="mt-8">
                            <p className="text-xs text-muted mb-3">Subscribe for design tips</p>
                            <div className="flex rounded-xl overflow-hidden border border-premium focus-within:border-accent/50 transition-colors">
                                <input type="email" placeholder="Your email" className="bg-surface/50 text-main text-sm px-4 py-3 w-full focus:outline-none" />
                                <button type="button" className="bg-accent text-on-accent px-5 py-3 text-sm font-bold hover:bg-accent/90 transition-colors">Go</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="border-t border-premium mt-16 pt-8 text-center text-xs text-muted">
                    &copy; 2026 A2S Design Technologies Pvt Ltd. All rights reserved. Made with ❤️ in India.
                </div>
            </div>
        </footer>
    );
};

export default Footer;
