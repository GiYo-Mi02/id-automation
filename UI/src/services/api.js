/**
 * Authenticated API Handler
 * Automatically includes API key in all requests
 * Enhanced with template CRUD, teacher support, and field mapping
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
    console.error('API Error:', error.message || JSON.stringify(error));
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


// =============================================================================
// TEMPLATE API - Database-backed templates with layer system
// =============================================================================

export const templateAPI = {
  /**
   * List all templates with optional filters
   * @param {Object} params - Filter parameters
   * @param {string} params.templateType - 'student' or 'teacher'
   * @param {string} params.schoolLevel - 'elementary', 'high_school', or 'teacher'
   * @param {boolean} params.activeOnly - Only return active templates
   */
  async list(params = {}) {
    const query = new URLSearchParams();
    if (params.templateType) query.set('template_type', params.templateType);
    if (params.schoolLevel) query.set('school_level', params.schoolLevel);
    if (params.activeOnly) query.set('active_only', 'true');
    
    const queryString = query.toString();
    return api.get(`/api/templates/db${queryString ? `?${queryString}` : ''}`);
  },
  
  /**
   * Get a specific template by ID
   */
  async get(id) {
    return api.get(`/api/templates/db/${id}`);
  },
  
  /**
   * Get the active template for a type
   */
  async getActive(templateType, schoolLevel = null) {
    const query = schoolLevel ? `?school_level=${schoolLevel}` : '';
    return api.get(`/api/templates/db/active/${templateType}${query}`);
  },
  
  /**
   * Create a new template
   */
  async create(template) {
    return api.post('/api/templates/db', template);
  },
  
  /**
   * Update an existing template
   */
  async update(id, updates) {
    return api.put(`/api/templates/db/${id}`, updates);
  },
  
  /**
   * Delete a template
   */
  async delete(id) {
    return api.delete(`/api/templates/db/${id}`);
  },
  
  /**
   * Activate a template (sets as active for its type)
   */
  async activate(id) {
    return api.post(`/api/templates/db/${id}/activate`, {});
  },
  
  /**
   * Duplicate a template
   */
  async duplicate(id, newName = null) {
    const query = newName ? `?new_name=${encodeURIComponent(newName)}` : '';
    return api.post(`/api/templates/db/${id}/duplicate${query}`, {});
  },
  
  /**
   * Get available fields for a template type
   */
  async getFields(templateType) {
    return api.get(`/api/templates/db/fields/${templateType}`);
  },
};


// =============================================================================
// TEACHER API
// =============================================================================

export const teacherAPI = {
  /**
   * List all teachers with pagination
   */
  async list(params = {}) {
    const query = new URLSearchParams();
    if (params.page) query.set('page', params.page.toString());
    if (params.pageSize) query.set('page_size', params.pageSize.toString());
    if (params.department) query.set('department', params.department);
    if (params.status) query.set('status', params.status);
    
    const queryString = query.toString();
    return api.get(`/api/teachers${queryString ? `?${queryString}` : ''}`);
  },
  
  /**
   * Search teachers
   */
  async search(query, limit = 10) {
    return api.get(`/api/teachers/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  },
  
  /**
   * Get a specific teacher by employee ID
   */
  async get(employeeId) {
    return api.get(`/api/teachers/${employeeId}`);
  },
  
  /**
   * Create a new teacher
   */
  async create(data) {
    return api.post('/api/teachers', data);
  },
  
  /**
   * Update a teacher
   */
  async update(employeeId, data) {
    return api.put(`/api/teachers/${employeeId}`, data);
  },
  
  /**
   * Delete a teacher
   */
  async delete(employeeId) {
    return api.delete(`/api/teachers/${employeeId}`);
  },
  
  /**
   * Get generation history for a teacher
   */
  async getHistory(employeeId, limit = 20) {
    return api.get(`/api/teachers/${employeeId}/history?limit=${limit}`);
  },
};


// =============================================================================
// STUDENT API EXTENSION
// =============================================================================

export const studentAPI = {
  /**
   * List all students
   */
  async list() {
    return api.get('/api/students');
  },
  
  /**
   * Search students
   */
  async search(query, limit = 10) {
    return api.get(`/api/students/search?q=${encodeURIComponent(query)}`);
  },
  
  /**
   * Get a specific student
   */
  async get(id) {
    const students = await api.get('/api/students');
    return students.find(s => s.id_number === id) || null;
  },
  
  /**
   * Update a student
   */
  async update(id, data) {
    return api.put(`/api/students/${id}`, data);
  },
  
  /**
   * Regenerate ID card for a student
   */
  async regenerate(id) {
    return api.post(`/api/regenerate/${id}`, {});
  },
  
  /**
   * Get generation history
   */
  async getHistory(limit = 50) {
    return api.get(`/api/history?limit=${limit}`);
  },
};


// =============================================================================
// LAYOUT API (Legacy support for JSON-based layouts)
// =============================================================================

export const layoutAPI = {
  async get() {
    return api.get('/api/layout');
  },
  
  async save(layout) {
    return api.post('/api/layout', layout);
  },
};


// =============================================================================
// SETTINGS API
// =============================================================================

export const settingsAPI = {
  async get() {
    return api.get('/api/settings');
  },
  
  async save(settings) {
    return api.post('/api/settings', settings);
  },
};


// =============================================================================
// FILE TEMPLATES API (PNG template files)
// =============================================================================

export const fileTemplatesAPI = {
  async list() {
    return api.get('/api/templates');
  },
  
  async upload(files) {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    return api.post('/api/templates/upload', formData);
  },
  
  async delete(filename) {
    return api.delete(`/api/templates/${filename}`);
  },
};


// =============================================================================
// CAPTURE API
// =============================================================================

export const captureAPI = {
  async upload(file, studentId, manualData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('student_id', studentId);
    
    if (manualData.name) formData.append('manual_name', manualData.name);
    if (manualData.grade) formData.append('manual_grade', manualData.grade);
    if (manualData.section) formData.append('manual_section', manualData.section);
    if (manualData.guardian) formData.append('manual_guardian', manualData.guardian);
    if (manualData.address) formData.append('manual_address', manualData.address);
    if (manualData.contact) formData.append('manual_contact', manualData.contact);
    
    return api.post('/api/capture', formData);
  },
};


// =============================================================================
// SYSTEM API
// =============================================================================

export const systemAPI = {
  async getStats() {
    return api.get('/api/system/stats');
  },
  
  async getHealth() {
    return api.get('/api/v2/system/health');
  },
  
  async exportAnalytics() {
    return api.get('/api/analytics/export');
  },
};


// =============================================================================
// IMPORT API
// =============================================================================

export const importAPI = {
  async preview(file) {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/students/import/preview', formData);
  },
  
  async execute(file) {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/students/import', formData);
  },
};

export default authenticatedFetch;
