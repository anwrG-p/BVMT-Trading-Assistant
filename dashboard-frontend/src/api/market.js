import client from './client';

export const getMarketOverview = async () => {
    const response = await client.get('/market/overview');
    return response.data;
};

export const getStockDetails = async (symbol) => {
    const response = await client.get(`/stock/${symbol}`);
    return response.data;
};
