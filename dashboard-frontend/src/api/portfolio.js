import client from './client';

export const getPortfolio = async () => {
    const response = await client.get('/portfolio');
    return response.data;
};
