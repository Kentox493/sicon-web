import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../services/api';

export const useAuthStore = create(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            login: async (username, password) => {
                set({ isLoading: true, error: null });
                try {
                    const data = await authAPI.login(username, password);
                    localStorage.setItem('access_token', data.access_token);

                    // Get user info
                    const user = await authAPI.getMe();

                    set({
                        token: data.access_token,
                        user,
                        isAuthenticated: true,
                        isLoading: false,
                    });

                    return true;
                } catch (error) {
                    set({
                        error: error.response?.data?.detail || 'Login failed',
                        isLoading: false,
                    });
                    return false;
                }
            },

            register: async (username, email, password) => {
                set({ isLoading: true, error: null });
                try {
                    await authAPI.register(username, email, password);
                    // Auto-login after register
                    return await get().login(username, password);
                } catch (error) {
                    set({
                        error: error.response?.data?.detail || 'Registration failed',
                        isLoading: false,
                    });
                    return false;
                }
            },

            logout: () => {
                localStorage.removeItem('access_token');
                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                });
            },

            checkAuth: async () => {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    set({ isAuthenticated: false });
                    return false;
                }

                try {
                    const user = await authAPI.getMe();
                    set({
                        user,
                        token,
                        isAuthenticated: true,
                    });
                    return true;
                } catch {
                    localStorage.removeItem('access_token');
                    set({ isAuthenticated: false });
                    return false;
                }
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: 's1c0n-auth',
            partialize: (state) => ({ token: state.token }),
        }
    )
);
