/**
 * Mock Authentication Service
 * Uses localStorage to simulate user authentication
 * Easily replaceable with real API calls
 */

const USERS_KEY = 'bvmt_users';
const CURRENT_USER_KEY = 'bvmt_current_user';

// Initialize demo user if no users exist
const initializeDemoUser = () => {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    if (users.length === 0) {
        const demoUser = {
            id: '1',
            email: 'demo@bvmt.tn',
            password: 'demo123',
            name: 'Demo User',
            createdAt: new Date().toISOString()
        };
        localStorage.setItem(USERS_KEY, JSON.stringify([demoUser]));
    }
};

initializeDemoUser();

const mockAuthService = {
    /**
     * Register a new user
     * @param {string} email 
     * @param {string} password 
     * @param {string} name 
     * @returns {Promise<{user, error}>}
     */
    async register(email, password, name) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500));

        const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');

        // Check if user already exists
        if (users.find(u => u.email === email)) {
            return { user: null, error: 'Un compte avec cet email existe déjà' };
        }

        // Create new user
        const newUser = {
            id: Date.now().toString(),
            email,
            password, // In real app, this would be hashed
            name,
            createdAt: new Date().toISOString()
        };

        users.push(newUser);
        localStorage.setItem(USERS_KEY, JSON.stringify(users));

        // Return user without password
        const { password: _, ...userWithoutPassword } = newUser;
        return { user: userWithoutPassword, error: null };
    },

    /**
     * Login user
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise<{user, error}>}
     */
    async login(email, password) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500));

        const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
        const user = users.find(u => u.email === email && u.password === password);

        if (!user) {
            return { user: null, error: 'Email ou mot de passe incorrect' };
        }

        // Store current user
        const { password: _, ...userWithoutPassword } = user;
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userWithoutPassword));

        return { user: userWithoutPassword, error: null };
    },

    /**
     * Logout current user
     */
    logout() {
        localStorage.removeItem(CURRENT_USER_KEY);
    },

    /**
     * Get current logged in user
     * @returns {object|null}
     */
    getCurrentUser() {
        const userJson = localStorage.getItem(CURRENT_USER_KEY);
        return userJson ? JSON.parse(userJson) : null;
    }
};

export default mockAuthService;
