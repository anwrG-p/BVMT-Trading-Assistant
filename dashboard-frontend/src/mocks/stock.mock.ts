import { StockAnalysisResponse } from '../types';

const random = (min: number, max: number): number => Math.random() * (max - min) + min;

export const generateStockAnalysis = (symbol: string): StockAnalysisResponse => {
  const basePrice = symbol === "BIAT" ? 94.5 : symbol === "SFBT" ? 11.9 : 25.0;
  const priceHistory = [];
  const today = new Date();

  // 30 days of history
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const variance = (Math.random() - 0.48) * 1.5;
    priceHistory.push({
      date: d.toISOString().split('T')[0],
      value: Number((basePrice + variance).toFixed(2)),
      forecast: false
    });
  }

  // 5 days of forecast
  const lastPrice = priceHistory[priceHistory.length - 1].value;
  for (let i = 1; i <= 5; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() + i);
    priceHistory.push({
      date: d.toISOString().split('T')[0],
      value: Number((lastPrice * (1 + 0.003 * i + random(-0.005, 0.005))).toFixed(2)),
      forecast: true
    });
  }

  const rsi = Math.floor(random(42, 68));
  const action = rsi < 45 ? 'ACHETER' : rsi > 65 ? 'VENDRE' : 'CONSERVER';

  return {
    symbol,
    name: `${symbol} - Bourse de Tunis`,
    price_history: priceHistory,
    sentiment_timeline: [
      { date: priceHistory[priceHistory.length - 10].date, score: 0.65 },
      { date: priceHistory[priceHistory.length - 5].date, score: 0.72 },
      { date: priceHistory[priceHistory.length - 1].date, score: 0.68 }
    ],
    indicators: {
      rsi,
      macd: rsi > 55 ? "Croisement Haussier (MACD > Signal)" : "Convergence Neutre"
    },
    recommendation: {
      action,
      confidence: Math.floor(random(72, 89))
    }
  };
};
