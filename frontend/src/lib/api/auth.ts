import apiClient from './client';
import type { APIResponse, LoginRequest, Token } from './types';

export async function login(credentials: LoginRequest): Promise<Token> {
    const response = await apiClient.post<Token>('/api/v1/auth/login', credentials);
    return response.data;
}

export function saveToken(token: string): void {
    if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', token);
    }
}

export function getToken(): string | null {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('access_token');
    }
    return null;
}

export function removeToken(): void {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    }
}

export function isAuthenticated(): boolean {
    return getToken() !== null;
}
