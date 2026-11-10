import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Search, ChevronDown, ArrowUpDown, TrendingUp, TrendingDown } from 'lucide-react';
import { PricePoint, Recommendation, TechnicalIndicators } from '../types';

interface StockSummary {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  volume: string;
}

const DEFAULT_STOCKS: StockSummary[] = [
  { symbol: 'BIAT', name: 'Banque Internationale Arabe de Tunisie', currentPrice: 94.50, change: 2.45, volume: '18.4K' },
  { symbol: 'SFBT', name: 'Société Frigorifique et Brasserie de Tunis', currentPrice: 11.90, change: 1.30, volume: '32.1K' },
  { symbol: 'ATTIJARI BANK', name: 'Attijari Bank Tunisie', currentPrice: 52.10, change: 1.85, volume: '14.2K' },
  { symbol: 'SAH', name: 'SAH Lilas', currentPrice: 8.40, change: 0.96, volume: '45.8K' },
  { symbol: 'BT', name: 'Banque de Tunisie', currentPrice: 5.15, change: 0.78, volume: '22.0K' },
  { symbol: 'UIB', name: 'Union Internationale de Banques', currentPrice: 24.20, change: -1.82, volume: '8.5K' },
];

const StockAnalysis: React.FC = () => {
  const [stocks] = useState<StockSummary[]>(DEFAULT_STOCKS);
  const [selectedStock, setSelectedStock] = useState<StockSummary>(DEFAULT_STOCKS[0]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortBy, setSortBy] = useState<'name' | 'performance'>('performance');
  const [sortReverse, setSortReverse] = useState<boolean>(false);
  const [dropdownOpen, setDropdownOpen] = useState<boolean>(false);
  const [chartData, setChartData] = useState<PricePoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [recommendation, setRecommendation] = useState<Recommendation>({ action: 'ACHETER', confidence: 82 });
  const [indicators, setIndicators] = useState<TechnicalIndicators>({ rsi: 58, macd: 'Bullish Crossover' });

  // Fetch stock analysis data from API
  useEffect(() => {
    const fetchStockData = async () => {
      setLoading(true);
      try {
        const data = await api.getStockAnalysis(selectedStock.symbol);
        if (data && data.price_history && data.price_history.length > 0) {
          setChartData(data.price_history);
          if (data.recommendation) setRecommendation(data.recommendation);
          if (data.indicators) setIndicators(data.indicators);
        }
      } catch (err) {
        console.error("Error fetching stock analysis:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStockData();
  }, [selectedStock.symbol]);

  const handleStockSelect = (stock: StockSummary) => {
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

  const CustomTooltip = ({ active, payload, label }: any) => {
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
            {label} {isForecast && <span style={{ color: 'var(--warning)' }}>(Prévision IA)</span>}
          </p>
          <p style={{ color: 'var(--text-primary)', fontSize: '14px', fontWeight: 'bold', margin: 0 }}>
            {Number(payload[0].value).toFixed(2)} TND
          </p>
        </div>
      );
    }
    return null;
  };

  const historicalData = chartData.filter(d => !d.forecast);
  const forecastData = chartData.filter(d => d.forecast);
  const forecastDataWithTransition = historicalData.length > 0 && forecastData.length > 0
    ? [historicalData[historicalData.length - 1], ...forecastData]
    : forecastData;

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
            <span>Sélectionner une valeur</span>
            <ChevronDown size={16} style={{ color: 'var(--text-secondary)' }} />
          </button>

          {dropdownOpen && (
            <div className="stock-selector-dropdown">
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
          <div className="card-title">Graphique Prix Historique + Prévisions XGBoost 5 jours</div>
          <div style={{ flex: 1, marginTop: '1rem' }}>
            {loading ? (
              <div className="p-8 text-center text-muted">Chargement des données...</div>
            ) : (
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
                  <Line
                    data={historicalData}
                    type="monotone"
                    dataKey="value"
                    stroke="var(--accent)"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 0, fill: 'var(--accent)' }}
                    name="Historique (Clôture)"
                  />
                  <Line
                    data={forecastDataWithTransition}
                    type="monotone"
                    dataKey="value"
                    stroke="var(--warning)"
                    strokeWidth={3}
                    strokeDasharray="5 5"
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 0, fill: 'var(--warning)' }}
                    name="Prévision Modèle"
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Signal AI and Technique */}
      <div className="grid-cols-2" style={{ marginBottom: '1.5rem' }}>
        <div className="glass-card">
          <div className="card-title">Signal Prédictif IA</div>
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
            <div className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>Indice de Confiance: {recommendation.confidence}%</div>
          </div>
        </div>

        <div className="glass-card flex-1">
          <div className="card-title">Indicateurs Techniques</div>
          <div className="space-y-4" style={{ marginTop: '1rem' }}>
            <div className="flex justify-between items-center">
              <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>RSI (14)</span>
              <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{indicators.rsi}</span>
            </div>
            <div style={{ width: '100%', height: '4px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, Math.max(0, indicators.rsi))}%`, height: '100%', background: 'var(--accent)' }}></div>
            </div>

            <div className="flex justify-between items-center mt-6">
              <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>MACD</span>
              <span className="font-mono" style={{ color: 'var(--accent)' }}>{indicators.macd}</span>
            </div>

            <div className="flex justify-between items-center mt-6">
              <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Volume Quotidien</span>
              <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{selectedStock.volume}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockAnalysis;
