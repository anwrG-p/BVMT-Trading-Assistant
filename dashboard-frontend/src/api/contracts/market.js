/**
 * @typedef {Object} IndexData
 * @property {string} name - Name of the index (e.g., "TUNINDEX")
 * @property {number} value - Current value of the index
 * @property {number} change - Daily percentage change
 */

/**
 * @typedef {Object} StockTicker
 * @property {string} symbol - Stock symbol
 * @property {number} price - Current price
 * @property {number} change - Daily percentage change
 */

/**
 * @typedef {Object} MarketAlert
 * @property {number} id - Alert ID
 * @property {string} symbol - Stock symbol related to the alert
 * @property {'volume'|'price'|'news'|'market'} type - Type of alert
 * @property {string} description - Short description of the alert
 * @property {string} timestamp - Time of the alert (e.g., "10:30")
 */

/**
 * @typedef {Object} MarketOverviewResponse
 * @property {IndexData} index - Main market index data
 * @property {StockTicker[]} gainers - Top 5 gaining stocks
 * @property {StockTicker[]} losers - Top 5 losing stocks
 * @property {number} sentiment - Global market sentiment score (0 to 1)
 * @property {MarketAlert[]} recent_alerts - List of recent market alerts
 */

/**
 * @typedef {Object} PricePoint
 * @property {string} date - Date or time label
 * @property {number} value - Price value
 * @property {boolean} [forecast] - Whether this point is a forecast
 */

/**
 * @typedef {Object} SentimentPoint
 * @property {string} date - Date label
 * @property {number} score - Sentiment score (0 to 1)
 */

/**
 * @typedef {Object} TechnicalIndicators
 * @property {number} rsi - Relative Strength Index value
 * @property {string} macd - MACD interpretation (e.g., "Bullish Crossover")
 */

/**
 * @typedef {Object} Recommendation
 * @property {'ACHETER'|'VENDRE'|'CONSERVER'} action - Recommended action
 * @property {number} confidence - Confidence score (0 to 100)
 */

/**
 * @typedef {Object} StockAnalysisResponse
 * @property {string} symbol - Stock symbol
 * @property {string} name - Full company name
 * @property {PricePoint[]} price_history - Historical price data and forecast
 * @property {SentimentPoint[]} sentiment_timeline - Sentiment history
 * @property {TechnicalIndicators} indicators - Technical indicators
 * @property {Recommendation} recommendation - AI recommendation
 */

export { };
