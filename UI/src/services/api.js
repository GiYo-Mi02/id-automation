/**
 * Authenticated API Handler
 * Automatically includes API key in all requests
 */

const API_KEY = import.meta.env.VITE_API_KEY;

/**
 * Authenticated fetch wrapper
 * @param {string} url - API endpoint (e.g., '/api/students' or full URL)
 * @param {object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<any>} Parsed JSON response
 */
export async function authenticatedFetch(url, options = {}) {
  // Ensure URL is absolute or starts with /
  const apiUrl = url.startsWith('http') ? url : url;

  // Merge headers with API key
  const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': import.meta.env.VITE_API_KEY,
    ...options.headers,
  };

  // Remove Content-Type for FormData
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(apiUrl, config);

    // Handle HTTP errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      throw new Error(errorMessage);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    // Parse and return JSON
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Convenience methods
export const api = {
  get: (url) => authenticatedFetch(url, { method: 'GET' }),
  
  post: (url, data) => authenticatedFetch(url, {
    method: 'POST',
    body: data instanceof FormData ? data : JSON.stringify(data),
  }),
  
  put: (url, data) => authenticatedFetch(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  delete: (url) => authenticatedFetch(url, { method: 'DELETE' }),
};

export default authenticatedFetch;
