import React, { useState } from 'react';
import { User, Bell, Shield, Moon, Globe, Check, AlertTriangle } from 'lucide-react';

const Settings = () => {
    const [activeTab, setActiveTab] = useState('general');
    const [darkMode, setDarkMode] = useState(true);
    const [emailNotifs, setEmailNotifs] = useState(true);
    const [pushNotifs, setPushNotifs] = useState(true);

    const tabs = [
        { id: 'general', label: 'Général', icon: <User size={18} /> },
        { id: 'notifications', label: 'Notifications', icon: <Bell size={18} /> },
        { id: 'security', label: 'Sécurité', icon: <Shield size={18} /> },
    ];

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Paramètres</h1>
            </div>

            <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
                {/* Sidebar Navigation */}
                <div className="glass-card" style={{ width: '250px', padding: '1rem' }}>
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.75rem',
                                width: '100%',
                                padding: '1rem',
                                background: activeTab === tab.id ? 'var(--accent)' : 'transparent',
                                color: activeTab === tab.id ? 'white' : 'var(--text-secondary)',
                                border: 'none',
                                borderRadius: '12px',
                                cursor: 'pointer',
                                marginBottom: '0.5rem',
                                transition: 'all 0.2s',
                                fontWeight: activeTab === tab.id ? '600' : '400',
                                textAlign: 'left'
                            }}
                        >
                            {tab.icon}
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content Area */}
                <div style={{ flex: 1 }}>
                    {activeTab === 'general' && (
                        <div className="glass-card">
                            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Préférences Générales</h2>

                            <div style={{ marginBottom: '2rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', marginBottom: '1rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
                                            <Moon size={20} style={{ color: 'var(--accent)' }} />
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>Mode Sombre</div>
                                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Activer le thème sombre pour l'application</div>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setDarkMode(!darkMode)}
                                        style={{
                                            width: '48px',
                                            height: '24px',
                                            background: darkMode ? 'var(--accent)' : 'rgba(255,255,255,0.2)',
                                            borderRadius: '12px',
                                            position: 'relative',
                                            cursor: 'pointer',
                                            border: 'none',
                                            transition: 'background 0.2s'
                                        }}
                                    >
                                        <div style={{
                                            width: '20px',
                                            height: '20px',
                                            background: 'white',
                                            borderRadius: '50%',
                                            position: 'absolute',
                                            top: '2px',
                                            left: darkMode ? '26px' : '2px',
                                            transition: 'left 0.2s'
                                        }} />
                                    </button>
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
                                            <Globe size={20} style={{ color: 'var(--accent)' }} />
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>Langue</div>
                                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Sélectionner la langue de l'interface</div>
                                        </div>
                                    </div>
                                    <select style={{
                                        background: 'rgba(0,0,0,0.2)',
                                        border: '1px solid var(--border)',
                                        color: 'var(--text-primary)',
                                        padding: '0.5rem 1rem',
                                        borderRadius: '8px',
                                        outline: 'none'
                                    }}>
                                        <option value="fr">Français</option>
                                        <option value="en">English</option>
                                        <option value="ar">العربية</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'notifications' && (
                        <div className="glass-card">
                            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Préférences de Notification</h2>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                                    <div>
                                        <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>Notifications Email</div>
                                        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Recevoir des mises à jour par email</div>
                                    </div>
                                    <button
                                        onClick={() => setEmailNotifs(!emailNotifs)}
                                        style={{
                                            width: '48px',
                                            height: '24px',
                                            background: emailNotifs ? 'var(--accent)' : 'rgba(255,255,255,0.2)',
                                            borderRadius: '12px',
                                            position: 'relative',
                                            cursor: 'pointer',
                                            border: 'none',
                                            transition: 'background 0.2s'
                                        }}
                                    >
                                        <div style={{
                                            width: '20px',
                                            height: '20px',
                                            background: 'white',
                                            borderRadius: '50%',
                                            position: 'absolute',
                                            top: '2px',
                                            left: emailNotifs ? '26px' : '2px',
                                            transition: 'left 0.2s'
                                        }} />
                                    </button>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                                    <div>
                                        <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>Notifications Push</div>
                                        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Recevoir des notifications sur le navigateur</div>
                                    </div>
                                    <button
                                        onClick={() => setPushNotifs(!pushNotifs)}
                                        style={{
                                            width: '48px',
                                            height: '24px',
                                            background: pushNotifs ? 'var(--accent)' : 'rgba(255,255,255,0.2)',
                                            borderRadius: '12px',
                                            position: 'relative',
                                            cursor: 'pointer',
                                            border: 'none',
                                            transition: 'background 0.2s'
                                        }}
                                    >
                                        <div style={{
                                            width: '20px',
                                            height: '20px',
                                            background: 'white',
                                            borderRadius: '50%',
                                            position: 'absolute',
                                            top: '2px',
                                            left: pushNotifs ? '26px' : '2px',
                                            transition: 'left 0.2s'
                                        }} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'security' && (
                        <div className="glass-card">
                            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Sécurité du Compte</h2>

                            <form style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }} onSubmit={(e) => e.preventDefault()}>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Mot de passe actuel</label>
                                    <input type="password" style={{ width: '100%', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }} />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Nouveau mot de passe</label>
                                    <input type="password" style={{ width: '100%', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }} />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Confirmer le mot de passe</label>
                                    <input type="password" style={{ width: '100%', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }} />
                                </div>
                                <button type="submit" className="btn-primary" style={{ alignSelf: 'flex-start' }}>
                                    Mettre à jour
                                </button>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Settings;
