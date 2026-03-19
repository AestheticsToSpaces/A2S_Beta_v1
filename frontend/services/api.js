import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

// Create axios instance
const api = axios.create({
    baseURL: API_URL,
});

// Add a request interceptor to include JWT
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        // Do not add Authorization header for public routes to avoid 401s on invalid tokens
        const publicRoutes = ['/users/login', '/users/register', '/gallery', '/products'];
        const isPublicRoute = publicRoutes.some(route => config.url && config.url.startsWith(route));

        if (token && !isPublicRoute) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// ============================================
// AUTHENTICATION (Java Backend Auth)
// ============================================

export const login = async (email, password) => {
    try {
        const response = await api.post('/users/login', { email, password });
        const { token, ...user } = response.data;

        // Save token to localStorage
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));

        return user;
    } catch (error) {
        throw error.response?.data?.message || 'Login failed';
    }
};

export const register = async (name, email, password, location = '') => {
    try {
        await api.post('/users/register', { name, email, password, location });
        // After registration, user can login
        return { success: true };
    } catch (error) {
        throw error.response?.data?.message || 'Registration failed';
    }
};

export const logout = async () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
};

// ============================================
// USER PROFILE
// ============================================

export const getUserProfile = async () => {
    try {
        const response = await api.get('/users/profile');
        const profile = response.data;

        return {
            id: profile.id,
            name: profile.name,
            email: profile.email,
            location: profile.location,
            savedDesigns: profile.savedDesigns || [],
            memberSince: profile.memberSince ? new Date(profile.memberSince).toLocaleDateString('en-IN', {
                month: 'short',
                year: 'numeric'
            }) : 'Member',
        };
    } catch (error) {
        throw error.response?.data?.message || 'Failed to fetch profile';
    }
};

export const updateUserProfile = async (updates) => {
    try {
        const response = await api.put('/users/profile', updates);
        return response.data;
    } catch (error) {
        throw error.response?.data?.message || 'Update failed';
    }
};

export const saveDesign = async (designId) => {
    try {
        const response = await api.post('/users/saved-designs', { designId });
        return response.data; // Returns the updated saved designs list
    } catch (error) {
        throw error.response?.data?.message || 'Failed to save design';
    }
};

// ============================================
// DESIGNS
// ============================================

export const getDesigns = async () => {
    try {
        const response = await api.get('/gallery');
        return response.data || [];
    } catch (error) {
        console.error('Error fetching designs:', error);
        throw error;
    }
};

export const getProducts = async () => {
    try {
        const response = await api.get('/products');
        return response.data || [];
    } catch (error) {
        console.error('Error fetching products:', error);
        throw error;
    }
};

export const getDesignById = async (id) => {
    try {
        const response = await api.get(`/gallery/${id}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching design:', error);
        throw error;
    }
};

// ============================================
// CHAT
// ============================================

export const sendChatMessage = async (message, projectContext) => {
    try {
        const response = await api.post('/chat', { message, projectContext });
        return response.data;
    } catch (error) {
        throw error.response?.data?.message || 'Chat failed';
    }
};
