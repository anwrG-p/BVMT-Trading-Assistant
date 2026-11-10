import { AlertsResponse, AlertDetail } from '../types';

const TYPES = ["Volume", "Price", "News", "Market"];
const SEVERITIES: Array<'High' | 'Medium' | 'Low'> = ["Low", "Medium", "High"];

const randomInt = (min: number, max: number): number => Math.floor(Math.random() * (max - min) + min);
const randomItem = <T>(arr: T[]): T => arr[randomInt(0, arr.length)];

export const generateAlerts = (): AlertsResponse => {
  const alerts: AlertDetail[] = [];
  const companies = ["SFBT", "BIAT", "SAH", "ATTIJARI", "POULINA"];

  for (let i = 1; i <= 10; i++) {
    const date = new Date();
    date.setMinutes(date.getMinutes() - randomInt(0, 300));

    alerts.push({
      id: i,
      symbol: randomItem(companies),
      type: randomItem(TYPES),
      severity: randomItem(SEVERITIES),
      message: "Mouvement inhabituel détecté par les modèles quantitatifs.",
      description: "Mouvement inhabituel détecté par les modèles quantitatifs.",
      timestamp: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: Math.random() > 0.6 ? "Resolved" : "Open"
    });
  }

  return {
    alerts: alerts.sort((a, b) => b.id - a.id),
    filters: ["All", ...TYPES]
  };
};
