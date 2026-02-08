/** @type {import('../api/contracts/portfolio').PortfolioResponse} */
export const PORTFOLIO_MOCK = {
    capital: 12500,
    roi: 15.2,
    positions: [
        { symbol: "SFBT", quantity: 150, buyPrice: 12.00, currentPrice: 13.80, pl: 270 },
        { symbol: "BIAT", quantity: 20, buyPrice: 85.00, currentPrice: 92.50, pl: 150 },
        { symbol: "SAH", quantity: 300, buyPrice: 8.00, currentPrice: 8.60, pl: 180 },
    ],
    allocation: [
        { name: "Banques", value: 45 },
        { name: "Biens de Conso.", value: 35 },
        { name: "Industrie", value: 20 },
    ],
    performance: [
        { date: 'Jan', value: 10000 },
        { date: 'Fév', value: 10300 },
        { date: 'Mar', value: 10250 },
        { date: 'Avr', value: 10800 },
        { date: 'Mai', value: 11500 },
        { date: 'Juin', value: 12500 },
    ],
    suggestions: [
        "Envisager une prise de bénéfices sur SFBT (RSI > 70)",
        "Diversifier vers le secteur technologique pour réduire le risque",
        "Placer un stop-loss sur BIAT à 89.00"
    ]
};
