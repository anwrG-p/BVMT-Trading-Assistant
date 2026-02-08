import { generateMarketOverview } from '../mocks/market.mock';
import { generateStockAnalysis } from '../mocks/stock.mock';
import { generatePortfolio } from '../mocks/portfolio.mock';
import { generateAlerts } from '../mocks/alerts.mock';
import axios from 'axios';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

/**
 * Simulates network delay
 * @param {number} ms 
 * @returns {Promise<void>}
 */
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const api = {
    /**
     * Get Market Overview
     * @returns {Promise<import('../mocks/market.mock').MarketOverview>}
     */
    getMarketOverview: async () => {
        if (USE_MOCK) {
            await delay(500);
            return generateMarketOverview();
        }
        try {
            const response = await client.get('/market/overview');
            return response.data;
        } catch (error) {
            console.warn("API Error, falling back to mock:", error);
            return generateMarketOverview();
        }
    },

    /**
     * Get Stock Analysis
     * @param {string} symbol 
     * @returns {Promise<import('../mocks/stock.mock').StockAnalysis>}
     */
    getStockAnalysis: async (symbol) => {
        if (USE_MOCK) {
            await delay(600);
            return generateStockAnalysis(symbol);
        }
        try {
            const response = await client.get(`/stock/${symbol}`);
            return response.data;
        } catch (error) {
            console.warn("API Error, falling back to mock:", error);
            return generateStockAnalysis(symbol);
        }
    },

    /**
     * Get Portfolio
     * @returns {Promise<import('../mocks/portfolio.mock').Portfolio>}
     */
    getPortfolio: async () => {
        if (USE_MOCK) {
            await delay(400);
            return generatePortfolio();
        }
        try {
            const response = await client.get('/portfolio');
            return response.data;
        } catch (error) {
            console.warn("API Error, falling back to mock:", error);
            return generatePortfolio();
        }
    },

    /**
     * Get Alerts
     * @returns {Promise<import('../mocks/alerts.mock').AlertsResponse>}
     */
    getAlerts: async () => {
        if (USE_MOCK) {
            await delay(300);
            return generateAlerts();
        }
        try {
            const response = await client.get('/alerts');
            return response.data;
        } catch (error) {
            console.warn("API Error, falling back to mock:", error);
            return generateAlerts();
        }
    }
};

export default api;
