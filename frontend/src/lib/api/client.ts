import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { browser } from '$app/environment';

// Use relative URL to leverage Vite proxy in dev and same-origin in prod
const API_BASE_URL = '';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        if (browser) {
            const token = localStorage.getItem('access_token');
            if (token && config.headers) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && browser) {
            // Token expired or invalid, clear storage and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default apiClient;
