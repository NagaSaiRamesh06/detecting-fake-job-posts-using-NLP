/**
 * JobCheck - Frontend API Service Client
 * Boilerplate for interacting with the backend Flask REST API endpoints.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Core helper for handling stateless HTTP requests and automatic JWT header injection.
 */
async function fetchWithAuth(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.msg || errorData.error || 'API Request failed');
    }

    return response.json();
}

export const api = {
    /**
     * User authentication & registration
     */
    login: async (username, password) => {
        const data = await fetchWithAuth('/api/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
        }
        return data;
    },

    register: (username, password, fullname) => {
        return fetchWithAuth('/api/register', {
            method: 'POST',
            body: JSON.stringify({ username, password, fullname }),
        });
    },

    getProfile: () => {
        return fetchWithAuth('/api/me');
    },

    logout: () => {
        localStorage.removeItem('token');
    },

    /**
     * AI Text prediction
     */
    predictJob: (jobDescription) => {
        return fetchWithAuth('/predict', {
            method: 'POST',
            body: JSON.stringify({ job_description: jobDescription }),
        });
    },

    /**
     * Image OCR Analysis
     * Uses FormData and lets the browser handle multipart boundaries.
     */
    scanJobImage: async (file) => {
        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('file', file);

        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/scan-image`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.msg || errorData.error || 'Image scan failed');
        }

        return response.json();
    },

    /**
     * Dashboard statistics & audit logging
     */
    getUserDashboard: () => {
        return fetchWithAuth('/api/dashboard');
    },

    getAdminDashboard: () => {
        return fetchWithAuth('/api/admin');
    }
};
