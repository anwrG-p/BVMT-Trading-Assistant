/** @type {import('../api/contracts/market').MarketOverviewResponse} */
export const MARKET_OVERVIEW_MOCK = {
    index: { name: "TUNINDEX", value: 8945.20, change: 0.45 },
    gainers: [
        { symbol: "SFBT", price: 13.80, change: 2.9 },
        { symbol: "BIAT", price: 92.50, change: 1.2 },
        { symbol: "SAH", price: 8.60, change: 0.9 },
        { symbol: "PGH", price: 11.40, change: 0.8 },
        { symbol: "SOTUVER", price: 12.95, change: 0.5 },
    ],
    losers: [
        { symbol: "CARTHAGE", price: 1.75, change: -2.8 },
        { symbol: "SERVICOM", price: 0.42, change: -2.1 },
        { symbol: "UADH", price: 0.32, change: -1.8 },
        { symbol: "GIF", price: 0.38, change: -1.5 },
        { symbol: "ELECTROSTAR", price: 0.28, change: -1.2 },
    ],
    sentiment: 0.65,
    recent_alerts: [
        { id: 1, symbol: "SFBT", type: "volume", description: "Hausse anormale du volume (+150%)", timestamp: "11:15" },
        { id: 2, symbol: "BIAT", type: "price", description: "Cassure de résistance à 92.00", timestamp: "10:30" },
        { id: 3, symbol: "MARKET", type: "news", description: "Annonce positive du secteur bancaire", timestamp: "09:45" },
    ]
};
