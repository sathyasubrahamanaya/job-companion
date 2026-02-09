import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import type { User, UserRole } from '$lib/api/types';

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
}

function createAuthStore() {
    const initialState: AuthState = {
        user: null,
        token: null,
        isAuthenticated: false
    };

    // Load from localStorage on init
    if (browser) {
        const savedToken = localStorage.getItem('access_token');
        const savedUser = localStorage.getItem('user');
        if (savedToken && savedUser) {
            initialState.token = savedToken;
            initialState.user = JSON.parse(savedUser);
            initialState.isAuthenticated = true;
        }
    }

    const { subscribe, set, update } = writable<AuthState>(initialState);

    return {
        subscribe,
        setAuth: (user: User, token: string) => {
            if (browser) {
                localStorage.setItem('access_token', token);
                localStorage.setItem('user', JSON.stringify(user));
            }
            set({ user, token, isAuthenticated: true });
        },
        updateUser: (user: User) => {
            if (browser) {
                localStorage.setItem('user', JSON.stringify(user));
            }
            update((state) => ({ ...state, user }));
        },
        logout: () => {
            if (browser) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
            }
            set({ user: null, token: null, isAuthenticated: false });
        },
        checkRole: (role: UserRole): boolean => {
            let currentRole: UserRole | undefined;
            subscribe((state) => {
                currentRole = state.user?.role;
            })();
            return currentRole === role;
        }
    };
}

export const authStore = createAuthStore();
