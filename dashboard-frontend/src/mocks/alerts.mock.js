/**
 * @typedef {Object} Alert
 * @property {number} id
 * @property {string} symbol
 * @property {string} type
 * @property {string} severity
 * @property {string} message
 * @property {string} timestamp
 * @property {string} status
 */

const TYPES = ["Volume", "Prix", "RSI", "News"];
const SEVERITIES = ["Low", "Medium", "High"];

const randomInt = (min, max) => Math.floor(Math.random() * (max - min) + min);
const randomItem = (arr) => arr[randomInt(0, arr.length)];

export const generateAlerts = () => {
    const alerts = [];
    const companies = ["SFBT", "BIAT", "SAH", "POULINA"];

    for (let i = 0; i < 15; i++) {
        const date = new Date();
        date.setMinutes(date.getMinutes() - randomInt(0, 300));

        alerts.push({
            id: i,
            symbol: randomItem(companies),
            type: randomItem(TYPES),
            severity: randomItem(SEVERITIES),
            message: "Mouvement inhabituel détecté.",
            timestamp: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: Math.random() > 0.7 ? "Resolved" : "Open"
        });
    }

    return {
        alerts: alerts.sort((a, b) => b.id - a.id),
        filters: TYPES
    };
};
