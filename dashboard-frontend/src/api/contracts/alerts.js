/**
 * @typedef {Object} AlertDetail
 * @property {number} id - Unique alert ID
 * @property {string} symbol - Related stock symbol
 * @property {string} type - Type of alert (Volume, Price, News, Market)
 * @property {'High'|'Medium'|'Low'} severity - Severity level
 * @property {string} timestamp - Timestamp of the alert
 * @property {'Open'|'Resolved'} status - Current status of the alert
 */

/**
 * @typedef {Object} AlertsResponse
 * @property {AlertDetail[]} alerts - List of all system alerts
 * @property {string[]} filters - Available filter categories
 */

export { };
