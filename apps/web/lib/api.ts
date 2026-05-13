/**
 * API client for the FastAPI backend.
 *
 * Day 2 will:
 * - Add token storage (httpOnly cookies preferred over localStorage)
 * - Add automatic refresh on 401
 * - Add typed request/response shapes generated from Pydantic schemas
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type ApiOptions = RequestInit & {
  token?: string | null;
};

export async function apiFetch<T = unknown>(
  path: string,
  options: ApiOptions = {},
): Promise<T> {
  const { token, headers, ...rest } = options;

  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  health: () => apiFetch<{ status: string }>('/health'),
  register: (email: string, password: string, full_name?: string) =>
    apiFetch<{ id: string; email: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    }),
  login: (email: string, password: string) =>
    apiFetch<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
};
