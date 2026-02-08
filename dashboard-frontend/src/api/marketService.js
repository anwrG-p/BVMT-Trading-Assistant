import client from './client';
import { MARKET_OVERVIEW_MOCK } from '../mock/marketOverview';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

const marketService = {
    getMarketOverview: async () => {
        if (USE_MOCK) {
            console.warn('Mode Démo: Utilisation des données simulées pour Market Overview');
            return MARKET_OVERVIEW_MOCK;
        }

        try {
            const response = await client.get('/market/overview');
            return response.data;
        } catch (error) {
            console.error('API Error (Market):', error);
            console.warn('Mode Démo (Fallback): Utilisation des données simulées');
            return MARKET_OVERVIEW_MOCK;
        }
    },
};

export default marketService;
