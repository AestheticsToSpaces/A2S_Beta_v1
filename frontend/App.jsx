import React, { useEffect } from 'react';
import { HashRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import Gallery from './pages/Gallery';
import DesignDetail from './pages/DesignDetail';
import AIConsultant from './pages/AIConsultant';
import Onboarding from './pages/Onboarding';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ThreeDSpace from './pages/ThreeDSpace';
import NotFound from './pages/NotFound';

// Scroll to top on route change
const ScrollToTop = () => {
    const { pathname } = useLocation();
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [pathname]);
    return null;
};

import AIStylistWidget from './components/AIStylistWidget';

const App = () => {
    return (
        <ErrorBoundary>
            <Router>
                <ScrollToTop />
                <div className="flex flex-col min-h-screen">
                    <Navbar />
                    <main className="flex-grow">
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/gallery" element={<Gallery />} />
                            <Route path="/design/:id" element={<DesignDetail />} />
                            <Route path="/consultant" element={<AIConsultant />} />
                            <Route path="/onboarding" element={<Onboarding />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/3d-space" element={<ThreeDSpace />} />
                            <Route path="*" element={<NotFound />} />
                        </Routes>
                    </main>
                    <Footer />
                    <AIStylistWidget />
                </div>
            </Router>
        </ErrorBoundary>
    );
};

export default App;
