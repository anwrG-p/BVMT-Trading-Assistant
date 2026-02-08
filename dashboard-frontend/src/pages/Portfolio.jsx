import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

const Portfolio = () => {
    const [portfolioData, setPortfolioData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPortfolio = async () => {
            try {
                const data = await api.getPortfolio();
                setPortfolioData(data);
            } catch (err) {
                console.error("Error fetching portfolio:", err);
                setError("Impossible de charger les données du portefeuille.");
            } finally {
                setLoading(false);
            }
        };

        fetchPortfolio();
    }, []);

    if (loading) return <div className="p-8 text-center" style={{ color: 'var(--secondary)' }}>Chargement du portefeuille...</div>;

    if (error) return (
        <div className="card text-danger" style={{ margin: '2rem', textAlign: 'center' }}>
            <div className="card-title">Erreur</div>
            <p>{error}</p>
        </div>
    );

    if (!portfolioData) return null;

    const {
        capital = 0,
        roi = 0,
        positions = [],
        allocation = [],
        performance = [],
        suggestions = []
    } = portfolioData;

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Mon Portefeuille</h1>
            </div>

            <div className="grid-cols-4" style={{ marginBottom: '1.5rem' }}>
                <div className="glass-card">
                    <div className="card-title">Capital Total</div>
                    <div className="stat-value">{capital.toLocaleString()} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>TND</span></div>
                </div>
                <div className="glass-card">
                    <div className="card-title">ROI Global</div>
                    <div className={`stat-value`} style={{ color: roi >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                        {roi > 0 ? '+' : ''}{roi}%
                    </div>
                </div>
                <div className="glass-card" style={{ gridColumn: 'span 2' }}>
                    <div className="card-title">Performance Globale</div>
                    <div style={{ height: '100px', width: '100%' }}>
                        <ResponsiveContainer>
                            <AreaChart data={performance}>
                                <defs>
                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--success)" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="var(--success)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <Area type="monotone" dataKey="value" stroke="var(--success)" fillOpacity={1} fill="url(#colorValue)" strokeWidth={2} />
                                <Tooltip contentStyle={{ background: 'rgba(26, 31, 46, 0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '12px' }} itemStyle={{ color: 'var(--text-primary)' }} labelStyle={{ color: 'var(--text-muted)' }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="grid-cols-2">
                {/* Positions Table */}
                <div className="glass-card" style={{ gridColumn: 'span 2' }}>
                    <div className="card-title">Positions Actuelles</div>
                    <div style={{ maxHeight: '400px', overflowY: 'auto', overflowX: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Quantité</th>
                                    <th>Prix Achat</th>
                                    <th>Prix Actuel</th>
                                    <th>P&L</th>
                                </tr>
                            </thead>
                            <tbody>
                                {positions.map((pos) => (
                                    <tr key={pos.symbol}>
                                        <td><strong style={{ color: 'var(--accent)' }}>{pos.symbol}</strong></td>
                                        <td>{pos.quantity}</td>
                                        <td>{pos.buyPrice.toFixed(2)}</td>
                                        <td>{pos.currentPrice.toFixed(2)}</td>
                                        <td style={{ fontWeight: 'bold', color: pos.pl >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                                            {pos.pl >= 0 ? '+' : ''}{pos.pl} TND
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Allocation Pie Chart */}
                <div className="glass-card">
                    <div className="card-title">Répartition par Secteur</div>
                    <div style={{ height: '250px', width: '100%' }}>
                        <ResponsiveContainer>
                            <PieChart>
                                <Pie
                                    data={allocation}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    paddingAngle={5}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    {allocation.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ background: 'rgba(26, 31, 46, 0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '12px' }} itemStyle={{ color: 'var(--text-primary)' }} />
                                <Legend wrapperStyle={{ color: 'var(--text-secondary)' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Optimization Suggestions */}
                <div className="glass-card">
                    <div className="card-title">Conseils d'Optimisation</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto', paddingRight: '0.5rem' }}>
                        {suggestions.map((suggestion, index) => (
                            <div key={index} style={{
                                padding: '1rem',
                                background: 'rgba(0, 212, 255, 0.05)',
                                borderLeft: '4px solid var(--accent)',
                                borderRadius: '8px',
                                fontSize: '0.925rem',
                                color: 'var(--text-primary)',
                                border: '1px solid rgba(0, 212, 255, 0.1)',
                                borderLeftWidth: '4px'
                            }}>
                                <div style={{ fontWeight: '600', marginBottom: '0.25rem', color: 'var(--accent)' }}>Conseil #{index + 1}</div>
                                {suggestion}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Portfolio;
