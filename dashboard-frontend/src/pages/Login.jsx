import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';
import { LogIn, AlertCircle } from 'lucide-react';
import AuthLayout from '../components/auth/AuthLayout';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const from = location.state?.from?.pathname || '/';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const { user, error: loginError } = await login(email, password);

        setLoading(false);

        if (loginError) {
            setError(loginError);
        } else if (user) {
            navigate(from, { replace: true });
        }
    };

    return (
        <AuthLayout>
            {/* Form Content */}
            <div>
                {/* Header */}
                <div style={{ marginBottom: '2rem' }}>
                    <h2 style={{
                        fontSize: '2rem',
                        fontWeight: '700',
                        color: 'var(--text-primary)',
                        margin: '0 0 0.5rem 0',
                        letterSpacing: '-0.02em'
                    }}>
                        Welcome back
                    </h2>
                    <p style={{
                        fontSize: '0.95rem',
                        color: 'var(--text-muted)',
                        margin: 0
                    }}>
                        Sign in to your account
                    </p>
                </div>

                {/* Error Message */}
                {error && (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.875rem',
                        marginBottom: '1.5rem',
                        borderRadius: '12px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.3)'
                    }}>
                        <AlertCircle size={16} style={{ color: 'var(--danger)' }} />
                        <p style={{ fontSize: '0.875rem', color: 'var(--danger)', margin: 0 }}>{error}</p>
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                    <div>
                        <label style={{
                            display: 'block',
                            fontSize: '0.8125rem',
                            fontWeight: '500',
                            color: 'var(--text-secondary)',
                            marginBottom: '0.5rem'
                        }}>
                            Email
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '0.875rem 0rem',
                                borderRadius: '12px',
                                fontSize: '0.9375rem',
                                background: 'rgba(255, 255, 255, 0.05)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                color: 'var(--text-primary)',
                                outline: 'none',
                                transition: 'all 0.2s'
                            }}
                            placeholder=" your@email.com"
                            required
                            onFocus={(e) => e.target.style.borderColor = 'var(--accent)'}
                            onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'}
                        />
                    </div>

                    <div>
                        <label style={{
                            display: 'block',
                            fontSize: '0.8125rem',
                            fontWeight: '500',
                            color: 'var(--text-secondary)',
                            marginBottom: '0.5rem'
                        }}>
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '0.875rem 0rem',
                                borderRadius: '12px',
                                fontSize: '0.9375rem',
                                background: 'rgba(255, 255, 255, 0.05)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                color: 'var(--text-primary)',
                                outline: 'none',
                                transition: 'all 0.2s'
                            }}
                            placeholder=" ••••••••••••••••••"
                            required
                            onFocus={(e) => e.target.style.borderColor = 'var(--accent)'}
                            onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            width: '100%',
                            padding: '0.875rem',
                            borderRadius: '12px',
                            fontSize: '0.9375rem',
                            fontWeight: '600',
                            background: loading ? 'var(--border)' : 'var(--accent)',
                            color: '#ffffff',
                            border: 'none',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem',
                            transition: 'all 0.2s',
                            boxShadow: loading ? 'none' : '0 4px 12px rgba(0, 212, 255, 0.3)'
                        }}
                        onMouseEnter={(e) => !loading && (e.target.style.background = 'var(--accent-hover)')}
                        onMouseLeave={(e) => !loading && (e.target.style.background = 'var(--accent)')}
                    >
                        {loading ? (
                            'Signing in...'
                        ) : (
                            <>
                                <LogIn size={18} />
                                Sign in
                            </>
                        )}
                    </button>
                </form>

                {/* Footer */}
                <div style={{ marginTop: '2rem', textAlign: 'center' }}>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', margin: 0 }}>
                        © 2026 BVMT AI. All rights reserved.
                    </p>
                </div>
            </div>
        </AuthLayout>
    );
};

export default Login;
