import { PortfolioResponse } from '../types';

const random = (min: number, max: number): number => Math.random() * (max - min) + min;

export const generatePortfolio = (): PortfolioResponse => {
  const symbols = ["SFBT", "BIAT", "SAH", "ATTIJARI BANK"];
  const positions = symbols.map(sym => {
    const qty = Math.floor(random(50, 400));
    const buyPrice = Number(random(10, 90).toFixed(2));
    const currentPrice = Number((buyPrice * (1 + random(-0.05, 0.12))).toFixed(2));
    const pl = Number(((currentPrice - buyPrice) * qty).toFixed(2));

    return {
      symbol: sym,
      quantity: qty,
      buyPrice,
      currentPrice,
      pl
    };
  });

  const capital = positions.reduce((acc, p) => acc + p.quantity * p.currentPrice, 0) + 12000;
  const cost = positions.reduce((acc, p) => acc + p.quantity * p.buyPrice, 0) + 12000;
  const roi = Number((((capital - cost) / cost) * 100).toFixed(2));

  const performance = [];
  const now = new Date();
  let baseVal = capital * 0.9;
  for (let i = 12; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i * 5);
    performance.push({
      date: date.toISOString().split('T')[0],
      value: Number(baseVal.toFixed(2))
    });
    baseVal = baseVal * (1 + random(-0.01, 0.02));
  }

  return {
    capital: Number(capital.toFixed(2)),
    roi,
    positions,
    allocation: [
      { name: "Secteur Bancaire", value: 55 },
      { name: "Agroalimentaire", value: 25 },
      { name: "Industrie", value: 12 },
      { name: "Liquidités", value: 8 }
    ],
    performance,
    suggestions: [
      "Surpondération sur le secteur bancaire. Rééquilibrer vers l'agroalimentaire.",
      "Conserver la position BIAT avec objectif à 98 TND.",
      "Renforcer SAH suite au support technique."
    ]
  };
};
