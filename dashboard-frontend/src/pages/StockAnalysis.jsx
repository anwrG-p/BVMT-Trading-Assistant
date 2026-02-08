import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Search, ChevronDown, ArrowUpDown, TrendingUp, TrendingDown } from 'lucide-react';

// Mock stock data
const MOCK_STOCKS = [
    { symbol: 'BIAT', name: 'Banque Internationale Arabe de Tunisie', currentPrice: 125.50, change: 3.2, volume: '15.2K' },
    { symbol: 'SAH', name: 'SIMPAR Holding', currentPrice: 11.80, change: -1.5, volume: '8.7K' },
    { symbol: 'SFBT', name: 'Société Franco-Tunisienne de Banques', currentPrice: 12.45, change: 2.8, volume: '12.5K' },
    { symbol: 'ATB', name: 'Arab Tunisian Bank', currentPrice: 4.25, change: 1.2, volume: '22.1K' },
    { symbol: 'BNA', name: 'Banque Nationale Agricole', currentPrice: 8.90, change: -0.8, volume: '9.5K' },
    { symbol: 'TELE', name: 'Télénet', currentPrice: 3.15, change: 4.5, volume: '31.2K' },
    { symbol: 'STB', name: 'Société Tunisienne de Banque', currentPrice: 6.75, change: 0.5, volume: '11.3K' },
];

// Generate mock historical + prediction data
const generateMockData = (basePrice) => {
    const data = [];
    const today = new Date();

    // Historical data (30 days)
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const variance = (Math.random() - 0.5) * 2;
        const price = basePrice + variance;
        data.push({
            date: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
            value: parseFloat(price.toFixed(2)),
            forecast: false
        });
    }

    // Prediction data (5 days)
    const lastPrice = data[data.length - 1].value;
    const trend = Math.random() > 0.5 ? 1 : -1;
    for (let i = 1; i <= 5; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        const variance = (Math.random() * 0.5 * trend);
        const price = lastPrice + (variance * i * 0.3);
        data.push({
            date: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
            value: parseFloat(price.toFixed(2)),
            forecast: true
        });
    }

    return data;
};

