import axios, { AxiosInstance } from 'axios';
import { generateMarketOverview } from '../mocks/market.mock';
import { generateStockAnalysis } from '../mocks/stock.mock';
import { generatePortfolio } from '../mocks/portfolio.mock';
import { generateAlerts } from '../mocks/alerts.mock';
import {
  MarketOverviewResponse,
  StockAnalysisResponse,
  PortfolioResponse,
  AlertsResponse
} from '../types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

const delay = (ms: number): Promise<void> => new Promise(resolve => setTimeout(resolve, ms));

const api = {
  /**
   * Get Market Overview
   */
  getMarketOverview: async (): Promise<MarketOverviewResponse> => {
    if (USE_MOCK) {
      await delay(400);
      return generateMarketOverview();
    }
    try {
      const response = await client.get<MarketOverviewResponse>('/market/overview');
      return response.data;
    } catch (error) {
      console.warn('API Error, falling back to mock:', error);
      return generateMarketOverview();
    }
  },

  /**
   * Get Stock Analysis
   */
  getStockAnalysis: async (symbol: string): Promise<StockAnalysisResponse> => {
    if (USE_MOCK) {
      await delay(400);
      return generateStockAnalysis(symbol);
    }
    try {
      const response = await client.get<StockAnalysisResponse>(`/stock/${symbol}`);
      return response.data;
    } catch (error) {
      console.warn('API Error, falling back to mock:', error);
      return generateStockAnalysis(symbol);
    }
  },

  /**
   * Get Portfolio
   */
  getPortfolio: async (): Promise<PortfolioResponse> => {
    if (USE_MOCK) {
      await delay(400);
      return generatePortfolio();
    }
    try {
      const response = await client.get<PortfolioResponse>('/portfolio');
      return response.data;
    } catch (error) {
      console.warn('API Error, falling back to mock:', error);
      return generatePortfolio();
    }
  },

  /**
   * Get Alerts
   */
  getAlerts: async (): Promise<AlertsResponse> => {
    if (USE_MOCK) {
      await delay(300);
      return generateAlerts();
    }
    try {
      const response = await client.get<AlertsResponse>('/alerts');
      return response.data;
    } catch (error) {
      console.warn('API Error, falling back to mock:', error);
      return generateAlerts();
    }
  }
};

export default api;
