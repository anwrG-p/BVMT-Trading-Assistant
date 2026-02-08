/**
 * @typedef {Object} MarketIndex
 * @property {string} name
 * @property {number} value
 * @property {number} change
 * @property {number} changePercent
 */

/**
 * @typedef {Object} StockTicker
 * @property {string} symbol
 * @property {string} name
 * @property {number} price
 * @property {number} change
 * @property {number} changePercent
 * @property {number} volume
 */

/**
 * @typedef {Object} MarketOverview
 * @property {MarketIndex} index
 * @property {StockTicker[]} gainers
 * @property {StockTicker[]} losers
 * @property {number} marketVolume
 * @property {number} activeTraders
 */

/**
 * Generates a random number between min and max
 * @param {number} min 
 * @param {number} max 
 * @returns {number}
 */
const random = (min, max) => Math.random() * (max - min) + min;

/**
 * Generates a random integer
 * @param {number} min 
 * @param {number} max 
 * @returns {number}
 */
const randomInt = (min, max) => Math.floor(random(min, max));

/**
 * Generates market overview data
 * @returns {MarketOverview}
 */
export const generateMarketOverview = () => {
    const tunindexValue = random(8500, 9200);
    const tunindexChange = random(-50, 50);

    const companies = [
        "SFBT", "BIAT", "SAH", "POULINA", "CARTHAGE", "BT", "Attijari", "STB", "BNA", "UIB",
        "SOTIPAPIER", "ICF", "TELNET", "SOTETEL", "TPR", "ASSAD", "SOTUVER", "UNIMED", "DELICE"
    ];

    const generateStock = (symbol) => ({
        symbol,
        name: `${symbol} Corp`,
        price: random(10, 200),
        change: random(-2, 2),
        changePercent: random(-5, 5),
        volume: randomInt(1000, 50000)
    });

    // Shuffle and pick
    const shuffled = [...companies].sort(() => 0.5 - Math.random());
    const gainers = shuffled.slice(0, 5).map(generateStock).map(s => ({ ...s, change: Math.abs(s.change), changePercent: Math.abs(s.changePercent) }));
    const losers = shuffled.slice(5, 10).map(generateStock).map(s => ({ ...s, change: -Math.abs(s.change), changePercent: -Math.abs(s.changePercent) }));

    return {
        index: {
            name: "TUNINDEX",
            value: Number(tunindexValue.toFixed(2)),
            change: Number(tunindexChange.toFixed(2)),
            changePercent: Number((tunindexChange / tunindexValue * 100).toFixed(2))
        },
        gainers,
        losers,
        marketVolume: randomInt(500000, 2000000),
        activeTraders: randomInt(500, 1500)
    };
};
