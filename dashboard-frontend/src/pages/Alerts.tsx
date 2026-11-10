import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Filter, CheckCircle, AlertCircle, Info, ChevronDown, ArrowUpDown, Eye, TrendingUp, TrendingDown, X } from 'lucide-react';
import { AlertDetail } from '../types';

interface AlertHistoryItem {
  id: string;
  symbol: string;
  type: string;
  date: string;
  action: string;
  result: string;
  success: boolean;
}

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertDetail[]>([]);
  const [filters, setFilters] = useState<string[]>([]);
  const [activeFilter, setActiveFilter] = useState<string>('All');
  const [filterDropdownOpen, setFilterDropdownOpen] = useState<boolean>(false);
  const [historyOpen, setHistoryOpen] = useState<boolean>(false);
  const [reverseSort, setReverseSort] = useState<boolean>(false);
  const [expandedAlerts, setExpandedAlerts] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const alertHistory: AlertHistoryItem[] = [
    {
      id: 'h1',
      symbol: 'BIAT',
      type: 'Anomalie',
      date: '2026-02-05 14:30',
      action: 'Position fermée à 126.20 TND',
      result: '+2.8%',
      success: true
    },
    {
      id: 'h2',
      symbol: 'SFBT',
      type: 'Prédiction',
      date: '2026-02-03 09:15',
      action: 'Achat de 50 actions à 12.10 TND',
      result: '+5.2%',
      success: true
    },
    {
      id: 'h3',
      symbol: 'SAH',
      type: 'Volatilité',
      date: '2026-02-01 16:45',
      action: 'Stop-loss déclenché à 11.50 TND',
      result: '-1.5%',
      success: false
    }
  ];

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const data = await api.getAlerts();
        setAlerts(data.alerts || []);
        setFilters(data.filters || []);
      } catch (err) {
        console.error("Error fetching alerts:", err);
        setError("Impossible de charger le flux d'alertes.");
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  const toggleAlertDetails = (alertId: number) => {
    const newExpanded = new Set(expandedAlerts);
    if (newExpanded.has(alertId)) {
      newExpanded.delete(alertId);
    } else {
      newExpanded.add(alertId);
    }
    setExpandedAlerts(newExpanded);
  };

  const filteredAlerts = activeFilter === 'All'
    ? alerts
    : alerts.filter(a => a.type.toLowerCase() === activeFilter.toLowerCase());

  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    return reverseSort ? a.id - b.id : b.id - a.id;
  });

  const getStatusIcon = (status: string) => {
    return status === 'Resolved'
      ? <CheckCircle size={18} className="text-success" />
      : <AlertCircle size={18} className="text-warning" />;
  };

  if (loading) return <div className="p-8 text-center" style={{ color: 'var(--secondary)' }}>Chargement des alertes...</div>;

  if (error) return (
    <div className="card text-danger" style={{ margin: '2rem', textAlign: 'center' }}>
      <div className="card-title">Erreur</div>
      <p>{error}</p>
    </div>
  );

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Surveillance & Alertes Marché</h1>
      </div>

      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: filterDropdownOpen ? '1rem' : '0' }}>
            <button
              onClick={() => setFilterDropdownOpen(!filterDropdownOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.25rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '12px',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <Filter size={18} style={{ color: 'var(--accent)' }} />
              <span>Filtres ({activeFilter})</span>
              <ChevronDown
                size={16}
                style={{
                  color: 'var(--text-secondary)',
                  transform: filterDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s'
                }}
              />
            </button>
          </div>

          {filterDropdownOpen && (
            <div style={{
              display: 'flex',
              gap: '0.75rem',
              flexWrap: 'wrap',
              paddingTop: '0.5rem'
            }}>
              <button
                style={{
                  border: activeFilter === 'All' ? '1px solid var(--accent)' : '1px solid rgba(255, 255, 255, 0.1)',
                  cursor: 'pointer',
                  background: activeFilter === 'All' ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                  color: activeFilter === 'All' ? 'var(--accent)' : 'var(--text-secondary)',
                  padding: '0.6rem 1.25rem',
                  fontSize: '0.875rem',
                  borderRadius: '12px',
                  fontWeight: activeFilter === 'All' ? '600' : '400',
                  transition: 'all 0.2s'
                }}
                onClick={() => setActiveFilter('All')}
              >
                Tous
              </button>
              {filters.filter(f => f !== 'All').map(filter => (
                <button
                  key={filter}
                  style={{
                    border: activeFilter === filter ? '1px solid var(--accent)' : '1px solid rgba(255, 255, 255, 0.1)',
                    cursor: 'pointer',
                    background: activeFilter === filter ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                    color: activeFilter === filter ? 'var(--accent)' : 'var(--text-secondary)',
                    padding: '0.6rem 1.25rem',
                    fontSize: '0.875rem',
                    borderRadius: '12px',
                    fontWeight: activeFilter === filter ? '600' : '400',
                    transition: 'all 0.2s'
                  }}
                  onClick={() => setActiveFilter(filter)}
                >
                  {filter}
                </button>
              ))}
              <button
                onClick={() => setReverseSort(!reverseSort)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.6rem 1.25rem',
                  background: reverseSort ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                  border: reverseSort ? '1px solid var(--accent)' : '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  color: reverseSort ? 'var(--accent)' : 'var(--text-secondary)',
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <ArrowUpDown size={16} />
                <span>Tri {reverseSort ? 'Ancien' : 'Récent'}</span>
              </button>
            </div>
          )}
        </div>

        <div style={{ flex: 1 }}>
          <button
            onClick={() => setHistoryOpen(!historyOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1.25rem',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              color: 'var(--text-primary)',
              fontSize: '0.875rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              width: '100%',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Info size={18} style={{ color: 'var(--accent)' }} />
              <span>Historique des alertes exécutées</span>
            </div>
            <ChevronDown
              size={16}
              style={{
                color: 'var(--text-secondary)',
                transform: historyOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.2s'
              }}
            />
          </button>

          {historyOpen && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem' }}>
              {alertHistory.map(item => (
                <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px' }}>
                  <div>
                    <strong style={{ color: 'var(--accent)' }}>{item.symbol}</strong> ({item.type}) - {item.action}
                  </div>
                  <div style={{ color: item.success ? 'var(--success)' : 'var(--danger)', fontWeight: 'bold' }}>
                    {item.result}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Active Alerts */}
      <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-title" style={{ marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Flux d'Alertes en Temps Réel</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {sortedAlerts.length > 0 ? sortedAlerts.map((alert) => (
            <div key={alert.id}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                padding: '1.25rem',
                background: 'rgba(255, 255, 255, 0.03)',
                borderRadius: '16px',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                borderLeft: `4px solid ${alert.severity === 'High' ? 'var(--danger)' : alert.severity === 'Medium' ? 'var(--warning)' : 'var(--accent)'}`,
                transition: 'transform 0.2s ease, background 0.2s ease',
              }}>
                <div style={{ marginRight: '1.25rem' }}>
                  {getStatusIcon(alert.status)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <strong style={{ fontSize: '1.125rem', color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>{alert.symbol}</strong>
                    <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{alert.timestamp}</span>
                    <span style={{
                      fontSize: '0.75rem',
                      padding: '0.2rem 0.6rem',
                      borderRadius: '6px',
                      fontWeight: '600',
                      background: alert.severity === 'High' ? 'rgba(239, 68, 68, 0.1)' : alert.severity === 'Medium' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(0, 212, 255, 0.1)',
                      color: alert.severity === 'High' ? 'var(--danger)' : alert.severity === 'Medium' ? 'var(--warning)' : 'var(--accent)',
                      border: '1px solid rgba(255, 255, 255, 0.05)'
                    }}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem' }}>
                    <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{alert.type}:</span> {alert.description || alert.message || "Anomalie détectée par les algorithmes de surveillance."}
                  </div>
                </div>
                <div>
                  <button
                    onClick={() => toggleAlertDetails(alert.id)}
                    style={{
                      padding: '0.6rem 1.25rem',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '10px',
                      background: expandedAlerts.has(alert.id) ? 'rgba(0, 212, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                      color: expandedAlerts.has(alert.id) ? 'var(--accent)' : 'var(--text-primary)',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '600',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    <Eye size={16} />
                    {expandedAlerts.has(alert.id) ? 'Masquer' : 'Détails'}
                  </button>
                </div>
              </div>

              {expandedAlerts.has(alert.id) && (
                <div style={{
                  marginTop: '0.5rem',
                  padding: '1.5rem',
                  background: 'rgba(0, 212, 255, 0.03)',
                  borderRadius: '12px',
                  border: '1px solid rgba(0, 212, 255, 0.1)'
                }}>
                  <div className="grid-cols-3" style={{ gap: '1.5rem' }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Valeur Surveillée</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{alert.symbol}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Type de Détection</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--accent)' }}>{alert.type}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Statut Traitement</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: alert.status === 'Resolved' ? 'var(--success)' : 'var(--warning)' }}>{alert.status}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )) : (
            <div style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-muted)' }}>
              <Info size={32} style={{ marginBottom: '1rem', opacity: 0.3 }} />
              <div style={{ fontSize: '1.125rem' }}>Aucune alerte trouvée pour ce filtre.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Alerts;