const StockAnalysis = () => {
    const [stocks] = useState(MOCK_STOCKS);
    const [selectedStock, setSelectedStock] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('performance'); // 'name' or 'performance'
    const [sortReverse, setSortReverse] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(true);

    // Initialize with best performing stock
    useEffect(() => {
        const sorted = [...stocks].sort((a, b) => b.change - a.change);
        const bestStock = sorted[0];
        setSelectedStock(bestStock);
        setChartData(generateMockData(bestStock.currentPrice));
        setLoading(false);
    }, []);

    // Update chart when stock changes
    useEffect(() => {
        if (selectedStock) {
            setChartData(generateMockData(selectedStock.currentPrice));
        }
    }, [selectedStock]);

    const handleStockSelect = (stock) => {
        setSelectedStock(stock);
        setDropdownOpen(false);
        setSearchTerm('');
    };

    const filteredAndSortedStocks = () => {
        let filtered = stocks.filter(stock =>
            stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
            stock.name.toLowerCase().includes(searchTerm.toLowerCase())
        );

        filtered.sort((a, b) => {
            if (sortBy === 'name') {
                return sortReverse
                    ? b.symbol.localeCompare(a.symbol)
                    : a.symbol.localeCompare(b.symbol);
            } else {
                return sortReverse
                    ? a.change - b.change
                    : b.change - a.change;
            }
        });

        return filtered;
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const isForecast = payload[0].payload.forecast;
            return (
                <div style={{
                    background: 'var(--bg-panel)',
                    padding: '12px 16px',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
                }}>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '11px', marginBottom: '4px' }}>
                        {label} {isForecast && <span style={{ color: 'var(--warning)' }}>(Prévision)</span>}
                    </p>
                    <p style={{ color: 'var(--text-primary)', fontSize: '14px', fontWeight: 'bold', margin: 0 }}>
                        {payload[0].value.toFixed(2)} TND
                    </p>
                </div>
            );
        }
        return null;
    };

    if (loading || !selectedStock) {
        return <div className="p-8 text-center text-muted">Chargement...</div>;
    }

    const historicalData = chartData.filter(d => !d.forecast);
    const forecastData = chartData.filter(d => d.forecast);
    // Combine with last historical point for smooth transition
    const forecastDataWithTransition = [historicalData[historicalData.length - 1], ...forecastData];

    const recommendation = {
        action: selectedStock.change > 2 ? 'ACHETER' : selectedStock.change < -1 ? 'VENDRE' : 'CONSERVER',
        confidence: Math.floor(Math.random() * 30) + 70
    };

    const indicators = {
        rsi: Math.floor(Math.random() * 40) + 40,
        macd: (Math.random() * 4 - 2).toFixed(2)
    };

    return (
        <div>
            {/* Header with Stock Selector */}
            <div className="flex justify-between items-start mb-6">
                <div className="flex-1">
                    <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                        {selectedStock.name} <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>({selectedStock.symbol})</span>
                    </h1>
                    <div className="flex items-center gap-3 mt-2">
                        <div className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                            {selectedStock.currentPrice.toFixed(2)}
                            <span className="text-sm font-normal" style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>TND</span>
                        </div>
                        <div className={`flex items-center gap-1 ${selectedStock.change >= 0 ? 'text-success' : 'text-danger'}`}>
                            {selectedStock.change >= 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                            <span className="font-semibold">{selectedStock.change >= 0 ? '+' : ''}{selectedStock.change.toFixed(2)}%</span>
                        </div>
                    </div>
                </div>

                {/* Advanced Stock Selector */}
                <div style={{ position: 'relative', minWidth: '320px' }}>
                    <button
                        className="stock-selector-btn"
                        onClick={() => setDropdownOpen(!dropdownOpen)}
                    >
                        <Search size={16} style={{ color: 'var(--text-secondary)' }} />
                        <span>Changer d'action</span>
                        <ChevronDown size={16} style={{ color: 'var(--text-secondary)' }} />
                    </button>

                    {dropdownOpen && (
                        <div className="stock-selector-dropdown">
                            {/* Search Input */}
                            <div style={{ padding: '1rem 2.75rem 1rem 0.75rem', borderBottom: '1px solid var(--border)' }}>
                                <input
                                    type="text"
                                    placeholder="Rechercher une action..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="stock-search-input"
                                    autoFocus
                                />
                            </div>

                            {/* Filter Controls */}
                            <div style={{
                                padding: '0.75rem',
                                borderBottom: '1px solid var(--border)',
                                display: 'flex',
                                gap: '0.5rem',
                                alignItems: 'center'
                            }}>
                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Trier par:</span>
                                <button
                                    className={`filter-btn ${sortBy === 'name' ? 'active' : ''}`}
                                    onClick={() => setSortBy('name')}
                                >
                                    Nom
                                </button>
                                <button
                                    className={`filter-btn ${sortBy === 'performance' ? 'active' : ''}`}
                                    onClick={() => setSortBy('performance')}
                                >
                                    Performance
                                </button>
                                <button
                                    className="filter-btn icon-only"
                                    onClick={() => setSortReverse(!sortReverse)}
                                    title="Inverser l'ordre"
                                >
                                    <ArrowUpDown size={14} />
                                </button>
                            </div>

                            {/* Stock List */}
                            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                                {filteredAndSortedStocks().map((stock) => (
                                    <button
                                        key={stock.symbol}
                                        className={`stock-item ${selectedStock.symbol === stock.symbol ? 'active' : ''}`}
                                        onClick={() => handleStockSelect(stock)}
                                    >
                                        <div>
                                            <div className="font-semibold" style={{ color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                                                {stock.symbol}
                                            </div>
                                            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                                                {stock.name.length > 30 ? stock.name.substring(0, 30) + '...' : stock.name}
                                            </div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ color: 'var(--text-primary)', fontSize: '0.875rem', fontWeight: 600 }}>
                                                {stock.currentPrice.toFixed(2)}
                                            </div>
                                            <div className={stock.change >= 0 ? 'text-success' : 'text-danger'} style={{ fontSize: '0.75rem' }}>
                                                {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}%
                                            </div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="grid-cols-4" style={{ marginBottom: '1.5rem' }}>
                {/* Chart - Full Width */}
                <div className="glass-card" style={{ gridColumn: 'span 4', height: '450px', display: 'flex', flexDirection: 'column', marginTop: '1rem' }}>
                    <div className="card-title">Graphique Prix Historique + Prévisions 5 jours</div>
                    <div style={{ flex: 1, marginTop: '1rem' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart>
                                <CartesianGrid stroke="rgba(255, 255, 255, 0.05)" strokeDasharray="3 3" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    tick={{ fill: 'var(--text-secondary)', fontSize: 10 }}
                                    axisLine={false}
                                    tickLine={false}
                                    allowDuplicatedCategory={false}
                                />
                                <YAxis
                                    domain={['auto', 'auto']}
                                    orientation="right"
                                    tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255, 255, 255, 0.1)' }} />
                                <Legend
                                    wrapperStyle={{ paddingTop: '20px' }}
                                    iconType="line"
                                />
                                {/* Historical Data */}
                                <Line
                                    data={historicalData}
                                    type="monotone"
                                    dataKey="value"
                                    stroke="var(--accent)"
                                    strokeWidth={3}
                                    dot={false}
                                    activeDot={{ r: 4, strokeWidth: 0, fill: 'var(--accent)' }}
                                    name="Historique"
                                />
                                {/* Forecast Data */}
                                <Line
                                    data={forecastDataWithTransition}
                                    type="monotone"
                                    dataKey="value"
                                    stroke="var(--warning)"
                                    strokeWidth={3}
                                    strokeDasharray="5 5"
                                    dot={false}
                                    activeDot={{ r: 4, strokeWidth: 0, fill: 'var(--warning)' }}
                                    name="Prévision"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Signal AI and Technique - Side by Side Below Chart */}
            <div className="grid-cols-2" style={{ marginBottom: '1.5rem' }}>
                {/* Recommendation */}
                <div className="glass-card">
                    <div className="card-title">Signal AI</div>
                    <div style={{
                        textAlign: 'center',
                        padding: '1.5rem 1rem',
                        background: recommendation.action === 'ACHETER' ? 'rgba(22, 199, 132, 0.1)' : recommendation.action === 'VENDRE' ? 'rgba(234, 57, 67, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                        borderRadius: '16px',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        marginTop: '0.5rem'
                    }}>
                        <div className="text-xl font-bold" style={{ color: `var(--${recommendation.action === 'ACHETER' ? 'success' : recommendation.action === 'VENDRE' ? 'danger' : 'warning'})` }}>
                            {recommendation.action}
                        </div>
                        <div className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>Confiance: {recommendation.confidence}%</div>
                    </div>
                </div>

                {/* Technicals */}
                <div className="glass-card flex-1">
                    <div className="card-title">Technique</div>
                    <div className="space-y-4" style={{ marginTop: '1rem' }}>
                        <div className="flex justify-between items-center">
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>RSI (14)</span>
                            <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{indicators.rsi}</span>
                        </div>
                        <div style={{ width: '100%', height: '4px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                            <div style={{ width: `${indicators.rsi}%`, height: '100%', background: 'var(--accent)' }}></div>
                        </div>

                        <div className="flex justify-between items-center mt-6">
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>MACD</span>
                            <span className="font-mono" style={{ color: indicators.macd > 0 ? 'var(--success)' : 'var(--danger)' }}>{indicators.macd}</span>
                        </div>

                        <div className="flex justify-between items-center mt-6">
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Volume</span>
                            <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{selectedStock.volume}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StockAnalysis;
