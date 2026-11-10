import { MarketOverviewResponse, StockTicker } from '../types';

const random = (min: number, max: number): number => Math.random() * (max - min) + min;
const randomInt = (min: number, max: number): number => Math.floor(random(min, max));

export const generateMarketOverview = (): MarketOverviewResponse => {
  const tunindexValue = random(9500, 10200);
  const tunindexChange = random(-50, 50);

  const companies = [
    "SFBT", "BIAT", "SAH", "POULINA", "CARTHAGE", "BT", "Attijari", "STB", "BNA", "UIB",
    "SOTIPAPIER", "ICF", "TELNET", "SOTETEL", "TPR", "ASSAD", "SOTUVER", "UNIMED", "DELICE"
  ];

  const generateStock = (symbol: string): StockTicker => ({
    symbol,
    price: Number(random(10, 120).toFixed(2)),
    change: Number(random(-3, 3).toFixed(2))
  });

  const shuffled = [...companies].sort(() => 0.5 - Math.random());
  const gainers = shuffled.slice(0, 5).map(generateStock).map(s => ({ ...s, change: Math.abs(s.change) }));
  const losers = shuffled.slice(5, 10).map(generateStock).map(s => ({ ...s, change: -Math.abs(s.change) }));

  return {
    index: {
      name: "TUNINDEX",
      value: Number(tunindexValue.toFixed(2)),
      change: Number(tunindexChange.toFixed(2))
    },
    gainers,
    losers,
    sentiment: 0.65,
    marketVolume: randomInt(500000, 2000000),
    activeTraders: randomInt(500, 1500),
    recent_alerts: [
      {
        id: 1,
        symbol: gainers[0]?.symbol || "BIAT",
        type: "volume",
        description: "Hausse inhabituelle des volumes de transaction",
        timestamp: "10:30"
      },
      {
        id: 2,
        symbol: "TUNINDEX",
        type: "market",
        description: "Franchissement de résistance clé",
        timestamp: "09:45"
      }
    ]
  };
};
