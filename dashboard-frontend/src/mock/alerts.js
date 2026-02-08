/** @type {import('../api/contracts/alerts').AlertsResponse} */
export const ALERTS_MOCK = {
    alerts: [
        { id: 1, symbol: "SFBT", type: "Volume", severity: "High", timestamp: "11:15", status: "Open" },
        { id: 2, symbol: "BIAT", type: "Price", severity: "Medium", timestamp: "10:30", status: "Resolved" },
        { id: 3, symbol: "SAH", type: "News", severity: "Low", timestamp: "09:00", status: "Open" },
        { id: 4, symbol: "TUNINDEX", type: "Market", severity: "High", timestamp: "08:55", status: "Resolved" },
    ],
    filters: ["Volume", "Price", "News", "Market"]
};
