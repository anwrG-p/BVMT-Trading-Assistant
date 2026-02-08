/**
 * @typedef {Object} Position
 * @property {string} symbol
 * @property {number} quantity
 * @property {number} buyPrice
 * @property {number} currentPrice
 * @property {number} totalValue
 * @property {number} pl
 * @property {number} plPercent
 */

/**
 * @typedef {Object} Portfolio
 * @property {number} totalCapital
 * @property {number} availableCash
 * @property {number} investedCapital
 * @property {number} roi
 * @property {Position[]} positions
 * @property {Object[]} allocation
 * @property {Object[]} performance
 * @property {string[]} suggestions
 */

const random = (min, max) => Math.random() * (max - min) + min;

export const generatePortfolio = () => {
    const symbols = ["SFBT", "BIAT", "SAH", "TELNET", "UNIMED"];
    const positions = symbols.map(sym => {
        const qty = Math.floor(random(10, 500));
        const buyPrice = random(10, 100);
        const currentPrice = buyPrice * (1 + random(-0.1, 0.15));

        return {
            symbol: sym,
            quantity: qty,
            buyPrice: Number(buyPrice.toFixed(2)),
            currentPrice: Number(currentPrice.toFixed(2)),
            totalValue: Number((qty * currentPrice).toFixed(2)),
            pl: Number((qty * (currentPrice - buyPrice)).toFixed(2)),
            plPercent: Number(((currentPrice - buyPrice) / buyPrice * 100).toFixed(2))
        };
    });

    const investedCapital = positions.reduce((sum, p) => sum + p.totalValue, 0);
    const availableCash = random(2000, 10000);
    const totalCapital = investedCapital + availableCash;
    const totalPL = positions.reduce((sum, p) => sum + p.pl, 0);
    const roi = (totalPL / (totalCapital - totalPL)) * 100;

    // Perf history
    const performance = [];
    const now = new Date();
    let val = totalCapital * 0.9;
    for (let i = 30; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        performance.push({
            date: date.toISOString().split('T')[0],
            value: Number(val.toFixed(2))
        });
        val = val * (1 + random(-0.01, 0.015));
    }

    return {
        totalCapital: Number(totalCapital.toFixed(2)),
        availableCash: Number(availableCash.toFixed(2)),
        investedCapital: Number(investedCapital.toFixed(2)),
        roi: Number(roi.toFixed(2)),
        positions,
        allocation: positions.map(p => ({ name: p.symbol, value: p.totalValue })),
        performance,
        suggestions: [
            "Diversifiez votre portefeuille avec des valeurs bancaires.",
            "Surveillez la volatilité de SAH.",
            "Considérez une prise de bénéfices sur SFBT."
        ]
    };
};
