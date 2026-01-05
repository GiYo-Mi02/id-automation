/**
 * API Client Utility
 * Automatically injects API key and handles errors
 */

const API_BASE = '/api';
const API_KEY = import.meta.env.VITE_API_KEY || '';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

/**
 * Fetch wrapper that automatically includes API key
 */
async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
      ...options.headers,
    },
  };

  // Remove Content-Type for FormData
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  try {
    const response = await fetch(url, config);

    // Handle non-2xx responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error.message, 0, null);
  }
}

/**
 * Convenience methods
 */
export const api = {
  get: (endpoint, options = {}) =>
    apiFetch(endpoint, { ...options, method: 'GET' }),

  post: (endpoint, data, options = {}) =>
    apiFetch(endpoint, {
      ...options,
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
    }),

  put: (endpoint, data, options = {}) =>
    apiFetch(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (endpoint, options = {}) =>
    apiFetch(endpoint, { ...options, method: 'DELETE' }),

  patch: (endpoint, data, options = {}) =>
    apiFetch(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};

export default api;
