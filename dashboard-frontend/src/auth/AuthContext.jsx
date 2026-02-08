import React, { createContext, useState, useEffect } from 'react';
import mockAuthService from './mockAuthService';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Check for existing session on mount
    useEffect(() => {
        const user = mockAuthService.getCurrentUser();
        setCurrentUser(user);
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const { user, error } = await mockAuthService.login(email, password);
        if (user) {
            setCurrentUser(user);
        }
        return { user, error };
    };

    const register = async (email, password, name) => {
        const { user, error } = await mockAuthService.register(email, password, name);
        if (user) {
            // Auto-login after registration
            const loginResult = await mockAuthService.login(email, password);
            if (loginResult.user) {
                setCurrentUser(loginResult.user);
            }
        }
        return { user, error };
    };

    const logout = () => {
        mockAuthService.logout();
        setCurrentUser(null);
    };

    const value = {
        currentUser,
        login,
        register,
        logout,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
