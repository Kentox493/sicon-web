import axios from 'axios';

const API_BASE_URL = 'http://192.168.0.5:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await api.post('/api/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        return response.data;
    },

    register: async (username, email, password) => {
        const response = await api.post('/api/auth/register', {
            username,
            email,
            password,
        });
        return response.data;
    },

    getMe: async () => {
        const response = await api.get('/api/auth/me');
        return response.data;
    },
};

// Scans API
export const scansAPI = {
    create: async (target, options) => {
        const response = await api.post('/api/scans/', {
            target,
            options,
        });
        return response.data;
    },

    list: async (skip = 0, limit = 20) => {
        const response = await api.get(`/api/scans/?skip=${skip}&limit=${limit}`);
        return response.data;
    },

    get: async (scanId) => {
        const response = await api.get(`/api/scans/${scanId}`);
        return response.data;
    },

    delete: async (scanId) => {
        await api.delete(`/api/scans/${scanId}`);
    },

    stop: async (scanId) => {
        const response = await api.post(`/api/scans/${scanId}/stop`);
        return response.data;
    },
};

// Reports API
export const reportsAPI = {
    list: async () => {
        const response = await api.get('/api/reports/');
        return response.data;
    },

    generate: async (scanId, useAi = false) => {
        const response = await api.post(`/api/reports/generate/${scanId}?use_ai=${useAi}`);
        return response.data;
    },

    download: async (scanId, useAi = false) => {
        const response = await api.get(`/api/reports/download/${scanId}?use_ai=${useAi}`, {
            responseType: 'blob',
        });
        return response.data;
    },

    delete: async (reportId) => {
        await api.delete(`/api/reports/${reportId}`);
    },
};

// Settings API
export const settingsAPI = {
    get: async () => {
        const response = await api.get('/api/settings/');
        return response.data;
    },

    update: async (data) => {
        const response = await api.put('/api/settings/', data);
        return response.data;
    },

    deleteGeminiKey: async () => {
        const response = await api.delete('/api/settings/gemini-key');
        return response.data;
    },
};

export default api;
