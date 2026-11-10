import React from 'react';
import { useAuth } from '../auth/useAuth';
import { Calendar, Activity, TrendingUp, Clock, Shield } from 'lucide-react';

const UserCenter: React.FC = () => {
  const { currentUser } = useAuth();

  const user = currentUser || {
    name: 'Trader Demo',
    email: 'demo@bvmt.tn',
    role: 'Analyste Quantitatif'
  };

  const getUserInitials = () => {
    if (!user.name) return 'U';
    const names = user.name.split(' ');
    if (names.length >= 2) return names[0][0] + names[1][0];
    return names[0][0];
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Profil & Espace Utilisateur</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '2rem' }}>
        {/* Profile Card */}
        <div className="glass-card" style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{
            width: '100px',
            height: '100px',
            background: 'var(--accent)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '2.5rem',
            fontWeight: 'bold',
            margin: '0 auto 1.5rem',
            boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)'
          }}>
            {getUserInitials()}
          </div>

          <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>{user.name}</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>{user.email}</p>

          <div style={{ display: 'inline-block', padding: '0.4rem 1rem', background: 'rgba(0, 212, 255, 0.1)', color: 'var(--accent)', borderRadius: '20px', fontSize: '0.875rem', fontWeight: '600' }}>
            {user.role || 'Trader Actif'}
          </div>

          <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid var(--border)', textAlign: 'left' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              <Calendar size={18} />
              <span>Membre certifié depuis {formatDate(new Date())}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-secondary)' }}>
              <Shield size={18} />
              <span>Session sécurisée active</span>
            </div>
          </div>
        </div>

        {/* Stats & Activity */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Stats Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                <Activity size={20} style={{ color: 'var(--accent)' }} />
                <span>Analyses Consultées</span>
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 'bold' }}>1,245</div>
            </div>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                <TrendingUp size={20} style={{ color: 'var(--success)' }} />
                <span>Performance Suivie</span>
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'var(--success)' }}>+18.4%</div>
            </div>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                <Clock size={20} style={{ color: 'var(--warning)' }} />
                <span>Fréquence</span>
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 'bold' }}>Temps réel</div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="glass-card" style={{ flex: 1 }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity size={20} style={{ color: 'var(--accent)' }} />
              Activité Récente de Session
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { action: 'Consultation prévisions XGBoost sur BIAT', device: 'Terminal de trading', time: 'Il y a 2 minutes' },
                { action: 'Optimisation portefeuille Sharpe Ratio', device: 'Moteur analytique', time: 'Il y a 1 heure' },
                { action: 'Alerte franchissement seuil sur SFBT', device: 'Moteur de signaux', time: 'Aujourd\'hui' },
              ].map((item, index) => (
                <div key={index} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '1rem',
                  background: 'rgba(255,255,255,0.03)',
                  borderRadius: '10px',
                  border: '1px solid var(--border)'
                }}>
                  <div>
                    <div style={{ fontWeight: '500', marginBottom: '0.25rem' }}>{item.action}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.device}</div>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{item.time}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserCenter;
