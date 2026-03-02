import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, User, MapPin, ArrowRight, Sparkles, Lock } from 'lucide-react';
import { login, register } from '../services/api';
import { useToast } from '../hooks/useToast';
import ToastContainer from '../components/ToastContainer';

const Login = () => {
    const navigate = useNavigate();
    const { toasts, addToast, removeToast, toast } = useToast();
    const [isLogin, setIsLogin] = useState(true);
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [location, setLocation] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [validationErrors, setValidationErrors] = useState({});

    // Email validation regex
    const validateEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    };

    // Password strength validation
    const validatePassword = (password) => {
        const errors = [];
        if (password.length < 8) errors.push('Password must be at least 8 characters');
        if (!/[A-Z]/.test(password)) errors.push('Include at least one uppercase letter');
        if (!/[a-z]/.test(password)) errors.push('Include at least one lowercase letter');
        if (!/[0-9]/.test(password)) errors.push('Include at least one number');
        return errors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setValidationErrors({});
        setLoading(true);

        const trimmedEmail = email.trim().toLowerCase();
        const trimmedPassword = password.trim();
        const errors = {};

        // Validate email
        if (!trimmedEmail) {
            errors.email = 'Email is required';
        } else if (!validateEmail(trimmedEmail)) {
            errors.email = 'Please enter a valid email address';
        }

        // Validate password
        if (!trimmedPassword) {
            errors.password = 'Password is required';
        } else if (!isLogin) {
            // Password strength only for registration
            const passwordErrors = validatePassword(trimmedPassword);
            if (passwordErrors.length > 0) {
                errors.password = passwordErrors[0]; // Show first error
            }
        }

        // Validate name for registration
        if (!isLogin) {
            const trimmedName = name.trim();
            if (!trimmedName) {
                errors.name = 'Name is required';
            } else if (trimmedName.length < 2) {
                errors.name = 'Name must be at least 2 characters';
            }
        }

        if (Object.keys(errors).length > 0) {
            setValidationErrors(errors);
            setLoading(false);
            toast.error('Please fix the errors in the form');
            return;
        }

        try {
            if (isLogin) {
                await login(trimmedEmail, trimmedPassword);
                toast.success('Welcome back!');
            } else {
                await register(name.trim(), trimmedEmail, trimmedPassword, location.trim());
                toast.success('Account created successfully!');
            }
            // Small delay to show toast before navigation
            setTimeout(() => {
                navigate('/dashboard', { replace: true });
            }, 500);
        } catch (err) {
            const errorMsg = err.response?.data?.message || err.message || 'An error occurred. Please try again.';
            setError(errorMsg);
            toast.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };


    return (
        <>
            <ToastContainer toasts={toasts} removeToast={removeToast} />
            <div className="min-h-screen bg-gradient-to-b from-a2s-cream/50 to-white pt-24 pb-16 flex items-center justify-center px-4">
                <div className="w-full max-w-md">
                    <div className="bg-white rounded-2xl luxury-shadow border border-gray-100 p-8 md:p-10">
                        <div className="text-center mb-8">
                            <div className="w-14 h-14 rounded-2xl bg-a2s-gold/15 flex items-center justify-center mx-auto mb-4">
                                <Sparkles size={28} className="text-a2s-gold" />
                            </div>
                            <h1 className="font-serif text-2xl md:text-3xl font-bold text-a2s-charcoal">
                                {isLogin ? 'Welcome Back' : 'Join A2S'}
                            </h1>
                            <span className="section-underline block mt-2 mb-3" aria-hidden="true" />
                            <p className="text-gray-600 text-sm">
                                {isLogin
                                    ? 'Sign in to access your designs and dashboard.'
                                    : 'Create an account to start your design journey.'}
                            </p>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-5">
                            {error && (
                                <div className="p-3 rounded-xl bg-red-50 border border-red-100 text-red-700 text-sm">
                                    {error}
                                </div>
                            )}

                            {!isLogin && (
                                <div>
                                    <label htmlFor="login-name" className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">
                                        Name
                                    </label>
                                    <div className="relative">
                                        <User size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                                        <input
                                            id="login-name"
                                            type="text"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                            placeholder="e.g. Anjali Sharma"
                                            className={`w-full pl-11 pr-4 py-3 rounded-xl border ${validationErrors.name ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-gray-200 focus:border-a2s-gold focus:ring-a2s-gold/20'} focus:ring-2 outline-none transition text-a2s-charcoal placeholder:text-gray-400`}
                                            autoComplete="name"
                                        />
                                    </div>
                                    {validationErrors.name && <p className="text-red-600 text-xs mt-1">{validationErrors.name}</p>}
                                </div>
                            )}

                            <div>
                                <label htmlFor="login-email" className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">
                                    Email
                                </label>
                                <div className="relative">
                                    <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                                    <input
                                        id="login-email"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="e.g. you@example.com"
                                        className={`w-full pl-11 pr-4 py-3 rounded-xl border ${validationErrors.email ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-gray-200 focus:border-a2s-gold focus:ring-a2s-gold/20'} focus:ring-2 outline-none transition text-a2s-charcoal placeholder:text-gray-400`}
                                        autoComplete="email"
                                    />
                                </div>
                                {validationErrors.email && <p className="text-red-600 text-xs mt-1">{validationErrors.email}</p>}
                            </div>

                            {!isLogin && (
                                <div>
                                    <label htmlFor="login-location" className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">
                                        City <span className="text-gray-400 font-normal">(optional)</span>
                                    </label>
                                    <div className="relative">
                                        <MapPin size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                                        <input
                                            id="login-location"
                                            type="text"
                                            value={location}
                                            onChange={(e) => setLocation(e.target.value)}
                                            placeholder="e.g. Mumbai, India"
                                            className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-200 focus:border-a2s-gold focus:ring-2 focus:ring-a2s-gold/20 outline-none transition text-a2s-charcoal placeholder:text-gray-400"
                                            autoComplete="address-level2"
                                        />
                                    </div>
                                </div>
                            )}

                            <div>
                                <label htmlFor="login-password" className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">
                                    Password
                                </label>
                                <div className="relative">
                                    <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                                    <input
                                        id="login-password"
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder={isLogin ? "Enter your password" : "Min. 8 characters"}
                                        className={`w-full pl-11 pr-4 py-3 rounded-xl border ${validationErrors.password ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-gray-200 focus:border-a2s-gold focus:ring-a2s-gold/20'} focus:ring-2 outline-none transition text-a2s-charcoal placeholder:text-gray-400`}
                                        autoComplete={isLogin ? "current-password" : "new-password"}
                                    />
                                </div>
                                {validationErrors.password && <p className="text-red-600 text-xs mt-1">{validationErrors.password}</p>}
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full btn-primary py-4 flex items-center justify-center gap-2 mt-6 disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')} <ArrowRight size={18} />
                            </button>
                        </form>

                        <p className="text-center text-sm text-gray-600 mt-6">
                            {isLogin ? "Don't have an account? " : "Already have an account? "}
                            <button
                                onClick={() => setIsLogin(!isLogin)}
                                className="text-a2s-gold font-semibold hover:text-a2s-charcoal transition"
                            >
                                {isLogin ? 'Sign up' : 'Sign in'}
                            </button>
                        </p>
                    </div>

                    <p className="text-center mt-6 text-sm text-gray-600">
                        <Link to="/" className="text-a2s-gold font-semibold hover:text-a2s-charcoal transition">
                            ← Back to home
                        </Link>
                    </p>
                </div>
            </div>
        </>
    );
};

export default Login;
