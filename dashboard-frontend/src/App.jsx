import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, TrendingUp, Briefcase, Bell, Settings as SettingsIcon, User, BarChart2, LogOut, MessageSquare, AlertTriangle, X, CheckCircle } from 'lucide-react';
import { AuthProvider } from './auth/AuthContext';
import { useAuth } from './auth/useAuth';
import ProtectedRoute from './routes/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import MarketOverview from './pages/MarketOverview';
import StockAnalysis from './pages/StockAnalysis';
import Portfolio from './pages/Portfolio';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import UserCenter from './pages/UserCenter';
import ChatbotPanel from './components/ChatbotPanel';
import './App.css';

const TopNavbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const isActive = (path) => location.pathname === path ? 'active' : '';
  const [timeframe, setTimeframe] = useState('1D');
  const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
  const { currentUser, logout } = useAuth();
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Mock notifications
  const notifications = [
    { id: 1, title: 'BIAT: Anomalie détectée', time: 'Il y a 2 min', read: false },
    { id: 2, title: 'SFBT: Objectif atteint', time: 'Il y a 15 min', read: true },
    { id: 3, title: 'Nouveau rapport de marché', time: 'Il y a 1h', read: true },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!currentUser?.name) return 'U';
    const names = currentUser.name.split(' ');
    if (names.length >= 2) {
      return names[0][0] + names[1][0];
    }
    return names[0][0];
  };

  return (
    <div className="navbar">
      {/* Left: Brand */}
      <div className="navbar-brand">
        <div style={{ width: '20px', height: '20px', background: 'var(--accent)', borderRadius: '50%' }}></div>
        <span className="navbar-title">BVMT AI</span>
      </div>

      {/* Center: Empty for now */}
      {currentUser && (
        <div className="navbar-center" style={{ justifyContent: 'center' }}>
          {/* Removed search and tools - now in Stock Analysis page */}
        </div>
      )}

      {/* Right: Actions */}
      <div className="navbar-actions">
        {currentUser ? (
          <>
            {/* Navigation Links with Expandable Labels */}
            <Link to="/" className={`nav-icon-expandable ${isActive('/') ? 'active' : ''}`}>
              <span className="nav-label">Marché</span>
              <LayoutDashboard size={18} />
            </Link>
            <Link to="/stock" className={`nav-icon-expandable ${isActive('/stock') ? 'active' : ''}`}>
              <span className="nav-label">Analyse</span>
              <TrendingUp size={18} />
            </Link>
            <Link to="/portfolio" className={`nav-icon-expandable ${isActive('/portfolio') ? 'active' : ''}`}>
              <span className="nav-label">Portefeuille</span>
              <Briefcase size={18} />
            </Link>
            <Link to="/alerts" className={`nav-icon-expandable ${isActive('/alerts') ? 'active' : ''}`}>
              <span className="nav-label">Alertes</span>
              <AlertTriangle size={18} />
            </Link>

            <div style={{ width: '1px', height: '20px', background: 'var(--border)', margin: '0 0.5rem' }}></div>

            {USE_MOCK && (
              <span style={{ fontSize: '10px', color: 'var(--warning)', border: '1px solid var(--warning)', padding: '2px 6px', borderRadius: '4px' }}>DEMO</span>
            )}

            <div style={{ position: 'relative' }}>
              <button
                className={`icon-button ${showNotifications ? 'active' : ''}`}
                title="Notifications"
                onClick={() => setShowNotifications(!showNotifications)}
                style={{ position: 'relative' }}
              >
                <Bell size={18} />
                <span style={{
                  position: 'absolute',
                  top: '0',
                  right: '0',
                  width: '8px',
                  height: '8px',
                  background: 'var(--danger)',
                  borderRadius: '50%',
                  border: '1px solid var(--bg-card)'
                }}></span>
              </button>

              {/* Floating Notifications Panel */}
              {showNotifications && (
                <div style={{
                  position: 'absolute',
                  top: '120%',
                  right: 0,
                  width: '320px',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                  zIndex: 1000,
                  overflow: 'hidden',
                  animation: 'slideDown 0.2s ease'
                }}>
                  <div style={{
                    padding: '1rem',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: '600', margin: 0 }}>Notifications</h3>
                    <button
                      onClick={() => setShowNotifications(false)}
                      style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
                    >
                      <X size={16} />
                    </button>
                  </div>
                  <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {notifications.map(notif => (
                      <div key={notif.id} style={{
                        padding: '0.75rem 1rem',
                        borderBottom: '1px solid var(--border)',
                        background: notif.read ? 'transparent' : 'rgba(0, 212, 255, 0.05)',
                        cursor: 'pointer',
                        transition: 'background 0.2s'
                      }} className="notification-item">
                        <div style={{ fontSize: '0.875rem', fontWeight: notif.read ? '400' : '600', marginBottom: '0.25rem' }}>
                          {notif.title}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {notif.time}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div style={{
                    padding: '0.75rem',
                    textAlign: 'center',
                    borderTop: '1px solid var(--border)',
                    fontSize: '0.8rem',
                    color: 'var(--accent)',
                    cursor: 'pointer',
                    fontWeight: '500'
                  }}>
                    Tout marquer comme lu
                  </div>
                </div>
              )}
            </div>
            <button
              className="icon-button"
              title="Assistant IA"
              onClick={() => setIsChatbotOpen(true)}
            >
              <MessageSquare size={18} />
            </button>
            <Link to="/settings" className="icon-button" title="Paramètres">
              <SettingsIcon size={18} />
            </Link>

            <div style={{ position: 'relative' }}>
              <Link
                to="/profile"
                className="icon-button"
                title={currentUser.name}
                style={{ position: 'relative' }}
              >
                <div style={{ width: '24px', height: '24px', background: 'var(--accent)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '10px', fontWeight: '600' }}>
                  {getUserInitials()}
                </div>
              </Link>
            </div>

            <button
              className="icon-button"
              title="Déconnexion"
              onClick={handleLogout}
            >
              <LogOut size={18} />
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-item-btn">
              Connexion
            </Link>
            <Link to="/register" className="nav-item-btn" style={{ background: 'var(--accent)', color: 'white' }}>
              S'inscrire
            </Link>
          </>
        )}
      </div>
      <ChatbotPanel isOpen={isChatbotOpen} onClose={() => setIsChatbotOpen(false)} />
    </div>
  );
};

const AppRoutes = () => {
  const location = useLocation();
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  if (isAuthPage) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    );
  }

  return (
    <div className="layout">
      <TopNavbar />
      <main className="main-content">
        <Routes>
          {/* Protected Routes */}
          <Route path="/" element={<ProtectedRoute><MarketOverview /></ProtectedRoute>} />
          <Route path="/stock" element={<ProtectedRoute><StockAnalysis /></ProtectedRoute>} />
          <Route path="/portfolio" element={<ProtectedRoute><Portfolio /></ProtectedRoute>} />
          <Route path="/alerts" element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><UserCenter /></ProtectedRoute>} />

          <Route path="*" element={<ProtectedRoute><MarketOverview /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
