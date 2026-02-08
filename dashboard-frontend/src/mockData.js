// Mock data for BVMT Dashboard

export const MARKET_DATA = {
    index: { name: "TUNINDEX", value: 8923.45, change: 0.82 },
    gainers: [
        { symbol: "SFBT", price: 13.50, change: 2.3 },
        { symbol: "BIAT", price: 92.10, change: 1.8 },
        { symbol: "SAH", price: 8.45, change: 1.5 },
        { symbol: "PGH", price: 11.20, change: 1.2 },
        { symbol: "SOTUVER", price: 12.80, change: 1.1 },
    ],
    losers: [
        { symbol: "CARTHAGE", price: 1.80, change: -3.2 },
        { symbol: "SERVICOM", price: 0.45, change: -2.8 },
        { symbol: "UADH", price: 0.35, change: -2.1 },
        { symbol: "GIF", price: 0.40, change: -1.9 },
        { symbol: "ELECTROSTAR", price: 0.30, change: -1.5 },
    ],
    sentiment: 0.72,
    recent_alerts: [
        { id: 1, symbol: "SFBT", type: "volume", description: "Unusual volume spike detected (+200%)", timestamp: "10:30" },
        { id: 2, symbol: "BIAT", type: "price", description: "Price broke resistance at 90.00", timestamp: "09:45" },
        { id: 3, symbol: "MARKET", type: "news", description: "Positive earnings reports from banking sector", timestamp: "09:00" },
    ]
};

export const STOCK_DATA = {
    symbol: "SFBT",
    name: "Société de Fabrication des Boissons de Tunisie",
    price_history: [
        { date: '2023-01', value: 12.5 },
        { date: '2023-02', value: 12.8 },
        { date: '2023-03', value: 12.6 },
        { date: '2023-04', value: 13.0 },
        { date: '2023-05', value: 13.2 },
        { date: '2023-06', value: 13.5 },
        // Forecast
        { date: '2023-07', value: 13.7, forecast: true },
        { date: '2023-08', value: 13.9, forecast: true },
        { date: '2023-09', value: 14.2, forecast: true },
    ],
    sentiment_timeline: [
        { date: '2023-01', score: 0.2 },
        { date: '2023-02', score: 0.4 },
        { date: '2023-03', score: 0.3 },
        { date: '2023-04', score: 0.6 },
        { date: '2023-05', score: 0.7 },
        { date: '2023-06', score: 0.8 },
    ],
    indicators: {
        rsi: 62,
        macd: "Bullish Crossover"
    },
    recommendation: {
        action: "ACHETER",
        confidence: 81
    }
};

export const PORTFOLIO_DATA = {
    capital: 10000,
    roi: 12.5,
    positions: [
        { symbol: "SFBT", quantity: 100, buyPrice: 12.00, currentPrice: 13.50, pl: 150 },
        { symbol: "BIAT", quantity: 10, buyPrice: 85.00, currentPrice: 92.10, pl: 71 },
        { symbol: "SAH", quantity: 200, buyPrice: 8.00, currentPrice: 8.45, pl: 90 },
    ],
    allocation: [
        { name: "Banks", value: 40 },
        { name: "Consumer Goods", value: 35 },
        { name: "Industry", value: 25 },
    ],
    performance: [
        { date: 'Jan', value: 10000 },
        { date: 'Feb', value: 10200 },
        { date: 'Mar', value: 10150 },
        { date: 'Apr', value: 10500 },
        { date: 'May', value: 10800 },
        { date: 'Jun', value: 11250 },
    ],
    suggestions: [
        "Consider taking profits on SFBT (RSI > 70)",
        "Diversify into Technology sector to reduce risk",
        "Set stop-loss for BIAT at 88.00"
    ]
};

export const ALERTS_DATA = {
    alerts: [
        { id: 1, symbol: "SFBT", type: "Volume", severity: "High", timestamp: "2023-10-25 10:30", status: "Open" },
        { id: 2, symbol: "BIAT", type: "Price", severity: "Medium", timestamp: "2023-10-25 09:45", status: "Resolved" },
        { id: 3, symbol: "SAH", type: "News", severity: "Low", timestamp: "2023-10-24 14:00", status: "Open" },
        { id: 4, symbol: "TUNINDEX", type: "Market", severity: "High", timestamp: "2023-10-24 12:00", status: "Resolved" },
    ],
    filters: ["Volume", "Price", "News", "Market"]
};
