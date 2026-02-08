import client from './client';
import { ALERTS_MOCK } from '../mock/alerts';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

const alertsService = {
    getAlerts: async () => {
        if (USE_MOCK) {
            console.warn('Mode Démo: Données simulées pour Alerts');
            return ALERTS_MOCK;
        }

        try {
            const response = await client.get('/alerts');
            return response.data;
        } catch (error) {
            console.error('API Error (Alerts):', error);
            console.warn('Mode Démo (Fallback): Utilisation des données simulées');
            return ALERTS_MOCK;
        }
    },
};

export default alertsService;
