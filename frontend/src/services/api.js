const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000/api';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  
  const headers = new Headers();
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const token = localStorage.getItem('token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const config = {
    ...options,
    headers: {
      ...Object.fromEntries(headers.entries()),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }

    if (!response.ok) {
      let errorMessage = '';
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json().catch(() => ({}));
        errorMessage = errorData.message || errorData.error || '';
      } else {
        errorMessage = await response.text().catch(() => '');
      }
      throw new Error(errorMessage || `Request failed with status ${response.status}`);
    }

    // Standard JSON parse or fallback for empty response bodies
    return await response.json().catch(() => ({}));
  } catch (error) {
    console.error('API Error:', error.message);
    throw error;
  }
}

export const api = {
  get: (endpoint, options) => request(endpoint, { ...options, method: 'GET' }),
  post: (endpoint, body, options) => request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) }),
  upload: (endpoint, formData, options) => request(endpoint, { ...options, method: 'POST', body: formData }),
  put: (endpoint, body, options) => request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint, options) => request(endpoint, { ...options, method: 'DELETE' }),
};
