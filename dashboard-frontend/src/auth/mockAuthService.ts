import { User } from '../types';

const USERS_KEY = 'bvmt_users';
const CURRENT_USER_KEY = 'bvmt_current_user';

interface StoredUser extends User {
  password?: string;
  createdAt?: string;
}

const initializeDemoUser = (): void => {
  if (typeof window === 'undefined') return;
  const users: StoredUser[] = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
  if (users.length === 0) {
    const demoUser: StoredUser = {
      id: '1',
      email: 'demo@bvmt.tn',
      password: 'demo123',
      name: 'Trader Demo',
      role: 'Analyste Marché',
      createdAt: new Date().toISOString()
    };
    localStorage.setItem(USERS_KEY, JSON.stringify([demoUser]));
  }
};

initializeDemoUser();

const mockAuthService = {
  async register(email: string, password: string, name: string): Promise<{ user: User | null; error: string | null }> {
    await new Promise(resolve => setTimeout(resolve, 300));
    const users: StoredUser[] = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');

    if (users.find(u => u.email.toLowerCase() === email.toLowerCase())) {
      return { user: null, error: 'Un compte avec cet email existe déjà' };
    }

    const newUser: StoredUser = {
      id: Date.now().toString(),
      email,
      password,
      name,
      role: 'Investisseur',
      createdAt: new Date().toISOString()
    };

    users.push(newUser);
    localStorage.setItem(USERS_KEY, JSON.stringify(users));

    const { password: _, ...userWithoutPassword } = newUser;
    return { user: userWithoutPassword, error: null };
  },

  async login(email: string, password: string): Promise<{ user: User | null; error: string | null }> {
    await new Promise(resolve => setTimeout(resolve, 300));
    const users: StoredUser[] = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);

    if (!user) {
      return { user: null, error: 'Email ou mot de passe incorrect' };
    }

    const { password: _, ...userWithoutPassword } = user;
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userWithoutPassword));
    return { user: userWithoutPassword, error: null };
  },

  logout(): void {
    localStorage.removeItem(CURRENT_USER_KEY);
  },

  getCurrentUser(): User | null {
    if (typeof window === 'undefined') return null;
    const userJson = localStorage.getItem(CURRENT_USER_KEY);
    return userJson ? JSON.parse(userJson) : null;
  }
};

export default mockAuthService;
