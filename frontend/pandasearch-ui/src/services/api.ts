import { SearchResponse, FilterOption, SearchConfig } from '../types/search';

const API_BASE = 'http://localhost:8000/api/v1';

export async function search(params: {
  query: string;
  filters?: Record<string, any>;
  sort_by?: string;
  page?: number;
  page_size?: number;
}): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    throw new Error(`Search failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function suggest(
  q: string,
  limit?: number
): Promise<{
  suggestions: Array<{ type: string; text: string; highlight?: string }>;
}> {
  const query = new URLSearchParams({ q });
  if (limit !== undefined) query.set('limit', String(limit));
  const res = await fetch(`${API_BASE}/suggest?${query.toString()}`);
  if (!res.ok) {
    throw new Error(`Suggest failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getFilters(
  applied?: Record<string, any>
): Promise<{ filters: FilterOption[] }> {
  const query = new URLSearchParams();
  if (applied) {
    query.set('applied', JSON.stringify(applied));
  }
  const res = await fetch(`${API_BASE}/filters?${query.toString()}`);
  if (!res.ok) {
    throw new Error(`Get filters failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getConfig(): Promise<SearchConfig> {
  const res = await fetch(`${API_BASE}/config`);
  if (!res.ok) {
    throw new Error(`Get config failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}
