import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { TrendingUp, TrendingDown, Activity, AlertTriangle, ArrowUpRight, ArrowDownRight, Bell, AlertCircle, Info } from 'lucide-react';

const MarketOverview = () => {
    const [marketData, setMarketData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchMarket = async () => {
            try {
                const data = await api.getMarketOverview();
                setMarketData(data);
            } catch (err) {
                console.error("Error fetching market data:", err);
                setError("Impossible de charger les données du marché.");
            } finally {
                setLoading(false);
            }
        };

        fetchMarket();
    }, []);

    if (loading) return <div className="p-8 text-center text-muted">Chargement du marché...</div>;
    if (error) return <div className="p-8 text-center text-danger">{error}</div>;
    if (!marketData) return null;

    const { index, gainers, losers, marketVolume, activeTraders } = marketData;
    const sentiment = 0.65; // Mock sentiment
    const sentimentWidth = `${sentiment * 100}%`;

    const dummyAlerts = [
        { id: 1, type: 'danger', symbol: 'BIAT', message: 'Anomalie de volume détectée (+300% vs moyenne)', time: 'Il y a 5 min', icon: AlertTriangle },
        { id: 2, type: 'warning', symbol: 'SAH', message: 'Cassure de support technique (11.200 TND)', time: 'Il y a 12 min', icon: AlertCircle },
        { id: 3, type: 'info', symbol: 'SFBT', message: 'Ordre institutionnel important détecté', time: 'Il y a 25 min', icon: Info },
    ];

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <h1 className="page-title">Vue d'Ensemble</h1>
                <span className="text-muted" style={{ fontSize: '0.8rem' }}>Dernière mise à jour: {new Date().toLocaleTimeString()}</span>
            </div>

            {/* KPI Grid */}
            <div className="grid-cols-4" style={{ marginBottom: '1.5rem' }}>
                {/* TUNINDEX */}
                <div className="glass-card">
                    <div className="card-title">TUNINDEX</div>
                    <div className="flex items-center gap-2">
                        <span className="stat-value">{index.value.toLocaleString()}</span>
                    </div>
                    <div className={`stat-change ${index.change >= 0 ? 'text-success' : 'text-danger'}`} style={{ display: 'flex', alignItems: 'center', marginTop: '0.5rem', fontSize: '0.9rem' }}>
                        {index.change >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                        <span style={{ fontWeight: 600 }}>{index.change}%</span>
                        <span style={{ marginLeft: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>vs veille</span>
                    </div>
                </div>

                {/* Sentiment */}
                <div className="glass-card" style={{ gridColumn: 'span 2' }}>
                    <div className="card-title">Sentiment du Marché</div>
                    <div className="flex justify-between items-end mb-2">
                        <span className="text-2xl font-bold" style={{ color: 'var(--success)' }}>Bullish</span>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Score: {(sentiment * 100).toFixed(0)}/100</span>
                    </div>
                    <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: sentimentWidth, height: '100%', background: 'linear-gradient(90deg, var(--danger) 0%, var(--warning) 50%, var(--success) 100%)' }}></div>
                    </div>
                    <div className="flex justify-between mt-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                        <span>Bearish</span>
                        <span>Neutral</span>
                        <span>Bullish</span>
                    </div>
                </div>

                {/* Volume */}
                <div className="glass-card">
                    <div className="card-title">Volume (TND)</div>
                    <div className="stat-value">{(marketVolume / 1000000).toFixed(2)}M</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                        <span style={{ color: 'var(--success)' }}>+12%</span> vs moyenne 30j
                    </div>
                </div>
            </div>

            {/* Lists Grid */}
            <div className="grid-cols-2">
                {/* Gainers */}
                <div className="glass-card">
                    <div className="flex justify-between items-center mb-4">
                        <div className="card-title mb-0">Top Performance</div>
                        <TrendingUp size={16} style={{ color: 'var(--success)' }} />
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Symbole</th>
                                <th className="text-right">Prix</th>
                                <th className="text-right">% Var</th>
                            </tr>
                        </thead>
                        <tbody>
                            {gainers.map((stock) => (
                                <tr key={stock.symbol}>
                                    <td className="font-semibold" style={{ color: 'var(--accent)' }}>{stock.symbol}</td>
                                    <td className="text-right">{stock.price.toFixed(2)}</td>
                                    <td className="text-right" style={{ color: 'var(--success)' }}>+{stock.changePercent.toFixed(2)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Losers */}
                <div className="glass-card">
                    <div className="flex justify-between items-center mb-4">
                        <div className="card-title mb-0">Moins Performants</div>
                        <TrendingDown size={16} style={{ color: 'var(--danger)' }} />
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Symbole</th>
                                <th className="text-right">Prix</th>
                                <th className="text-right">% Var</th>
                            </tr>
                        </thead>
                        <tbody>
                            {losers.map((stock) => (
                                <tr key={stock.symbol}>
                                    <td className="font-semibold" style={{ color: 'var(--accent)' }}>{stock.symbol}</td>
                                    <td className="text-right">{stock.price.toFixed(2)}</td>
                                    <td className="text-right" style={{ color: 'var(--danger)' }}>{stock.changePercent.toFixed(2)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Recent Alerts */}
            <div className="glass-card mt-4">
                <div className="flex justify-between items-center mb-4">
                    <div className="card-title mb-0">Alertes récentes (anomalies détectées)</div>
                    <Bell size={16} style={{ color: 'var(--accent)' }} />
                </div>
                <div className="space-y-4">
                    {dummyAlerts.map((alert) => (
                        <div key={alert.id} className="flex items-start gap-4 p-3 rounded" style={{ background: 'rgba(255, 255, 255, 0.02)', borderLeft: `4px solid var(--${alert.type})` }}>
                            <div className={`mt-1 text-${alert.type}`}>
                                <alert.icon size={18} />
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start">
                                    <span className="font-semibold text-accent">{alert.symbol}</span>
                                    <span className="text-xs text-muted">{alert.time}</span>
                                </div>
                                <p className="text-sm mt-1 mb-0" style={{ color: 'var(--text-secondary)' }}>{alert.message}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default MarketOverview;
