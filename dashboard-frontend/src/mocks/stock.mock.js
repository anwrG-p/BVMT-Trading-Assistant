/**
 * @typedef {Object} PricePoint
 * @property {string} date
 * @property {number} value
 */

/**
 * @typedef {Object} StockAnalysis
 * @property {string} symbol
 * @property {string} name
 * @property {number} currentPrice
 * @property {number} change
 * @property {PricePoint[]} history - Last 30 days
 * @property {PricePoint[]} forecast - Next 5 days
 * @property {Object} indicators
 * @property {number} indicators.rsi
 * @property {number} indicators.macd
 * @property {string} indicators.signal
 * @property {Object} recommendation
 * @property {'ACHETER' | 'VENDRE' | 'CONSERVER'} recommendation.action
 * @property {number} recommendation.confidence
 * @property {Object[]} sentimentHistory
 */

const random = (min, max) => Math.random() * (max - min) + min;

/**
 * Random Walk generator
 */
const generateRandomWalk = (startPrice, steps, volatility = 0.02) => {
    let price = startPrice;
    const data = [];
    const now = new Date();

    for (let i = steps; i > 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        data.push({
            date: date.toISOString().split('T')[0],
            value: Number(price.toFixed(2))
        });
        price = price * (1 + random(-volatility, volatility));
    }
    return { data, lastPrice: price };
};

export const generateStockAnalysis = (symbol) => {
    const startPrice = random(10, 150);
    const { data: history, lastPrice } = generateRandomWalk(startPrice, 30);

    // Forecast
    let forecastPrice = lastPrice;
    const forecast = [];
    for (let i = 1; i <= 5; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        forecastPrice = forecastPrice * (1 + random(-0.02, 0.025)); // Slight bullish bias
        forecast.push({
            date: date.toISOString().split('T')[0],
            value: Number(forecastPrice.toFixed(2))
        });
    }

    const rsi = Math.floor(random(20, 80));
    const action = rsi < 30 ? 'ACHETER' : rsi > 70 ? 'VENDRE' : 'CONSERVER';
    const confidence = Math.floor(random(60, 95));

    return {
        symbol,
        name: `${symbol} Corp`,
        currentPrice: Number(lastPrice.toFixed(2)),
        change: Number((lastPrice - history[history.length - 2].value).toFixed(2)),
        history,
        forecast,
        indicators: {
            rsi,
            macd: Number(random(-0.5, 0.5).toFixed(3)),
            signal: random(0, 1) > 0.5 ? "Bullish" : "Bearish"
        },
        recommendation: {
            action,
            confidence
        },
        sentimentHistory: history.map(h => ({
            date: h.date,
            score: Number(random(0.3, 0.9).toFixed(2))
        }))
    };
};
