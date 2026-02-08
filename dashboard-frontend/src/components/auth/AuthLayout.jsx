import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const AuthLayout = ({ children }) => {
    const location = useLocation();
    const isLogin = location.pathname === '/login';

    return (
        <div className="auth-container">
            {/* Top Navigation Bar */}
            <div className="auth-header">
                <div className="auth-brand">BVMT AI</div>
                <div className="auth-nav">
                    <Link
                        to="/login"
                        className={`auth-nav-btn ${isLogin ? 'active' : ''}`}
                    >
                        Login
                    </Link>
                    <Link
                        to="/register"
                        className={`auth-nav-btn ${!isLogin ? 'active' : ''}`}
                    >
                        Register
                    </Link>
                </div>
            </div>

            {/* Main Content */}
            <div className="auth-content">
                {/* Left Side - Branding */}
                <div className="auth-logo-section">
                    <div className="auth-logo-container">
                        {/* AI Pulse Animation */}
                        <div className="ai-pulse-logo">
                            <div className="pulse-ring"></div>
                            <div className="pulse-ring"></div>
                            <div className="pulse-ring"></div>
                            <div className="logo-core">
                                <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="40" cy="40" r="35" stroke="currentColor" strokeWidth="2" opacity="0.3" />
                                    <path d="M25 40L35 50L55 30" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                                    <circle cx="40" cy="40" r="5" fill="currentColor" />
                                </svg>
                            </div>
                        </div>

                        {/* Brand Text */}
                        <h1 className="auth-main-title">BVMT AI</h1>
                        <p className="auth-subtitle">Système d'Assistant Intelligent de Trading</p>
                    </div>
                </div>

                {/* Right Side - Form */}
                <div className="auth-form-section">
                    <div className="glassmorphism-card">
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;
