import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Filter, CheckCircle, AlertCircle, Info, ChevronDown, ArrowUpDown, Eye, TrendingUp, TrendingDown, X } from 'lucide-react';

const Alerts = () => {
    const [alerts, setAlerts] = useState([]);
    const [filters, setFilters] = useState([]);
    const [activeFilter, setActiveFilter] = useState('All');
    const [filterDropdownOpen, setFilterDropdownOpen] = useState(false);
    const [historyOpen, setHistoryOpen] = useState(false);
    const [reverseSort, setReverseSort] = useState(false);
    const [expandedAlerts, setExpandedAlerts] = useState(new Set());
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Mock history data
    const alertHistory = [
        {
            id: 'h1',
            symbol: 'BIAT',
            type: 'Anomalie',
            date: '2026-02-05 14:30',
            action: 'Position fermée à 126.20 TND',
            result: '+2.8%',
            success: true
        },
        {
            id: 'h2',
            symbol: 'SFBT',
            type: 'Prédiction',
            date: '2026-02-03 09:15',
            action: 'Achat de 50 actions à 12.10 TND',
            result: '+5.2%',
            success: true
        },
        {
            id: 'h3',
            symbol: 'SAH',
            type: 'Volatilité',
            date: '2026-02-01 16:45',
            action: 'Stop-loss déclenché à 11.50 TND',
            result: '-1.5%',
            success: false
        }
    ];

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const data = await api.getAlerts();
                setAlerts(data.alerts || []);
                setFilters(data.filters || []);
            } catch (err) {
                console.error("Error fetching alerts:", err);
                setError("Impossible de charger le flux d'alertes.");
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
    }, []);

    const toggleAlertDetails = (alertId) => {
        const newExpanded = new Set(expandedAlerts);
        if (newExpanded.has(alertId)) {
            newExpanded.delete(alertId);
        } else {
            newExpanded.add(alertId);
        }
        setExpandedAlerts(newExpanded);
    };

    const filteredAlerts = activeFilter === 'All'
        ? alerts
        : alerts.filter(a => a.type === activeFilter);

    // Sort alerts by timestamp with reverse option
    const sortedAlerts = [...filteredAlerts].sort((a, b) => {
        const comparison = new Date(b.timestamp) - new Date(a.timestamp);
        return reverseSort ? -comparison : comparison;
    });

    const getSeverityColor = (severity) => {
        switch (severity.toLowerCase()) {
            case 'high': return 'badge-danger';
            case 'medium': return 'badge-warning';
            case 'low': return 'badge-neutral';
            default: return 'badge-neutral';
        }
    };

    const getStatusIcon = (status) => {
        return status === 'Resolved'
            ? <CheckCircle size={18} className="text-success" />
            : <AlertCircle size={18} className="text-warning" />;
    };

    if (loading) return <div className="p-8 text-center" style={{ color: 'var(--secondary)' }}>Chargement des alertes...</div>;

    if (error) return (
        <div className="card text-danger" style={{ margin: '2rem', textAlign: 'center' }}>
            <div className="card-title">Erreur</div>
            <p>{error}</p>
        </div>
    );

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Surveillance & Alertes</h1>
            </div>

            <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem', alignItems: 'flex-start' }}>
                {/* Filter Section */}
                <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: filterDropdownOpen ? '1rem' : '0' }}>
                        <button
                            onClick={() => setFilterDropdownOpen(!filterDropdownOpen)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '0.75rem 1.25rem',
                                background: 'rgba(255, 255, 255, 0.05)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                borderRadius: '12px',
                                color: 'var(--text-primary)',
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                        >
                            <Filter size={18} style={{ color: 'var(--accent)' }} />
                            <span>Filtres</span>
                            <ChevronDown
                                size={16}
                                style={{
                                    color: 'var(--text-secondary)',
                                    transform: filterDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                                    transition: 'transform 0.2s'
                                }}
                            />
                        </button>


                    </div>

                    {/* Filter Buttons - Collapsible */}
                    {filterDropdownOpen && (
                        <div style={{
                            display: 'flex',
                            gap: '0.75rem',
                            flexWrap: 'wrap',
                            animation: 'slideDown 0.2s ease',
                            paddingTop: '0.5rem'
                        }}>
                            <button
                                style={{
                                    border: activeFilter === 'All' ? '1px solid var(--accent)' : '1px solid rgba(255, 255, 255, 0.1)',
                                    cursor: 'pointer',
                                    background: activeFilter === 'All' ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                                    color: activeFilter === 'All' ? 'var(--accent)' : 'var(--text-secondary)',
                                    padding: '0.6rem 1.25rem',
                                    fontSize: '0.875rem',
                                    borderRadius: '12px',
                                    fontWeight: activeFilter === 'All' ? '600' : '400',
                                    transition: 'all 0.2s'
                                }}
                                onClick={() => setActiveFilter('All')}
                            >
                                Tous
                            </button>
                            {filters.map(filter => (
                                <button
                                    key={filter}
                                    style={{
                                        border: activeFilter === filter ? '1px solid var(--accent)' : '1px solid rgba(255, 255, 255, 0.1)',
                                        cursor: 'pointer',
                                        background: activeFilter === filter ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                                        color: activeFilter === filter ? 'var(--accent)' : 'var(--text-secondary)',
                                        padding: '0.6rem 1.25rem',
                                        fontSize: '0.875rem',
                                        borderRadius: '12px',
                                        fontWeight: activeFilter === filter ? '600' : '400',
                                        transition: 'all 0.2s'
                                    }}
                                    onClick={() => setActiveFilter(filter)}
                                >
                                    {filter}
                                </button>
                            ))}
                            {/* Reverse Sort Button - Moved Input */}
                            <button
                                onClick={() => setReverseSort(!reverseSort)}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    padding: '0.6rem 1.25rem',
                                    background: reverseSort ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                                    border: reverseSort ? '1px solid var(--accent)' : '1px solid rgba(255, 255, 255, 0.1)',
                                    borderRadius: '12px',
                                    color: reverseSort ? 'var(--accent)' : 'var(--text-secondary)',
                                    fontSize: '0.875rem',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                                title="Inverser l'ordre"
                            >
                                <ArrowUpDown size={16} />
                                <span>Tri inversé</span>
                            </button>
                        </div>
                    )}
                </div>

                {/* History Section - Moved here */}
                <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginBottom: historyOpen ? '1rem' : '0' }}>
                        <button
                            onClick={() => setHistoryOpen(!historyOpen)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '0.75rem 1.25rem',
                                background: 'rgba(255, 255, 255, 0.05)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                borderRadius: '12px',
                                color: 'var(--text-primary)',
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                                width: '100%',
                                justifyContent: 'space-between'
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Info size={18} style={{ color: 'var(--accent)' }} />
                                <span>Historique des alertes</span>
                            </div>
                            <ChevronDown
                                size={16}
                                style={{
                                    color: 'var(--text-secondary)',
                                    transform: historyOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                                    transition: 'transform 0.2s'
                                }}
                            />
                        </button>
                    </div>

                    {historyOpen && (
                        <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '1rem',
                            animation: 'slideDown 0.2s ease',
                            marginTop: '0.5rem',
                            maxHeight: '300px',
                            overflowY: 'auto',
                            paddingRight: '0.5rem'
                        }}>
                            {alertHistory.map((item) => (
                                <div key={item.id} style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    padding: '1rem',
                                    background: 'rgba(255, 255, 255, 0.03)',
                                    borderRadius: '12px',
                                    border: '1px solid rgba(255, 255, 255, 0.05)',
                                    borderLeft: `4px solid ${item.success ? 'var(--success)' : 'var(--danger)'}`,
                                }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                                            <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>{item.symbol}</strong>
                                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.date}</span>
                                        </div>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                                            {item.action}
                                        </div>
                                    </div>
                                    <div style={{
                                        width: '32px',
                                        height: '32px',
                                        borderRadius: '50%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        background: item.success ? 'rgba(22, 199, 132, 0.1)' : 'rgba(239, 68, 68, 0.1)'
                                    }}>
                                        {item.success ? (
                                            <CheckCircle size={16} style={{ color: 'var(--success)' }} />
                                        ) : (
                                            <X size={16} style={{ color: 'var(--danger)' }} />
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Active Alerts */}
            <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
                <div className="card-title" style={{ marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Flux d'Alertes</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {sortedAlerts.length > 0 ? sortedAlerts.map((alert) => (
                        <div key={alert.id}>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                padding: '1.25rem',
                                background: 'rgba(255, 255, 255, 0.03)',
                                borderRadius: '16px',
                                border: '1px solid rgba(255, 255, 255, 0.05)',
                                borderLeft: `4px solid ${alert.severity === 'High' ? 'var(--danger)' : alert.severity === 'Medium' ? 'var(--warning)' : 'var(--accent)'}`,
                                transition: 'transform 0.2s ease, background 0.2s ease',
                            }}>
                                <div style={{ marginRight: '1.25rem' }}>
                                    {getStatusIcon(alert.status)}
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                        <strong style={{ fontSize: '1.125rem', color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>{alert.symbol}</strong>
                                        <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{alert.timestamp}</span>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            padding: '0.2rem 0.6rem',
                                            borderRadius: '6px',
                                            fontWeight: '600',
                                            background: alert.severity === 'High' ? 'rgba(239, 68, 68, 0.1)' : alert.severity === 'Medium' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(0, 212, 255, 0.1)',
                                            color: alert.severity === 'High' ? 'var(--danger)' : alert.severity === 'Medium' ? 'var(--warning)' : 'var(--accent)',
                                            border: '1px solid rgba(255, 255, 255, 0.05)'
                                        }}>
                                            {alert.severity.toUpperCase()}
                                        </span>
                                    </div>
                                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem' }}>
                                        <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{alert.type}:</span> Une anomalie a été détectée dans le flux de données en temps réel.
                                    </div>
                                </div>
                                <div>
                                    <button
                                        onClick={() => toggleAlertDetails(alert.id)}
                                        style={{
                                            padding: '0.6rem 1.25rem',
                                            border: '1px solid rgba(255, 255, 255, 0.1)',
                                            borderRadius: '10px',
                                            background: expandedAlerts.has(alert.id) ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                                            color: expandedAlerts.has(alert.id) ? 'var(--accent)' : 'var(--text-primary)',
                                            cursor: 'pointer',
                                            fontSize: '0.875rem',
                                            fontWeight: '600',
                                            transition: 'all 0.2s',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.5rem'
                                        }}
                                    >
                                        <Eye size={16} />
                                        {expandedAlerts.has(alert.id) ? 'Masquer' : 'Détails'}
                                    </button>
                                </div>
                            </div>

                            {/* Expanded Alert Details */}
                            {expandedAlerts.has(alert.id) && (
                                <div style={{
                                    marginTop: '0.5rem',
                                    padding: '1.5rem',
                                    background: 'rgba(0, 212, 255, 0.03)',
                                    borderRadius: '12px',
                                    border: '1px solid rgba(0, 212, 255, 0.1)',
                                    animation: 'slideDown 0.2s ease'
                                }}>
                                    <div className="grid-cols-3" style={{ gap: '1.5rem' }}>
                                        <div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Prix Actuel</div>
                                            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                                                {(Math.random() * 50 + 50).toFixed(2)} TND
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Variation 24h</div>
                                            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: Math.random() > 0.5 ? 'var(--success)' : 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                {Math.random() > 0.5 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                                                {(Math.random() * 10 - 5).toFixed(2)}%
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Volume</div>
                                            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                                                {(Math.random() * 50 + 10).toFixed(1)}K
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px' }}>
                                        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                                            <strong style={{ color: 'var(--accent)' }}>Analyse détaillée:</strong> L'algorithme a détecté une variation significative du volume de transactions accompagnée d'une divergence des indicateurs techniques (RSI, MACD). Cette combinaison suggère une opportunité potentielle ou un risque accru selon votre stratégie d'investissement.
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )) : (
                        <div style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-muted)' }}>
                            <Info size={32} style={{ marginBottom: '1rem', opacity: 0.3 }} />
                            <div style={{ fontSize: '1.125rem' }}>Aucune alerte trouvée pour ce filtre.</div>
                        </div>
                    )}
                </div>
            </div>


        </div>
    );
};

export default Alerts;
