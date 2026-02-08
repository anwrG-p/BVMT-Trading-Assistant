import client from './client';
import { PORTFOLIO_MOCK } from '../mock/portfolio';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

const portfolioService = {
    getPortfolio: async () => {
        if (USE_MOCK) {
            console.warn('Mode Démo: Données simulées pour Portfolio');
            return PORTFOLIO_MOCK;
        }

        try {
            const response = await client.get('/portfolio');
            return response.data;
        } catch (error) {
            console.error('API Error (Portfolio):', error);
            console.warn('Mode Démo (Fallback): Utilisation des données simulées');
            return PORTFOLIO_MOCK;
        }
    },
};

export default portfolioService;
