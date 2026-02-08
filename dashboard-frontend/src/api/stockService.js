import client from './client';
import { STOCK_ANALYSIS_MOCK_SFBT, STOCK_ANALYSIS_MOCK_BIAT } from '../mock/stockAnalysis';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

const stockService = {
    getStockAnalysis: async (symbol) => {
        if (!symbol) throw new Error('Symbol is required');

        if (USE_MOCK) {
            console.warn(`Mode Démo: Données simulées pour ${symbol}`);
            return symbol === 'BIAT' ? STOCK_ANALYSIS_MOCK_BIAT : STOCK_ANALYSIS_MOCK_SFBT;
        }

        try {
            const response = await client.get(`/stock/${symbol}`);
            return response.data;
        } catch (error) {
            console.error(`API Error (Stock ${symbol}):`, error);
            console.warn('Mode Démo (Fallback): Utilisation des données simulées');
            return symbol === 'BIAT' ? STOCK_ANALYSIS_MOCK_BIAT : STOCK_ANALYSIS_MOCK_SFBT;
        }
    },
};

export default stockService;
