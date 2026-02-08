/** @type {import('../api/contracts/market').StockAnalysisResponse} */
export const STOCK_ANALYSIS_MOCK_SFBT = {
    symbol: "SFBT",
    name: "Société de Fabrication des Boissons de Tunisie",
    price_history: [
        { date: '2023-01', value: 12.5 },
        { date: '2023-02', value: 12.8 },
        { date: '2023-03', value: 12.6 },
        { date: '2023-04', value: 13.0 },
        { date: '2023-05', value: 13.2 },
        { date: '2023-06', value: 13.5 },
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
        rsi: 65,
        macd: "Croisement Haussier"
    },
    recommendation: {
        action: "ACHETER",
        confidence: 85
    }
};

export const STOCK_ANALYSIS_MOCK_BIAT = {
    symbol: "BIAT",
    name: "Banque Internationale Arabe de Tunisie",
    price_history: [
        { date: '2023-01', value: 85.0 },
        { date: '2023-02', value: 87.5 },
        { date: '2023-03', value: 86.0 },
        { date: '2023-04', value: 89.0 },
        { date: '2023-05', value: 91.0 },
        { date: '2023-06', value: 92.0 },
        { date: '2023-07', value: 93.5, forecast: true },
        { date: '2023-08', value: 95.0, forecast: true },
    ],
    sentiment_timeline: [
        { date: '2023-01', score: 0.5 },
        { date: '2023-02', score: 0.55 },
        { date: '2023-03', score: 0.6 },
        { date: '2023-04', score: 0.65 },
        { date: '2023-05', score: 0.7 },
    ],
    indicators: {
        rsi: 58,
        macd: "Neutre"
    },
    recommendation: {
        action: "CONSERVER",
        confidence: 60
    }
};
