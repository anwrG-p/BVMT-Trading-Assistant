// Type definitions for BVMT Trading Assistant Frontend

export interface IndexData {
  name: string;
  value: number;
  change: number;
}

export interface StockTicker {
  symbol: string;
  price: number;
  change: number;
}

export interface MarketAlert {
  id: number;
  symbol: string;
  type: 'volume' | 'price' | 'news' | 'market';
  description: string;
  timestamp: string;
}

export interface MarketOverviewResponse {
  index: IndexData;
  gainers: StockTicker[];
  losers: StockTicker[];
  sentiment: number;
  recent_alerts: MarketAlert[];
  marketVolume?: number;
  activeTraders?: number;
}

export interface PricePoint {
  date: string;
  value: number;
  forecast?: boolean;
}

export interface SentimentPoint {
  date: string;
  score: number;
}

export interface TechnicalIndicators {
  rsi: number;
  macd: string;
}

export interface Recommendation {
  action: 'ACHETER' | 'VENDRE' | 'CONSERVER';
  confidence: number;
}

export interface StockAnalysisResponse {
  symbol: string;
  name: string;
  price_history: PricePoint[];
  sentiment_timeline: SentimentPoint[];
  indicators: TechnicalIndicators;
  recommendation: Recommendation;
}

export interface Position {
  symbol: string;
  quantity: number;
  buyPrice: number;
  currentPrice: number;
  pl: number;
}

export interface AllocationItem {
  name: string;
  value: number;
}

export interface PerformancePoint {
  date: string;
  value: number;
}

export interface PortfolioResponse {
  capital: number;
  roi: number;
  positions: Position[];
  allocation: AllocationItem[];
  performance: PerformancePoint[];
  suggestions: string[];
}

export interface AlertDetail {
  id: number;
  symbol: string;
  type: string;
  severity: 'High' | 'Medium' | 'Low';
  timestamp: string;
  status: 'Open' | 'Resolved';
  message?: string;
  description?: string;
}

export interface AlertsResponse {
  alerts: AlertDetail[];
  filters: string[];
}

export interface User {
  id?: string;
  name?: string;
  email: string;
  role?: string;
}
