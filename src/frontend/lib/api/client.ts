/**
 * Base API Client Configuration
 * Handles HTTP requests to backend microservices
 */

const API_BASE_URLS = {
  auth: process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8001',
  budget: process.env.NEXT_PUBLIC_BUDGET_API_URL || 'http://localhost:8003',
  ranking: process.env.NEXT_PUBLIC_RANKING_API_URL || 'http://localhost:8002',
  ai: process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8004',
};

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = localStorage.getItem('token');

  const headers = new Headers({
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>
  });

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new APIError(
      error.detail || response.statusText,
      response.status,
      error
    );
  }

  return response;
}

export async function apiGet<T>(
  service: keyof typeof API_BASE_URLS,
  endpoint: string
): Promise<T> {
  const url = `${API_BASE_URLS[service]}${endpoint}`;
  const response = await fetchWithAuth(url);
  return response.json();
}

export async function apiPost<T>(
  service: keyof typeof API_BASE_URLS,
  endpoint: string,
  data?: any
): Promise<T> {
  const url = `${API_BASE_URLS[service]}${endpoint}`;
  const response = await fetchWithAuth(url, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function apiPut<T>(
  service: keyof typeof API_BASE_URLS,
  endpoint: string,
  data?: any
): Promise<T> {
  const url = `${API_BASE_URLS[service]}${endpoint}`;
  const response = await fetchWithAuth(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function apiDelete<T>(
  service: keyof typeof API_BASE_URLS,
  endpoint: string
): Promise<T> {
  const url = `${API_BASE_URLS[service]}${endpoint}`;
  const response = await fetchWithAuth(url, {
    method: 'DELETE',
  });
  return response.json();
}
