/**
 * @typedef {Object} Position
 * @property {string} symbol - Stock symbol
 * @property {number} quantity - Number of shares held
 * @property {number} buyPrice - Average buy price
 * @property {number} currentPrice - Current market price
 * @property {number} pl - Profit/Loss value
 */

/**
 * @typedef {Object} AllocationItem
 * @property {string} name - Sector or asset class name
 * @property {number} value - Percentage or value allocation
 */

/**
 * @typedef {Object} PerformancePoint
 * @property {string} date - Date label
 * @property {number} value - Portfolio value at that date
 */

/**
 * @typedef {Object} PortfolioResponse
 * @property {number} capital - Total portfolio value
 * @property {number} roi - Return on Investment percentage
 * @property {Position[]} positions - List of current holdings
 * @property {AllocationItem[]} allocation - Portfolio allocation data
 * @property {PerformancePoint[]} performance - Historical performance data
 * @property {string[]} suggestions - List of AI optimization suggestions
 */

export { };
